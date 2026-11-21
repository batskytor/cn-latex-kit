"""Tests for the Word parser using a synthetic .docx."""

import pytest

from cn_latex_kit.word.parser import WordTemplateParser

pytest.importorskip("docx")


def test_parse_real_template_if_present():
    """If the sample template is available, verify the key extracted values."""
    import os
    candidates = [
        r"D:\研究生\现代设计理论与应用\论文\论文模板.docx",
        "examples/论文模板.docx",
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if path is None:
        pytest.skip("示例 Word 模板不可用")
    spec = WordTemplateParser(path).parse()
    assert spec.page.width_mm == 210.0
    assert spec.page.height_mm == 297.0
    assert spec.page.columns == 2
    assert spec.fonts.cjk_body == "SimSun"
    assert spec.fonts.cjk_heading == "SimHei"
    assert spec.fonts.cjk_abstract == "KaiTi"
    assert spec.sizes.body == "五号"
    assert spec.sizes.title == "小二"
    assert spec.body_line_spacing == 1.15
    assert spec.reference_line_spacing == 1.25
