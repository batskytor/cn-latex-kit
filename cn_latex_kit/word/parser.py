"""Parse a Word (.docx) thesis template into a :class:`FormatSpec`.

Word templates used by Chinese journals typically describe their rules twice:

* **structurally**, through section properties, styles and runs; and
* **verbally**, in note boxes such as ``字体：宋体，字号：五号，行距：多倍行距1.15``.

Real-world templates put crucial information (captions, references, headings)
only in the verbal notes, so this parser reads *both* channels and merges them.
Structural values are the baseline; verbal notes refine the specific roles
(title / author / abstract / caption / ...).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from ..latex.spec import (
    FormatSpec, FontSpec, PageSpec, SizeSpec,
    canonical_cjk_font, pt_to_zh_size,
)

try:  # python-docx is the normal path
    from docx import Document
    from docx.oxml.ns import qn
    _HAS_DOCX = True
except ImportError:  # pragma: no cover - exercised only without dependency
    Document = None  # type: ignore
    _HAS_DOCX = False


# ---------------------------------------------------------------------------
# Small extractors for the verbal notes
# ---------------------------------------------------------------------------
_FONT_RE = re.compile(r"字体[：:]?\s*(?:中文)?\s*([\u4e00-\u9fa5A-Za-z]+)")
_SIZE_RE = re.compile(r"字号[：:]?\s*(小?[一二三四五六七八九十]号?|[0-9]+(?:\.[0-9]+)?\s*pt|[0-9]+(?:\.[0-9]+)?)")
_BARE_SIZE_RE = re.compile(r"(小?[一二三四五六七八九十]号?)")
_SPACING_RE = re.compile(r"(?:多倍行距|行距)[：:]?\s*([0-9]+(?:\.[0-9]+)?)\s*倍?")
_XSPACE_SPACING_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*倍行距")
_INDENT_RE = re.compile(r"缩进\s*([0-9]+)\s*字")
_COLS_RE = re.compile(r"跨接两栏|双栏|分栏")


def _extract_font(text: str) -> Optional[str]:
    m = _FONT_RE.search(text)
    return canonical_cjk_font(m.group(1)) if m else None


def _clean_size(raw: str) -> Optional[str]:
    if "pt" in raw:
        return pt_to_zh_size(float(re.sub(r"[^\d.]", "", raw)))
    if raw.isdigit():
        return pt_to_zh_size(float(raw))
    # Canonical names: "小二"/"小五" (no 号) vs "五号"/"三号" (with 号).
    if raw.startswith("小"):
        cleaned = raw[:-1] if raw.endswith("号") else raw
    else:
        cleaned = raw if raw.endswith("号") else raw + "号"
    if cleaned in ("一", "号", ""):
        return None
    return cleaned


def _extract_size(text: str) -> Optional[str]:
    m = _SIZE_RE.search(text)
    if m:
        return _clean_size(m.group(1))
    m = _BARE_SIZE_RE.search(text)
    return _clean_size(m.group(1)) if m else None


def _extract_spacing(text: str) -> Optional[float]:
    for rx in (_SPACING_RE, _XSPACE_SPACING_RE):
        m = rx.search(text)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def _extract_indent(text: str) -> Optional[float]:
    m = _INDENT_RE.search(text)
    return float(m.group(1)) if m else None


def _norm(text: str) -> str:
    """Normalise full-width spaces/punctuation a bit for matching."""
    return text.replace("\u3000", " ").replace("\xa0", " ")


# ---------------------------------------------------------------------------
# Rule table: which verbal notes fill which spec field
# ---------------------------------------------------------------------------
# (attribute path, required keywords, description)
# Distinct keys for "reference title" vs "reference body" avoid one note's
# spacing/font overwriting the other's.
_RULES: List[Tuple[str, Tuple[str, ...], str]] = [
    ("title",          ("中文题目",),      "中文题目"),
    ("author",         ("作者姓名",),      "作者姓名"),
    ("abstract",       ("此处是摘要",),    "中文摘要"),
    ("en_title",       ("英文标题",),      "英文标题"),
    ("author_info",    ("基金项目",),      "基金项目/作者简介"),
    ("heading1",       ("黑体", "小三", "行距"), "一级标题"),
    ("heading2",       ("宋体", "五号", "加粗"), "二级标题"),
    ("caption",        ("图名", "黑体"),   "图表名"),
    ("caption",        ("表名", "黑体"),   "图表名"),
    ("reference_body", ("参考文献正文",), "参考文献正文"),
    ("reference_title",("参考文献", "黑体"), "参考文献标题"),
    ("body",           ("正文", "宋体", "五号"), "正文"),
]


class WordTemplateParser:
    """Extract a :class:`FormatSpec` from a Word thesis template."""

    def __init__(self, docx_path: str | Path, verbose: bool = False) -> None:
        self.path = Path(docx_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Word 模板不存在: {self.path}")
        if not _HAS_DOCX:
            raise RuntimeError(
                "缺少依赖 python-docx，请先运行: pip install python-docx"
            )
        self.verbose = verbose
        self.logs: List[str] = []
        self.doc = Document(str(self.path))

    def _log(self, msg: str) -> None:
        self.logs.append(msg)

    # -- structural channel -------------------------------------------------
    def _parse_page(self) -> PageSpec:
        page = PageSpec()
        try:
            sec = self.doc.sections[0]
            if sec.page_width:
                page.width_mm = round(sec.page_width.mm, 1)
            if sec.page_height:
                page.height_mm = round(sec.page_height.mm, 1)
            if sec.top_margin:
                page.top_mm = round(sec.top_margin.mm, 1)
            if sec.bottom_margin:
                page.bottom_mm = round(sec.bottom_margin.mm, 1)
            if sec.left_margin:
                page.left_mm = round(sec.left_margin.mm, 1)
            if sec.right_margin:
                page.right_mm = round(sec.right_margin.mm, 1)
        except Exception as exc:  # noqa: BLE001 - be permissive with odd docx
            self._log(f"页面尺寸读取不完整: {exc}")

        # Column count / gap live in the raw sectPr XML.
        try:
            nums: List[int] = []
            gaps: List[float] = []
            for sec in self.doc.sections:
                cols = sec._sectPr.find(qn("w:cols"))
                if cols is None:
                    continue
                nums.append(int(cols.get(qn("w:num"), "1")))
                space = cols.get(qn("w:space"))
                if space:
                    # twips -> mm : 1 twip = 1/1440 inch = 25.4/1440 mm
                    gaps.append(int(space) * 25.4 / 1440)
            if nums:
                page.columns = max(set(nums), key=nums.count) if 2 in nums else nums[0]
            if gaps:
                page.columnsep_mm = round(sum(gaps) / len(gaps), 1)
        except Exception as exc:  # noqa: BLE001
            self._log(f"分栏设置读取不完整: {exc}")

        self._log(
            f"页面: {page.width_mm}×{page.height_mm}mm, "
            f"边距 上{page.top_mm}/下{page.bottom_mm}/左{page.left_mm}/右{page.right_mm}mm, "
            f"{page.columns}栏 栏距{page.columnsep_mm}mm"
        )
        return page

    def _parse_normal_style(self) -> Tuple[FontSpec, SizeSpec, float, float]:
        fonts = FontSpec()
        sizes = SizeSpec()
        spacing = 1.15
        indent = 2.0
        try:
            normal = self.doc.styles["Normal"]
            rpr = normal.element.get_or_add_rPr()
            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is not None:
                ea = rfonts.get(qn("w:eastAsia"))
                if ea:
                    fonts.cjk_body = canonical_cjk_font(ea)
                ascii_f = rfonts.get(qn("w:ascii"))
                if ascii_f and "Times" in ascii_f:
                    fonts.latin = "Times New Roman"
            if normal.font.size is not None:
                sizes.body = pt_to_zh_size(normal.font.size.pt)
            pf = normal.paragraph_format
            if pf.line_spacing is not None:
                try:
                    ls = float(pf.line_spacing)
                    if 0 < ls < 10:  # a multiple, not an absolute length
                        spacing = round(ls, 2)
                except (TypeError, ValueError):
                    pass
            if pf.first_line_indent is not None:
                try:
                    mm = pf.first_line_indent.mm
                    pt = mm * 72 / 25.4
                    # Roughly convert to "characters" using the body size.
                    body_pt = {"五号": 10.5, "小四": 12.0, "小五": 9.0}.get(sizes.body, 10.5)
                    indent = max(1.0, round(pt / body_pt))
                except (AttributeError, TypeError):
                    pass
        except Exception as exc:  # noqa: BLE001
            self._log(f"Normal 样式读取不完整: {exc}")
        self._log(
            f"样式: 正文 {fonts.cjk_body}/{sizes.body}, "
            f"行距 {spacing}, 首行缩进 {indent:g} 字"
        )
        return fonts, sizes, spacing, indent

    # -- verbal channel -----------------------------------------------------
    def _iter_paragraph_texts(self) -> Iterable[str]:
        for p in self.doc.paragraphs:
            t = _norm(p.text)
            if t.strip():
                yield t
        # Notes often live inside tables / textboxes; scan those too.
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    t = _norm(cell.text)
                    if t.strip():
                        yield t
        # Most "注：..." notes in journal templates live in textboxes (wps:wsp /
        # v:textbox), which python-docx does not expose. Pull their <w:p> text
        # directly from the raw document XML so those rules can fire.
        try:
            body = self.doc.element.body
            for para in body.iter(qn("w:p")):
                parts = [node.text or "" for node in para.iter(qn("w:t"))]
                t = _norm("".join(parts))
                if t.strip():
                    yield t
        except Exception as exc:  # noqa: BLE001
            self._log(f"文本框文本读取不完整: {exc}")

    def _apply_rules(self, fonts: FontSpec, sizes: SizeSpec,
                     spec: FormatSpec) -> None:
        texts = list(self._iter_paragraph_texts())
        # Join with a separator so a rule can match a note spread over lines
        # only when keywords are close; we still test per-paragraph first.
        for attr, keywords, label in _RULES:
            for text in texts:
                if not all(k in text for k in keywords):
                    continue
                # Textbox paragraphs can merge several notes. Restrict the
                # extraction to a window around the last keyword so we pick
                # e.g. the author's "楷体/小三", not the title's "黑体/小二".
                anchor = text.rfind(keywords[-1])
                window = text[max(0, anchor - 40): anchor + 120]
                font = _extract_font(window)
                size = _extract_size(window)
                spacing = _extract_spacing(window)
                indent = _extract_indent(window)
                changed = False

                # Font role assignment
                if font:
                    if attr in ("title", "caption", "heading1", "reference_title"):
                        fonts.cjk_heading = font
                    elif attr in ("author", "abstract", "author_info"):
                        fonts.cjk_abstract = font
                    elif attr in ("heading2", "body", "reference_body"):
                        fonts.cjk_body = font
                    changed = True

                # Size role assignment (reference-title notes carry no size)
                if size and attr != "reference_title":
                    if attr == "reference_body":
                        sizes.reference = size
                    elif hasattr(sizes, attr):
                        setattr(sizes, attr, size)
                    elif attr == "caption":
                        sizes.caption = size
                    else:
                        continue
                    changed = True

                # Spacing / indent role assignment
                if attr == "body":
                    if spacing:
                        spec.body_line_spacing = spacing
                        changed = True
                    if indent:
                        spec.body_indent_em = indent
                        changed = True
                elif attr == "heading1" and spacing:
                    spec.heading1_line_spacing = spacing
                    changed = True
                elif attr == "reference_body" and spacing:
                    spec.reference_line_spacing = spacing
                    changed = True

                if changed:
                    self._log(f"规则命中[{label}]: font={font} size={size} spacing={spacing}")
                    # A rule fires once (first matching note wins).
                    break

        # Captions: detect placement (figure below / table above) and bilingual.
        joined = "\n".join(texts)
        spec.caption_figure_below = ("图名" not in joined) or ("图下" in joined or "位于图下" in joined)
        spec.caption_table_above = ("表名" not in joined) or ("表的上方" in joined or "位于表上方" in joined)
        spec.bilingual_abstract = "Abstract" in joined or "英文摘要" in joined
        spec.three_line_table = "三线表" in joined
        if _COLS_RE.search(joined):
            self._log("文本提示存在分栏/跨栏要求")

    # -- public -------------------------------------------------------------
    def parse(self) -> FormatSpec:
        """Run the full extraction and return a populated spec."""
        page = self._parse_page()
        fonts, sizes, spacing, indent = self._parse_normal_style()

        spec = FormatSpec(
            source_docx=str(self.path),
            page=page,
            fonts=fonts,
            sizes=sizes,
            body_line_spacing=spacing,
            body_indent_em=indent,
            notes=self.logs,
        )
        self._apply_rules(fonts, sizes, spec)
        spec.notes = list(self.logs)
        return spec
