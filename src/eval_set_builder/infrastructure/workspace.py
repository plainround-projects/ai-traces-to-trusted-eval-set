"""A directory as a workspace: named text files under one root, with no way out of it."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath


class DirectoryWorkspace:
    """Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _path(self, name: str) -> Path:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"workspace names must be relative and stay inside the root: {name!r}")
        return self._root.joinpath(*pure.parts)

    def exists(self, name: str) -> bool:
        """True when the file is there."""
        return self._path(name).is_file()

    def read_text(self, name: str) -> str:
        """The file's text."""
        return self._path(name).read_text(encoding="utf-8")

    def write_text(self, name: str, text: str) -> None:
        """Replace the file, creating folders as needed."""
        path = self._path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def digest(self, name: str) -> str:
        """SHA-256 of the file's bytes, in hex."""
        return hashlib.sha256(self._path(name).read_bytes()).hexdigest()

    def list_names(self, prefix: str) -> list[str]:
        """The file names that start with `prefix`, sorted."""
        found = (path.relative_to(self._root).as_posix() for path in self._root.rglob("*") if path.is_file())
        return sorted(name for name in found if name.startswith(prefix))
