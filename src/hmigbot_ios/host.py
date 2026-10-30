"""Read-only host and provider capability negotiation.

Migration stages consume this profile instead of branching on the operating
system. Discovery never runs a build, connects to a device, or mutates a
project. Runtime and device capabilities remain unverified until a provider
records real evidence.
"""
from __future__ import annotations

import os
import platform as _platform
import shutil
import sys
from typing import Callable, Mapping

SCHEMA_VERSION = 1
AVAILABLE = "available"
PARTIAL = "partial"
UNAVAILABLE = "unavailable"
UNVERIFIED = "unverified"
RELEASE_PROFILE = "macos-arm64"


def normalize_host_os(value: str | None) -> str:
    value = (value or "").strip().lower()
    if value in {"darwin", "macos", "mac", "osx"}:
        return "macos"
    if value in {"windows", "win32", "win"}:
        return "windows"
    if value in {"linux", "linux2"}:
        return "linux"
    return value or "unknown"


def supported_host(*, host_os=None, machine=None):
    return (normalize_host_os(host_os or _platform.system()) == 'macos' and
            (machine or _platform.machine()).lower() in {'arm64', 'aarch64'})


def require_supported_host(*, host_os=None, machine=None):
    """Fail before runtime execution or managed writes on deferred platforms."""
    if not supported_host(host_os=host_os, machine=machine):
        from .core import MigrationError
        raise MigrationError('Unsupported host for release ' + RELEASE_PROFILE +
                             '; use macOS Apple Silicon. Intel Mac, Windows and Linux support is deferred; '
                             'see PLATFORM-ROADMAP.md')
    return RELEASE_PROFILE


def _tool(name: str, *, aliases: tuple[str, ...] = (), lookup: Callable[[str], str | None] | None = None) -> dict:
    lookup = lookup or shutil.which
    for candidate in (name,) + aliases:
        path = lookup(candidate)
        if path:
            return {"status": AVAILABLE, "command": candidate, "path": path}
    return {"status": UNAVAILABLE, "command": name, "path": None}


def detect_host_profile(*, host_os: str | None = None, machine: str | None = None,
                        lookup: Callable[[str], str | None] | None = None,
                        environ: Mapping[str, str] | None = None) -> dict:
    """Detect the host and select source/target providers without mutation."""
    env = dict(os.environ if environ is None else environ)
    os_name = normalize_host_os(host_os or _platform.system())
    architecture = machine or _platform.machine()
    supported = supported_host(host_os=os_name, machine=architecture)
    xcodebuild = _tool("xcodebuild", lookup=lookup)
    xcrun = _tool("xcrun", lookup=lookup)
    swift = _tool("swift", lookup=lookup)
    native_xcode = supported and xcodebuild["status"] == AVAILABLE and xcrun["status"] == AVAILABLE

    if native_xcode:
        source_provider, source_mode = "macos_xcode", "native"
        membership, compiler, ios_build, ios_runtime = AVAILABLE, AVAILABLE, AVAILABLE, UNVERIFIED
    elif supported:
        source_provider, source_mode = "macos_static_fallback", "static_fallback"
        membership, compiler, ios_build, ios_runtime = PARTIAL, UNAVAILABLE, UNAVAILABLE, UNAVAILABLE
    else:
        source_provider, source_mode = "unavailable", "unsupported_host"
        membership, compiler, ios_build, ios_runtime = UNAVAILABLE, UNAVAILABLE, UNAVAILABLE, UNAVAILABLE

    hvigor = _tool("hvigorw", lookup=lookup)
    node = _tool("node", lookup=lookup)
    ohpm = _tool("ohpm", lookup=lookup)
    hdc = _tool("hdc", lookup=lookup)
    harmony_build = AVAILABLE if supported and hvigor["status"] == AVAILABLE and node["status"] == AVAILABLE else UNAVAILABLE
    cloud_allowed = supported and env.get("HMIGBOT_ALLOW_CLOUD_PROVIDER", "1").lower() not in {"0", "false", "no"}

    return {
        "schema_version": SCHEMA_VERSION,
        "host": {"os": os_name, "arch": architecture, "python": sys.version.split()[0],
                 "release_profile": RELEASE_PROFILE, "supported": supported,
                 "status": "supported" if supported else "unsupported"},
        "source": {"platform": "ios", "provider": source_provider, "mode": source_mode,
                   "status": "discovered" if supported else "deferred"},
        "target": {"platform": "harmonyos", "provider": "local_harmony" if supported else "unavailable",
                   "mode": "local" if supported else "unsupported_host"},
        "tools": {"xcodebuild": xcodebuild, "xcrun": xcrun, "swift": swift,
                  "hvigorw": hvigor, "node": node, "ohpm": ohpm, "hdc": hdc},
        "capabilities": {
            "ios.static_analysis": AVAILABLE if supported else UNAVAILABLE,
            "ios.xcode_project_membership": membership,
            "ios.swift_compiler_context": compiler,
            "ios.build": ios_build,
            "ios.runtime": ios_runtime,
            "harmony.build": harmony_build,
            "harmony.runtime": UNVERIFIED if supported else UNAVAILABLE,
            "harmony.device": UNVERIFIED if supported and hdc["status"] == AVAILABLE else UNAVAILABLE,
            "cloud.macos_build": UNVERIFIED if cloud_allowed else UNAVAILABLE,
        },
        "selection": {
            "source_reason": ("macOS with xcodebuild and xcrun" if native_xcode else
                              "Host deferred by macos-arm64 release profile" if not supported else
                              "Apple tools unavailable; static fallback"),
            "cloud_provider_allowed": cloud_allowed,
            "evidence_policy": "availability is discovery only; execution requires provider evidence",
            "platform_roadmap": "PLATFORM-ROADMAP.md",
        },
    }


def provider_for(profile: Mapping, capability: str) -> str:
    source = profile.get("source") if isinstance(profile, Mapping) else None
    target = profile.get("target") if isinstance(profile, Mapping) else None
    host = profile.get('host') if isinstance(profile, Mapping) else None
    if isinstance(host, Mapping) and host.get('supported') is False:
        return 'unavailable'
    if capability.startswith("ios."):
        return str(source.get("provider")) if isinstance(source, Mapping) else "unavailable"
    if capability.startswith("harmony."):
        return str(target.get("provider")) if isinstance(target, Mapping) else "unavailable"
    if capability.startswith("cloud."):
        return "cloud_macos"
    return "unavailable"


def validate_profile(profile: Mapping) -> None:
    if not isinstance(profile, Mapping) or profile.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported host profile schema")
    for section in ("host", "source", "target", "capabilities", "selection"):
        if not isinstance(profile.get(section), Mapping):
            raise ValueError("Host profile missing " + section)
    if profile["source"].get("platform") != "ios":
        raise ValueError("Host profile source platform must be ios")
    if profile["target"].get("platform") != "harmonyos":
        raise ValueError("Host profile target platform must be harmonyos")
    allowed = {AVAILABLE, PARTIAL, UNAVAILABLE, UNVERIFIED}
    if any(value not in allowed for value in profile["capabilities"].values()):
        raise ValueError("Invalid host capability status")
