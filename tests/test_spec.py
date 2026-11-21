"""Tests for the size-conversion utilities."""

from cn_latex_kit.latex.spec import pt_to_zh_size, zihao, canonical_cjk_font


def test_zihao_mapping():
    assert zihao("小二") == "-2"
    assert zihao("五号") == "5"
    assert zihao("-5") == "-5"


def test_pt_conversion():
    assert pt_to_zh_size(10.5) == "五号"
    assert pt_to_zh_size(18.0) == "小二"
    assert pt_to_zh_size(9.0) == "小五"
    assert pt_to_zh_size(11.0) in ("五号", "小四")  # nearest


def test_font_alias():
    assert canonical_cjk_font("宋体") == "SimSun"
    assert canonical_cjk_font("黑体") == "SimHei"
    assert canonical_cjk_font("楷体") == "KaiTi"
    assert canonical_cjk_font("Times New Roman") == "Times New Roman"
