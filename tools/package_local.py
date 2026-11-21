"""Assemble and check the portable local evaluation build using Python alone."""
import ast
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output" / "relay-local.zip"


def build():
    files = [ROOT / name for name in ("server.py", "index.html", "styles.css", "README.md")]
    files.extend(sorted((ROOT / "src").glob("*.mjs")))
    ast.parse(files[0].read_text(encoding="utf-8-sig"))
    DEST.parent.mkdir(exist_ok=True)
    with ZipFile(DEST, "w", ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, file.relative_to(ROOT))
    with ZipFile(DEST) as archive:
        if archive.testzip():
            raise RuntimeError("Package failed its integrity check")
    print(f"{len(files)} runtime and documentation files packaged in {DEST}")


if __name__ == "__main__":
    build()
