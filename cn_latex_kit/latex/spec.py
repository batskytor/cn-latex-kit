"""Data model for the extracted formatting specification.

This module is the contract between the Word parser and the LaTeX generator.
Everything the generator needs is expressed through the :class:`FormatSpec`
tree of dataclasses, so the two stages stay independent and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Chinese font-size (号) conversions
# ---------------------------------------------------------------------------
# Word stores point sizes; Chinese typography uses "号".  These tables let us
# move between the three representations: 号名 <-> pt <-> \zihao argument.
ZH_SIZE_TO_PT: Dict[str, float] = {
    "初号": 42.0, "小初": 36.0,
    "一号": 26.0, "小一": 24.0,
    "二号": 22.0, "小二": 18.0,
    "三号": 16.0, "小三": 15.0,
    "四号": 14.0, "小四": 12.0,
    "五号": 10.5, "小五": 9.0,
    "六号": 7.5, "小六": 6.5,
    "七号": 5.5, "八号": 5.0,
}

ZH_SIZE_TO_ZIHao: Dict[str, str] = {
    "初号": "0", "小初": "-0",
    "一号": "1", "小一": "-1",
    "二号": "2", "小二": "-2",
    "三号": "3", "小三": "-3",
    "四号": "4", "小四": "-4",
    "五号": "5", "小五": "-5",
    "六号": "6", "小六": "-6",
    "七号": "7", "八号": "8",
}

PT_TO_ZH_SIZE: Dict[float, str] = {v: k for k, v in ZH_SIZE_TO_PT.items()}


def pt_to_zh_size(pt: float) -> str:
    """Return the closest Chinese size name for a point value."""
    if pt in PT_TO_ZH_SIZE:
        return PT_TO_ZH_SIZE[pt]
    return min(ZH_SIZE_TO_PT, key=lambda name: abs(ZH_SIZE_TO_PT[name] - pt))


def zihao(name: str) -> str:
    r"""Return the ``\zihao`` argument for a Chinese size name.

    ``zihao("小五") == "-5"`` so callers can emit ``\zihao{-5}``.
    """
    if name in ZH_SIZE_TO_ZIHao:
        return ZH_SIZE_TO_ZIHao[name]
    # Already a raw argument such as "5" or "-5".
    return name


# Canonical CJK family names as understood by fontspec/xeCJK on Windows.
CJK_FONT_ALIASES: Dict[str, str] = {
    "宋体": "SimSun", "宋": "SimSun", "simsun": "SimSun",
    "黑体": "SimHei", "黑": "SimHei", "simhei": "SimHei",
    "楷体": "KaiTi", "楷": "KaiTi", "kaiti": "KaiTi", "kai": "KaiTi",
    "仿宋": "FangSong", "fangsong": "FangSong",
    "微软雅黑": "Microsoft YaHei", "雅黑": "Microsoft YaHei",
}


def canonical_cjk_font(name: str) -> str:
    """Map a Chinese font name from a Word file to its fontspec family name."""
    key = name.strip().lower()
    for zh, en in CJK_FONT_ALIASES.items():
        if key == zh.lower():
            return en
    return name.strip()


# ---------------------------------------------------------------------------
# Specification dataclasses
# ---------------------------------------------------------------------------
@dataclass
class PageSpec:
    width_mm: float = 210.0
    height_mm: float = 297.0
    top_mm: float = 32.0
    bottom_mm: float = 25.0
    left_mm: float = 20.0
    right_mm: float = 20.0
    columns: int = 2
    columnsep_mm: float = 7.5

    @property
    def paper_option(self) -> str:
        if abs(self.width_mm - 210) < 1 and abs(self.height_mm - 297) < 1:
            return "a4paper"
        return f"paperwidth={self.width_mm}mm,paperheight={self.height_mm}mm"


@dataclass
class FontSpec:
    cjk_body: str = "SimSun"      # 正文宋体
    cjk_heading: str = "SimHei"   # 标题黑体
    cjk_abstract: str = "KaiTi"   # 摘要/作者楷体
    cjk_mono: str = "FangSong"    # 仿宋
    latin: str = "Times New Roman"


@dataclass
class SizeSpec:
    body: str = "五号"
    title: str = "小二"
    author: str = "小三"
    affiliation: str = "小五"
    abstract: str = "五号"
    en_title: str = "三号"
    author_info: str = "小五"
    heading1: str = "小三"
    heading2: str = "五号"
    caption: str = "小五"
    reference: str = "小五"


@dataclass
class FormatSpec:
    """Complete formatting specification extracted from a Word template."""

    journal_name: str = ""
    page: PageSpec = field(default_factory=PageSpec)
    fonts: FontSpec = field(default_factory=FontSpec)
    sizes: SizeSpec = field(default_factory=SizeSpec)

    body_line_spacing: float = 1.15
    body_indent_em: float = 2.0
    heading1_line_spacing: float = 1.5
    reference_line_spacing: float = 1.25

    caption_figure_below: bool = True
    caption_table_above: bool = True
    bilingual_abstract: bool = True
    three_line_table: bool = True
    equation_number_by_section: bool = True

    source_docx: str = ""
    notes: List[str] = field(default_factory=list)
