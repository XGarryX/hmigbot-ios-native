"""
Minimal Java .class file constant pool parser.
No external dependencies — reads the binary format directly.

Spec: https://docs.oracle.com/javase/specs/jvms/se17/html/jvms-4.html
"""

import struct
from pathlib import Path
from dataclasses import dataclass, field

# Constant pool tags
CP_UTF8 = 1
CP_INT = 3
CP_FLOAT = 4
CP_LONG = 5
CP_DOUBLE = 6
CP_CLASS = 7
CP_STRING = 8
CP_FIELDREF = 9
CP_METHODREF = 10
CP_INTERFACE_METHODREF = 11
CP_NAME_AND_TYPE = 12
CP_METHOD_HANDLE = 15
CP_METHOD_TYPE = 16
CP_INVOKE_DYNAMIC = 18


@dataclass
class ConstantPool:
    entries: dict = field(default_factory=dict)
    raw: list = field(default_factory=list)

    def get_utf8(self, index: int) -> str:
        e = self.entries.get(index)
        if e and e[0] == CP_UTF8:
            return e[1]
        return ""

    def get_class_name(self, index: int) -> str:
        e = self.entries.get(index)
        if e and e[0] == CP_CLASS:
            return self.get_utf8(e[1]).replace("/", ".")
        return ""

    def get_name_and_type(self, index: int) -> tuple:
        e = self.entries.get(index)
        if e and e[0] == CP_NAME_AND_TYPE:
            return self.get_utf8(e[1]), self.get_utf8(e[2])
        return "", ""

    def get_methodref(self, index: int) -> dict:
        e = self.entries.get(index)
        if e and e[0] in (CP_METHODREF, CP_INTERFACE_METHODREF):
            cls = self.get_class_name(e[1])
            name, desc = self.get_name_and_type(e[2])
            return {"class": cls, "name": name, "descriptor": desc}
        return {}

    def get_fieldref(self, index: int) -> dict:
        e = self.entries.get(index)
        if e and e[0] == CP_FIELDREF:
            cls = self.get_class_name(e[1])
            name, desc = self.get_name_and_type(e[2])
            return {"class": cls, "name": name, "descriptor": desc}
        return {}


def _read_u1(data: bytes, offset: int) -> tuple:
    return struct.unpack_from(">B", data, offset)[0], offset + 1

def _read_u2(data: bytes, offset: int) -> tuple:
    return struct.unpack_from(">H", data, offset)[0], offset + 2

def _read_u4(data: bytes, offset: int) -> tuple:
    return struct.unpack_from(">I", data, offset)[0], offset + 4


def parse_class(filepath: str | Path) -> dict:
    """Parse a .class file, return constant pool + method bytecode analysis."""
    data = Path(filepath).read_bytes()
    off = 0

    magic, off = _read_u4(data, off)
    assert magic == 0xCAFEBABE, f"Not a class file: {filepath}"

    minor, off = _read_u2(data, off)
    major, off = _read_u2(data, off)

    cp_count, off = _read_u2(data, off)
    pool = ConstantPool()
    i = 1
    while i < cp_count:
        tag, off = _read_u1(data, off)
        if tag == CP_UTF8:
            length, off = _read_u2(data, off)
            val = data[off:off+length].decode("utf-8", errors="replace")
            off += length
            pool.entries[i] = (tag, val)
        elif tag == CP_INT:
            val, off = struct.unpack_from(">i", data, off)[0], off + 4
            pool.entries[i] = (tag, val)
        elif tag == CP_FLOAT:
            off += 4
            pool.entries[i] = (tag, None)
        elif tag in (CP_LONG, CP_DOUBLE):
            off += 8
            pool.entries[i] = (tag, None)
            i += 1  # takes 2 slots
        elif tag == CP_CLASS:
            idx, off = _read_u2(data, off)
            pool.entries[i] = (tag, idx)
        elif tag == CP_STRING:
            idx, off = _read_u2(data, off)
            pool.entries[i] = (tag, idx)
        elif tag in (CP_FIELDREF, CP_METHODREF, CP_INTERFACE_METHODREF):
            cls_idx, off = _read_u2(data, off)
            nat_idx, off = _read_u2(data, off)
            pool.entries[i] = (tag, cls_idx, nat_idx)
        elif tag == CP_NAME_AND_TYPE:
            n_idx, off = _read_u2(data, off)
            d_idx, off = _read_u2(data, off)
            pool.entries[i] = (tag, n_idx, d_idx)
        elif tag == CP_METHOD_HANDLE:
            off += 3
            pool.entries[i] = (tag, None)
        elif tag == CP_METHOD_TYPE:
            off += 2
            pool.entries[i] = (tag, None)
        elif tag == CP_INVOKE_DYNAMIC:
            off += 4
            pool.entries[i] = (tag, None)
        else:
            break
        i += 1

    access_flags, off = _read_u2(data, off)
    this_class, off = _read_u2(data, off)
    super_class, off = _read_u2(data, off)

    iface_count, off = _read_u2(data, off)
    off += iface_count * 2

    # Fields
    field_count, off = _read_u2(data, off)
    for _ in range(field_count):
        fa, off = _read_u2(data, off)
        fn, off = _read_u2(data, off)
        fd, off = _read_u2(data, off)
        attr_count, off = _read_u2(data, off)
        for _ in range(attr_count):
            an, off = _read_u2(data, off)
            al, off = _read_u4(data, off)
            off += al

    # Methods — extract bytecode
    methods = []
    method_count, off = _read_u2(data, off)
    for _ in range(method_count):
        ma, off = _read_u2(data, off)
        mn_idx, off = _read_u2(data, off)
        md_idx, off = _read_u2(data, off)
        m_name = pool.get_utf8(mn_idx)
        m_desc = pool.get_utf8(md_idx)

        code_bytes = None
        attr_count, off = _read_u2(data, off)
        for _ in range(attr_count):
            an_idx, off = _read_u2(data, off)
            al, off = _read_u4(data, off)
            attr_end = off + al
            attr_name = pool.get_utf8(an_idx)
            if attr_name == "Code":
                max_stack, off = _read_u2(data, off)
                max_locals, off = _read_u2(data, off)
                code_len, off = _read_u4(data, off)
                code_bytes = data[off:off+code_len]
            off = attr_end

        methods.append({
            "name": m_name,
            "descriptor": m_desc,
            "code": code_bytes,
        })

    this_name = pool.get_class_name(this_class)

    return {
        "class": this_name,
        "super": pool.get_class_name(super_class) if super_class else "",
        "pool": pool,
        "methods": methods,
    }


