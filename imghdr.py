"""Lightweight replacement for stdlib ``imghdr`` to satisfy environments
where the module is unavailable (e.g. newer Python removals).

This implements a minimal ``what(file, h=None)`` used by Streamlit to
detect common image file types by magic bytes.
"""
from typing import Optional


def _read_header(file) -> bytes:
    # file may be a filename, a file-like object, or bytes
    if isinstance(file, (bytes, bytearray)):
        return bytes(file[:64])
    try:
        # file-like object
        pos = None
        if hasattr(file, "read"):
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
        # filename
        with open(file, "rb") as f:
            return f.read(64)
    except Exception:
        return b""


def what(file, h: Optional[bytes] = None) -> Optional[str]:
    """Return the image type (e.g. 'jpeg', 'png') or None if unknown."""
    header = h if h is not None else _read_header(file)
    if not header:
        return None

    # JPEG
    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"

    # PNG
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    # GIF
    if header[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"

    # TIFF
    if header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        return "tiff"

    # BMP
    if header.startswith(b"BM"):
        return "bmp"

    # WEBP (RIFF .....WEBP)
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "webp"

    # ICO
    if header.startswith(b"\x00\x00\x01\x00"):
        return "ico"

    return None
