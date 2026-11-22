"""Seekable concatenated archive parts without extraction or source writes."""

import io
from bisect import bisect_right
from pathlib import Path
from typing import BinaryIO


class JoinedParts(io.RawIOBase):
    """Expose contiguous .part00… files as a seekable ZIP byte stream.

    This supports byte-split ZIP downloads, not PKZIP multi-disk archives.
    Missing interior parts fail before opening any archive members.
    """

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self.paths = paths
        self.offsets = [0]
        for path in paths:
            self.offsets.append(self.offsets[-1] + path.stat().st_size)
        self.position = 0
        self.handle: BinaryIO | None = None
        self.part = -1

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        position = offset + (
            self.position if whence == 1 else self.offsets[-1] if whence == 2 else 0
        )
        if position < 0:
            raise ValueError("negative seek")
        self.position = position
        return position

    def read(self, size: int = -1) -> bytes:
        remaining = self.offsets[-1] - self.position
        size = remaining if size < 0 else min(size, remaining)
        chunks = []
        while size > 0:
            part = bisect_right(self.offsets, self.position) - 1
            if part != self.part:
                if self.handle:
                    self.handle.close()
                self.handle = self.paths[part].open("rb")
                self.part = part
            assert self.handle is not None
            self.handle.seek(self.position - self.offsets[part])
            chunk = self.handle.read(min(size, self.offsets[part + 1] - self.position))
            if not chunk:
                raise OSError("archive part truncated")
            chunks.append(chunk)
            self.position += len(chunk)
            size -= len(chunk)
        return b"".join(chunks)

    def close(self) -> None:
        if self.handle:
            self.handle.close()
        super().close()
