"""Runtime validation for reports crossing adapter/provider boundaries."""
import re
from pathlib import Path

from .core import SCHEMA, MigrationError, digest, json_bytes, safe_child


def require(condition, message):
    if not condition:
        raise MigrationError(message)


def hash_value(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_file_map(files):
    require(isinstance(files, dict) and bool(files), "File map must be a non-empty object")
    seen = set()
    for name, checksum in files.items():
        require(isinstance(name, str), "File path must be a string")
        safe_child(Path.cwd(), name)
        require(name.casefold() not in seen, "Case-colliding file paths")
        seen.add(name.casefold())
        require(hash_value(checksum), f"Invalid checksum: {name}")


def validate_generation(value):
    require(isinstance(value, dict) and value.get("schema_version") == SCHEMA, "Unsupported generation contract")
    require(hash_value(value.get("source_sha256")), "Invalid source checksum")
    validate_file_map(value.get("files"))
    require(isinstance(value.get("generated_pages"), list), "Missing generated pages")
    require(bool(value['generated_pages']) or value.get('status') == 'scaffold_created', 'Empty generated pages require explicit scaffold status')
    for page in value["generated_pages"]:
        require(isinstance(page, dict) and page.get("target") in value["files"], "Generated page not in file map")


def validate_facts(value):
    require(isinstance(value, dict) and value.get("schema_version") == SCHEMA, "Unsupported facts contract")
    require(value.get("source_platform") == "ios", "This adapter expects iOS source facts")
    source = value.get("source_snapshot")
    require(isinstance(source, dict) and isinstance(source.get("files"), list), "Missing source snapshot")
    require(hash_value(source.get("sha256")), "Invalid source snapshot checksum")
    files = {}
    for item in source["files"]:
        require(isinstance(item, dict) and isinstance(item.get("path"), str), "Invalid source file entry")
        require(item["path"] not in files, "Duplicate source file entry")
        files[item["path"]] = item.get("sha256")
    validate_file_map(files)
    require(digest(json_bytes(source["files"])) == source["sha256"], "Source snapshot manifest was modified")
    require(isinstance(value.get("facts"), list), "Missing facts")
    seen = set()
    for fact in value["facts"]:
        require(isinstance(fact, dict) and isinstance(fact.get("id"), str), "Invalid fact")
        require(fact["id"] not in seen, "Duplicate fact ID")
        seen.add(fact["id"])
        require(fact.get("evidence") in {"structured_static", "lexical_hint", "restricted_parser"}, "Invalid static evidence class")
        refs = fact.get("source_anchors_ref")
        require(isinstance(refs, list) and bool(refs), "Missing source anchors")
        for ref in refs:
            require(isinstance(ref, dict) and ref.get("path") in files, "Anchor file absent from snapshot")
            require(ref.get("sha256") == files[ref["path"]], "Anchor has stale checksum")
            require(type(ref.get("line")) is int and ref["line"] >= 1, "Anchor line must be a positive integer")
    return value
