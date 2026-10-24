"""Own a suspended Windows scheduler process and all of its descendants."""
from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
import subprocess


def run(command, *, cwd, env, timeout):
    """Resume only after job assignment; timeout always terminates the whole job."""
    if os.name != 'nt':
        return subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=timeout, shell=False)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)

    class BasicLimits(ctypes.Structure):
        _fields_ = [('ProcessTime', ctypes.c_int64), ('JobTime', ctypes.c_int64),
                    ('LimitFlags', wintypes.DWORD), ('MinWorkingSet', ctypes.c_size_t),
                    ('MaxWorkingSet', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                    ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD),
                    ('SchedulingClass', wintypes.DWORD)]

    class IOCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ('ReadOps', 'WriteOps', 'OtherOps', 'ReadBytes', 'WriteBytes', 'OtherBytes')]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [('Basic', BasicLimits), ('IO', IOCounters), ('ProcessMemory', ctypes.c_size_t),
                    ('JobMemory', ctypes.c_size_t), ('PeakProcess', ctypes.c_size_t),
                    ('PeakJob', ctypes.c_size_t)]

    class ThreadEntry(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD),
                    ('th32ThreadID', wintypes.DWORD), ('th32OwnerProcessID', wintypes.DWORD),
                    ('tpBasePri', wintypes.LONG), ('tpDeltaPri', wintypes.LONG),
                    ('dwFlags', wintypes.DWORD)]

    signatures = {
        'CreateJobObjectW': ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        'SetInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
        'AssignProcessToJobObject': ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        'TerminateJobObject': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL),
        'CreateToolhelp32Snapshot': ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
        'Thread32First': ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        'Thread32Next': ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
        'OpenThread': ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        'ResumeThread': ([wintypes.HANDLE], wintypes.DWORD),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result

    def require(value):
        if not value:
            raise ctypes.WinError(ctypes.get_last_error())
        return value

    job = require(kernel.CreateJobObjectW(None, None))
    process = None
    try:
        limits = ExtendedLimits()
        limits.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        require(kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=False, creationflags=0x00000004)
        require(kernel.AssignProcessToJobObject(job, wintypes.HANDLE(int(process._handle))))
        threads = kernel.CreateToolhelp32Snapshot(0x00000004, 0)  # TH32CS_SNAPTHREAD
        if threads == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            entry = ThreadEntry()
            entry.dwSize = ctypes.sizeof(entry)
            found = kernel.Thread32First(threads, ctypes.byref(entry))
            resumed = False
            while found:
                if entry.th32OwnerProcessID == process.pid:
                    thread = require(kernel.OpenThread(0x0002, False, entry.th32ThreadID))
                    try:
                        if kernel.ResumeThread(thread) == 0xFFFFFFFF:
                            raise ctypes.WinError(ctypes.get_last_error())
                        resumed = True
                    finally:
                        kernel.CloseHandle(thread)
                found = kernel.Thread32Next(threads, ctypes.byref(entry))
            if not resumed:
                raise OSError('Could not resume the owned scheduler process')
        finally:
            kernel.CloseHandle(threads)
        try:
            output, errors = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            require(kernel.TerminateJobObject(job, 1))
            output, errors = process.communicate(timeout=5)
            exc.output, exc.stderr = output, errors
            exc.ios_process_tree = {'root_pid': process.pid, 'job_terminated': True,
                                    'suspended_until_job_assignment': True}
            raise
        return subprocess.CompletedProcess(command, process.returncode, output, errors)
    finally:
        # Closing the job also handles cancellation, setup errors, or a parent
        # exiting before its helper. No unrelated process is ever enumerated/killed.
        kernel.CloseHandle(job)
        if process is not None:
            if process.poll() is None:
                process.kill()  # Setup may have failed before job assignment.
            process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            process._handle.Close()
