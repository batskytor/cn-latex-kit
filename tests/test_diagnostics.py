"""Tests for compiler-log diagnostics."""

from cn_latex_kit.build.diagnostics import Diagnostic, render_diagnostics


def test_render_no_diagnostics():
    out = render_diagnostics([])
    assert "未发现已知问题" in out


def test_render_error():
    d = Diagnostic("error", "! Fatal Package fontspec Error ...",
                   "fontspec 需要 XeLaTeX", "改用 XeLaTeX")
    out = render_diagnostics([d])
    assert "fontspec 需要 XeLaTeX" in out
    assert "改用 XeLaTeX" in out
    assert "错误" in out
