"""Command-line interface for cn-latex-kit."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__
from .build.compiler import compile_document
from .build.doctor import run_doctor
from .build.diagnostics import parse_log, render_diagnostics
from .latex.generator import LatexGenerator
from .word.parser import WordTemplateParser


def cmd_from_word(args: argparse.Namespace) -> int:
    """Parse a Word template and generate a LaTeX project."""
    try:
        spec = WordTemplateParser(args.docx, verbose=True).parse()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        return 1

    if args.journal_name:
        spec.journal_name = args.journal_name

    out = Path(args.out)
    paths = LatexGenerator(spec, cls_name=args.cls_name).write_all(out)

    print(f"已从 Word 模板提取格式并生成 LaTeX 项目：{out.resolve()}")
    print("-" * 60)
    print(f"  纸张/页边距 : {spec.page.width_mm:g}×{spec.page.height_mm:g}mm, "
          f"上{spec.page.top_mm:g}/下{spec.page.bottom_mm:g}/"
          f"左{spec.page.left_mm:g}/右{spec.page.right_mm:g}mm")
    print(f"  分栏        : {spec.page.columns} 栏, 栏距 {spec.page.columnsep_mm:g}mm")
    print(f"  中文字体    : 正文 {spec.fonts.cjk_body} / 标题 {spec.fonts.cjk_heading} "
          f"/ 摘要 {spec.fonts.cjk_abstract}")
    print(f"  正文字号    : {spec.sizes.body}, 行距 {spec.body_line_spacing:g}, "
          f"首行缩进 {spec.body_indent_em:g} 字")
    print("-" * 60)
    for p in paths:
        print(f"  生成: {p.name}")
    print("\n下一步：")
    print(f"  cd {out}")
    print("  cnlatex doctor     # 检查环境（可选）")
    print("  cnlatex compile    # 智能编译，自动使用 XeLaTeX")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    report = run_doctor()
    print(report.render())
    return 0 if report.all_ok else 1


def cmd_compile(args: argparse.Namespace) -> int:
    result = compile_document(args.tex, engine=args.engine,
                              auto_fix=not args.no_fix, max_runs=args.runs)
    print(result.render())
    # Always offer diagnosis on failure.
    if not result.success and args.tex:
        log = Path(args.tex).with_suffix(".log")
        if log.exists():
            print("\n" + render_diagnostics(parse_log(log)))
    return 0 if result.success else 1


def cmd_diagnose(args: argparse.Namespace) -> int:
    try:
        diags = parse_log(args.log)
    except FileNotFoundError as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        return 1
    print(render_diagnostics(diags, f"编译诊断报告（{args.log}）"))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Copy the bundled ready-to-use journal template into a directory."""
    out = Path(args.out)
    # Running from a source checkout: cli.py lives in <repo>/cn_latex_kit/,
    # so templates/ is one level up. Also try the installed-package location.
    candidates = [
        Path(__file__).resolve().parent.parent / "templates",
        Path(__file__).resolve().parent / "templates",
    ]
    source = next((p for p in candidates if p.exists()), candidates[0])
    if not source.exists():
        print("[错误] 找不到内置模板目录 templates/。", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)
    print(f"已初始化示例模板到：{out.resolve()}")
    print("  cnlatex compile main.tex   # 编译（自动使用 XeLaTeX）")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cnlatex",
        description="cn-latex-kit: 把 Word 论文格式模板转成 LaTeX 模板，并智能编译中文 LaTeX。",
    )
    parser.add_argument("--version", action="version", version=f"cnlatex {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("from-word", help="从 Word 模板生成 LaTeX 项目")
    p.add_argument("docx", help="Word 模板 .docx 文件路径")
    p.add_argument("-o", "--out", default="latex-project", help="输出目录（默认 latex-project）")
    p.add_argument("--cls-name", default="journaltemplate", help="生成的 .cls 类名")
    p.add_argument("--journal-name", default="", help="期刊中文名称（可选，用于页眉）")
    p.set_defaults(func=cmd_from_word)

    p = sub.add_parser("doctor", help="检查编译环境（编译器/字体/宏包）")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("compile", help="智能编译 .tex（自动选 XeLaTeX）")
    p.add_argument("tex", nargs="?", default="main.tex", help="主 .tex 文件（默认 main.tex）")
    p.add_argument("--engine", choices=["xelatex", "pdflatex", "latexmk"],
                   help="强制指定编译引擎")
    p.add_argument("--no-fix", action="store_true", help="不自动创建 .latexmkrc")
    p.add_argument("--runs", type=int, default=2, help="编译遍数（解析交叉引用，默认 2）")
    p.set_defaults(func=cmd_compile)

    p = sub.add_parser("diagnose", help="把编译日志错误翻译成中文并给出修复建议")
    p.add_argument("log", help=".log 日志文件路径")
    p.set_defaults(func=cmd_diagnose)

    p = sub.add_parser("init", help="复制内置的期刊 LaTeX 模板")
    p.add_argument("-o", "--out", default="my-paper", help="输出目录（默认 my-paper）")
    p.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
