"""Tests for the LaTeX generator, including the prefix-collision regression."""

from cn_latex_kit.latex.generator import LatexGenerator
from cn_latex_kit.latex.spec import FormatSpec, FontSpec, PageSpec, SizeSpec


def make_spec() -> FormatSpec:
    return FormatSpec(
        journal_name="测试大学学报",
        page=PageSpec(top_mm=30, bottom_mm=25, left_mm=20, right_mm=20,
                      columns=2, columnsep_mm=8.0),
        fonts=FontSpec(cjk_body="SimSun", cjk_heading="SimHei",
                       cjk_abstract="KaiTi"),
        sizes=SizeSpec(body="五号", title="小二", author="小三",
                       heading1="小三", caption="小五", reference="小五"),
    )


def test_cls_has_no_placeholder_collision():
    cls = LatexGenerator(make_spec(), cls_name="testcls").render_cls()
    # \zihaoauthor must NOT eat the prefix of \zihaoauthorinfo
    assert "\\zihao{-3info}" not in cls
    assert "\\zihao{-3}" in cls
    assert "\\zihao{-5}" in cls


def test_cls_reflects_spec():
    cls = LatexGenerator(make_spec(), cls_name="testcls").render_cls()
    assert "top=30mm" in cls or "top=30.0mm" in cls
    assert "columnsep=8.0mm" in cls
    assert "SimSun" in cls and "SimHei" in cls
    assert "a4paper" in cls


def test_latexmkrc_forces_xelatex():
    rc = LatexGenerator(make_spec()).render_latexmkrc()
    assert "xelatex" in rc
    assert "pdf_mode" in rc


def test_generated_main_uses_cls_name():
    tex = LatexGenerator(make_spec(), cls_name="testcls").render_main()
    assert "\\documentclass[UTF8]{testcls}" in tex
