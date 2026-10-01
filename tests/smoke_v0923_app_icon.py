from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "static" / "assets" / "app" / "agent-city.ico"
EXPECTED_SIZES = [16, 24, 32, 48, 64, 128, 256]
EXPECTED_SHA256 = "0a516c3efb859a69ed62485f31876a23052c873b959a60353970c3f82f948eab"


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def png_alpha_extremes(data: bytes) -> tuple[int, int, int, int]:
    assert data.startswith(b"\x89PNG\r\n\x1a\n")

    pos = 8
    width = height = color_type = bit_depth = None
    idat = bytearray()

    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length

        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            break

    assert width and height
    assert bit_depth == 8
    assert color_type == 6  # RGBA

    raw = zlib.decompress(bytes(idat))
    bpp = 4
    stride = width * bpp
    rows: list[bytearray] = []
    offset = 0

    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        scan = bytearray(raw[offset:offset + stride])
        offset += stride
        prev = rows[-1] if rows else bytearray(stride)

        for i in range(stride):
            left = scan[i - bpp] if i >= bpp else 0
            up = prev[i]
            up_left = prev[i - bpp] if i >= bpp else 0

            if filter_type == 1:
                scan[i] = (scan[i] + left) & 0xFF
            elif filter_type == 2:
                scan[i] = (scan[i] + up) & 0xFF
            elif filter_type == 3:
                scan[i] = (scan[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                scan[i] = (scan[i] + paeth(left, up, up_left)) & 0xFF
            else:
                assert filter_type == 0

        rows.append(scan)

    alphas = [row[i] for row in rows for i in range(3, stride, 4)]
    return width, height, min(alphas), max(alphas)


def main() -> None:
    data = ICON.read_bytes()
    assert len(data) == 31650
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256

    reserved, icon_type, count = struct.unpack("<HHH", data[:6])
    assert reserved == 0
    assert icon_type == 1
    assert count == len(EXPECTED_SIZES)

    seen: list[int] = []
    for index in range(count):
        start = 6 + (16 * index)
        width_byte, height_byte, colors, reserved_byte, planes, bits, size, offset = struct.unpack(
            "<BBBBHHII", data[start:start + 16]
        )

        width = 256 if width_byte == 0 else width_byte
        height = 256 if height_byte == 0 else height_byte

        assert width == height
        assert colors == 0
        assert reserved_byte == 0
        assert planes == 1
        assert bits == 32
        assert offset + size <= len(data)

        frame = data[offset:offset + size]
        png_width, png_height, min_alpha, max_alpha = png_alpha_extremes(frame)

        assert png_width == width
        assert png_height == height
        assert min_alpha == 0
        assert max_alpha == 255
        seen.append(width)

    assert sorted(seen) == EXPECTED_SIZES

    tray = (ROOT / "agent_city_tray.ps1").read_text(encoding="utf-8")
    shortcut = (ROOT / "install_desktop_shortcut.ps1").read_text(encoding="utf-8")
    assert 'static\\assets\\app\\agent-city.ico' in tray
    assert 'static\\assets\\app\\agent-city.ico' in shortcut

    print("v0.9.23 Agent City application icon smoke passed.")


if __name__ == "__main__":
    main()