def extract_invocations(pool: ConstantPool, code: bytes) -> list[dict]:
    """Walk bytecode and extract all invoke* / new / field instructions.
    Returns list of references found in the constant pool.
    On any parsing error, returns what was collected so far.
    """
    if not code:
        return []

    result = []
    off = 0
    code_len = len(code)

    # Opcode lengths for deterministic-width instructions
    OPCODE_SIZE = {
        0x00: 1, 0x01: 1, 0x02: 1, 0x03: 1, 0x04: 1,
        0x05: 1, 0x06: 1, 0x07: 1, 0x08: 1, 0x09: 1,
        0x0A: 1, 0x0B: 1, 0x0C: 1, 0x0D: 1, 0x0E: 1,
        0x0F: 2, 0x10: 2, 0x11: 3, 0x12: 2, 0x13: 3,
        0x14: 3, 0x15: 2, 0x16: 2, 0x17: 2, 0x18: 2,
        0x19: 2, 0x1A: 1, 0x1B: 1, 0x1C: 1, 0x1D: 1,
        0x1E: 1, 0x1F: 1, 0x20: 1, 0x21: 1, 0x22: 1,
        0x23: 1, 0x24: 1, 0x25: 1, 0x26: 1, 0x27: 1,
        0x28: 1, 0x29: 1, 0x2A: 1, 0x2B: 1, 0x2C: 1,
        0x2D: 1, 0x2E: 1, 0x2F: 1, 0x30: 1, 0x31: 1,
        0x32: 1, 0x33: 1, 0x34: 1, 0x35: 1, 0x36: 2,
        0x37: 2, 0x38: 2, 0x39: 2, 0x3A: 2, 0x3B: 2,
        0x3C: 2, 0x3D: 2, 0x3E: 2, 0x3F: 2, 0x40: 2,
        0x41: 2, 0x42: 2, 0x43: 2, 0x44: 2, 0x45: 2,
        0x46: 2, 0x47: 2, 0x48: 2, 0x49: 2, 0x4A: 2,
        0x4B: 2, 0x4C: 2, 0x4D: 2, 0x4E: 2, 0x4F: 2,
        0x50: 2, 0x51: 2, 0x52: 2, 0x53: 2, 0x54: 2,
        0x55: 2, 0x56: 2, 0x57: 1, 0x58: 1, 0x59: 1,
        0x5A: 1, 0x5B: 1, 0x5C: 1, 0x5D: 1, 0x5E: 1,
        0x5F: 1, 0x60: 1, 0x61: 1, 0x62: 1, 0x63: 1,
        0x64: 1, 0x65: 1, 0x66: 1, 0x67: 1, 0x68: 1,
        0x69: 1, 0x6A: 1, 0x6B: 1, 0x6C: 1, 0x6D: 1,
        0x6E: 1, 0x6F: 1, 0x70: 1, 0x71: 1, 0x72: 1,
        0x73: 1, 0x74: 1, 0x75: 1, 0x76: 1, 0x77: 1,
        0x78: 1, 0x79: 1, 0x7A: 1, 0x7B: 1, 0x7C: 1,
        0x7D: 1, 0x7E: 1, 0x7F: 1, 0x80: 1, 0x81: 1,
        0x82: 1, 0x83: 1, 0x84: 3, 0x85: 1, 0x86: 1,
        0x87: 1, 0x88: 1, 0x89: 1, 0x8A: 1, 0x8B: 1,
        0x8C: 1, 0x8D: 1, 0x8E: 1, 0x8F: 1, 0x90: 1,
        0x91: 1, 0x92: 1, 0x93: 1, 0x94: 1, 0x95: 1,
        0x96: 1, 0x97: 1, 0x98: 1, 0x99: 3, 0x9A: 3,
        0x9B: 3, 0x9C: 3, 0x9D: 3, 0x9E: 3, 0x9F: 3,
        0xA0: 3, 0xA1: 3, 0xA2: 3, 0xA3: 3, 0xA4: 3,
        0xA5: 3, 0xA6: 3, 0xA7: 3, 0xA8: 3, 0xA9: 3,
        0xAC: 1, 0xAD: 2, 0xAE: 2, 0xAF: 1, 0xB0: 1,
        0xB1: 1, 0xB2: 3, 0xB3: 3, 0xB4: 3, 0xB5: 3,
        0xB6: 3, 0xB7: 3, 0xB8: 3, 0xB9: 5, 0xBA: 5,
        0xBB: 3, 0xBC: 2, 0xBD: 3, 0xBE: 1, 0xBF: 1,
        0xC0: 3, 0xC1: 3, 0xC2: 1, 0xC3: 1, 0xC6: 3,
        0xC7: 3, 0xC8: 3, 0xC9: 3,
    }

    try:
        while off < code_len:
            opcode = code[off]

            if opcode in (0xB6, 0xB7, 0xB8):  # invokevirtual/special/static
                if off + 2 < code_len:
                    idx = (code[off+1] << 8) | code[off+2]
                    ref = pool.get_methodref(idx)
                    if ref:
                        ref["opcode"] = hex(opcode)
                        result.append(ref)
                off += 3
            elif opcode == 0xB9:  # invokeinterface
                if off + 2 < code_len:
                    idx = (code[off+1] << 8) | code[off+2]
                    ref = pool.get_methodref(idx)
                    if ref:
                        ref["opcode"] = hex(opcode)
                        result.append(ref)
                off += 5
            elif opcode == 0xBB:  # new
                if off + 2 < code_len:
                    idx = (code[off+1] << 8) | code[off+2]
                    cls = pool.get_class_name(idx)
                    result.append({"opcode": "new", "class": cls, "name": "", "descriptor": ""})
                off += 3
            elif opcode in (0x12, 0x13):  # ldc / ldc_w
                if opcode == 0x12:
                    idx = code[off+1] if off + 1 < code_len else 0
                    off += 2
                else:
                    idx = (code[off+1] << 8) | code[off+2] if off + 2 < code_len else 0
                    off += 3
                if idx:
                    entry = pool.entries.get(idx)
                    if entry and entry[0] == CP_CLASS:
                        cls_name = pool.get_class_name(idx)
                        result.append({"opcode": "ldc_class", "class": cls_name, "name": "", "descriptor": ""})
            elif opcode == 0xB4:  # getfield
                if off + 2 < code_len:
                    idx = (code[off+1] << 8) | code[off+2]
                    ref = pool.get_fieldref(idx)
                    if ref:
                        ref["opcode"] = "getfield"
                        result.append(ref)
                off += 3
            elif opcode == 0xB5:  # putfield
                if off + 2 < code_len:
                    idx = (code[off+1] << 8) | code[off+2]
                    ref = pool.get_fieldref(idx)
                    if ref:
                        ref["opcode"] = "putfield"
                        result.append(ref)
                off += 3
            elif opcode == 0xAB:  # lookupswitch
                pad = (4 - ((off + 1) % 4)) % 4
                base = off + 1 + pad
                if base + 8 <= code_len:
                    npairs = struct.unpack_from(">i", code, base + 4)[0]
                    off = base + 8 + npairs * 8
                else:
                    break
            elif opcode == 0xAA:  # tableswitch
                pad = (4 - ((off + 1) % 4)) % 4
                base = off + 1 + pad
                if base + 12 <= code_len:
                    low = struct.unpack_from(">i", code, base + 4)[0]
                    high = struct.unpack_from(">i", code, base + 8)[0]
                    off = base + 12 + (high - low + 1) * 4
                else:
                    break
            elif opcode == 0xC5:  # multianewarray
                off += 4
            elif opcode == 0xC4:  # wide
                off += 4
            elif opcode in OPCODE_SIZE:
                off += OPCODE_SIZE[opcode]
            else:
                off += 1  # unknown — skip
    except (IndexError, struct.error):
        pass

    return result
