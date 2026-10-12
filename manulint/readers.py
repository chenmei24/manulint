"""Read manuscript text and embedded figures from .docx / .md / .txt files."""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image


@dataclass
class Figure:
    name: str
    image: Image.Image
    width_in: float | None  # displayed width in inches (docx only)


@dataclass
class Manuscript:
    text: str
    figures: list = field(default_factory=list)
    source: str = ""


def read_manuscript(path: str | Path) -> Manuscript:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".docx":
        return _read_docx(p)
    if suffix in (".md", ".markdown", ".txt", ".text"):
        return _read_text(p)
    raise ValueError(f"unsupported file type: {suffix} (use .docx / .md / .txt)")


def _read_text(p: Path) -> Manuscript:
    text = p.read_text(encoding="utf-8", errors="replace")
    figs: list[Figure] = []
    if p.suffix.lower() in (".md", ".markdown"):
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
            img_path = (p.parent / m.group(1).strip()).resolve()
            if img_path.is_file():
                try:
                    figs.append(Figure(img_path.name, Image.open(img_path), None))
                except Exception:
                    pass
    return Manuscript(text=text, figures=figs, source=str(p))


def _read_docx(p: Path) -> Manuscript:
    from docx import Document

    doc = Document(str(p))
    paras = [para.text for para in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            paras.append(" | ".join(cell.text for cell in row.cells))
    text = "\n".join(paras)

    figs: list[Figure] = []
    try:
        figs = _extract_docx_figures(p, doc)
    except Exception:
        pass
    return Manuscript(text=text, figures=figs, source=str(p))


def _extract_docx_figures(p: Path, doc) -> list[Figure]:
    """Extract embedded images and estimate displayed width.

    Heuristic: inline shapes appear in document order, matching the order of
    image parts in word/media/. Good enough for a DPI sanity check.
    """
    EMU_PER_INCH = 914400
    widths: list[float] = []
    for shape in doc.inline_shapes:
        try:
            widths.append(shape.width / EMU_PER_INCH)
        except Exception:
            widths.append(None)  # type: ignore[arg-type]

    images: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(p) as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                images.append((Path(name).name, zf.read(name)))

    figs: list[Figure] = []
    for i, (name, blob) in enumerate(images):
        try:
            img = Image.open(io.BytesIO(blob))
            img.load()
        except Exception:
            continue
        w = widths[i] if i < len(widths) else None
        figs.append(Figure(name, img, w))
    return figs
