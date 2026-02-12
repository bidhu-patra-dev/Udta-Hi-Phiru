"""Local package providing an `imghdr` module for environments missing
the stdlib module (eg. Python 3.13+ minimal runtimes).
"""
from typing import Optional


def _read_header(file) -> bytes:
    if isinstance(file, (bytes, bytearray)):
        return bytes(file[:64])
    try:
        if hasattr(file, "read"):
            pos = None
            try:
                pos = file.tell()
            except Exception:
                pos = None
            header = file.read(64)
            if pos is not None:
                try:
                    file.seek(pos)
                except Exception:
                    pass
            return header
        with open(file, "rb") as f:
            return f.read(64)
    except Exception:
        return b""


def what(file, h: Optional[bytes] = None) -> Optional[str]:
    header = h if h is not None else _read_header(file)
    if not header:
        return None
    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        return "tiff"
    if header.startswith(b"BM"):
        return "bmp"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "webp"
    if header.startswith(b"\x00\x00\x01\x00"):
        return "ico"
    return None
