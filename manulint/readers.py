"""Read local manuscript text and each embedded image occurrence."""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image


@dataclass
class Figure:
    name: str
    image: Image.Image | None
    width_in: float | None
    height_in: float | None = None
    skip_reason: str = ""


@dataclass
class Manuscript:
    text: str
    figures: list[Figure] = field(default_factory=list)
    source: str = ""
    notes: list[str] = field(default_factory=list)


def read_manuscript(path: str | Path) -> Manuscript:
    p = Path(path)
    suffix = p.suffix.lower()
    try:
        if suffix == ".docx":
            manuscript = _read_docx(p)
        elif suffix in (".md", ".markdown", ".txt", ".text"):
            manuscript = _read_text(p)
        else:
            raise ValueError(f"Unsupported file type: {suffix} (use .docx / .md / .txt)")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Cannot read manuscript: {exc}") from exc
    if not manuscript.text.strip():
        raise ValueError("Manuscript has no extractable text; provide a non-empty document.")
    return manuscript


def _load_image(blob: bytes) -> Image.Image:
    with Image.open(io.BytesIO(blob)) as image:
        image.load()
        return image.copy()


def _read_text(p: Path) -> Manuscript:
    text = p.read_text(encoding="utf-8-sig")
    figures: list[Figure] = []
    if p.suffix.lower() in (".md", ".markdown"):
        for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
            target = match.group(1).strip().strip("<>")
            if re.match(r"\w+://", target):
                figures.append(Figure(target, None, None, skip_reason="Remote images are not downloaded."))
                continue
            image_path = p.parent / target
            try:
                image = _load_image(image_path.read_bytes())
                figures.append(Figure(image_path.name, image, None))
            except Exception:
                figures.append(Figure(image_path.name, None, None,
                                      skip_reason="Image is missing, unreadable, or unsupported (including vector formats)."))
    return Manuscript(text=text, figures=figures, source=str(p))


def _read_docx(p: Path) -> Manuscript:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    try:
        doc = Document(str(p))
        paragraphs = []
        for element in doc.element.body:
            if element.tag == qn("w:p"):
                paragraphs.append(Paragraph(element, doc).text)
            elif element.tag == qn("w:tbl"):
                table = Table(element, doc)
                for row in table.rows:
                    paragraphs.append(" | ".join(cell.text for cell in row.cells))
        figures = _extract_docx_figures(doc)
        notes = []
        if doc.element.body.xpath(".//w:pict"):
            notes.append("Legacy VML pictures were skipped; raster DPI checks cover modern body drawings only.")
        return Manuscript("\n".join(paragraphs), figures, str(p), notes)
    except Exception as exc:
        raise ValueError(f"Cannot read DOCX: file may be damaged, encrypted, or unsupported ({type(exc).__name__}).") from exc


def _extract_docx_figures(doc) -> list[Figure]:
    """Resolve each drawing by relationship ID, including reused image parts."""
    from docx.oxml.ns import qn

    figures: list[Figure] = []
    for drawing in doc.element.body.xpath(".//w:drawing"):
        extents = drawing.xpath(".//wp:extent")
        extent = extents[0] if extents else None
        try:
            width = int(extent.get("cx")) / 914400 if extent is not None else None
            height = int(extent.get("cy")) / 914400 if extent is not None else None
        except (TypeError, ValueError):
            width = height = None
        for blip in drawing.xpath(".//a:blip"):
            occurrence = len(figures) + 1
            rel_id = blip.get(qn("r:embed"))
            part = doc.part.related_parts.get(rel_id)
            if part is None:
                figures.append(Figure(f"drawing {occurrence}", None, width, height,
                                      "External or unresolved image relationship; image was skipped."))
                continue
            name = f"{Path(str(part.partname)).name} (occurrence {occurrence})"
            if Path(str(part.partname)).suffix.lower() in (".svg", ".emf", ".wmf", ".eps"):
                figures.append(Figure(name, None, width, height,
                                      "Vector format: raster DPI does not apply; verify the journal's format requirements."))
                continue
            try:
                image = _load_image(part.blob)
                figures.append(Figure(name, image, width, height))
            except Exception:
                figures.append(Figure(name, None, width, height,
                                      "Unsupported or unreadable image; resolution was not checked."))
    return figures
