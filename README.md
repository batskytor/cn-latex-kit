# cn-latex-kit

> 把 Word 论文格式模板自动转换成 LaTeX 模板，并用正确的引擎编译中文 LaTeX —— 不再被 `fontspec` 和 `latexmk -pdf` 的报错折磨。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)
![Engine](https://img.shields.io/badge/Engine-XeLaTeX-orange.svg)

## 缘起

国内很多期刊只提供 Word 模板。照着模板手写 LaTeX 既费时又容易漏掉细节；更令人头疼的是，用 VS Code / TeXstudio 默认的 `latexmk -pdf`（pdfLaTeX）编译中文模板时，会报出：

```
D:\...\runscript.tlu:933: command failed with exit code 12:
! Fatal Package fontspec Error: The fontspec package requires either XeTeX or LuaTeX.
```

这个工具把整套流程做成了命令行工具：

1. **解析 Word** —— 读取页面的页边距、纸张、分栏，以及正文里用文字描述的"字体：宋体，字号：五号，行距 1.15"等规范；
2. **生成 LaTeX** —— 产出一个参数化的 `.cls` 类文件、示例 `main.tex`，以及强制 XeLaTeX 的 `.latexmkrc`；
3. **智能编译** —— 自动识别中文文档、自动补 `.latexmkrc`，调用 XeLaTeX 编译；
4. **诊断报错** —— 把英文编译日志翻译成中文，并给出可执行的修复建议（包括上面那条 `exit code 12`）。

## 功能

| 命令 | 作用 |
| --- | --- |
| `cnlatex from-word <模板.docx>` | 解析 Word 格式，生成完整 LaTeX 项目 |
| `cnlatex init` | 复制内置的《哈尔滨理工大学学报》模板 |
| `cnlatex doctor` | 检查编译器、字体、宏包是否齐全 |
| `cnlatex compile [main.tex]` | 智能编译，自动选择 XeLaTeX 并生成 `.latexmkrc` |
| `cnlatex diagnose <日志.log>` | 把编译错误翻译成中文 + 修复建议 |

## 安装

```bash
git clone https://github.com/<你的用户名>/cn-latex-kit.git
cd cn-latex-kit
pip install -e .
```

依赖：`python-docx>=1.1.0`（解析 Word）。编译部分需要本机安装 **TeX Live** 或 **MiKTeX**（含 XeLaTeX、latexmk）。

验证环境：

```bash
cnlatex doctor
```

## 快速开始

### 场景 A：我有一個 Word 论文模板，想转成 LaTeX

```bash
cnlatex from-word "论文模板.docx" -o my-paper --journal-name "某某大学学报"
cd my-paper
cnlatex compile          # 自动用 XeLaTeX 编译，输出 main.pdf
```

生成的目录：

```
my-paper/
├── journaltemplate.cls   # 参数化的类文件（字体/字号/页面/图表/参考文献全部就位）
├── main.tex              # 填好示例数据的论文，替换文字即可
└── .latexmkrc            # 强制 XeLaTeX，一劳永逸解决 exit code 12
```

工具会从 Word 中提取并换算：

- 页面尺寸与页边距（mm）、分栏数与栏距
- 正文/标题/摘要/图表名/参考文献各自的**中文字体**与**字号**（含"五号 ↔ 10.5pt ↔ `\zihao{5}`"换算）
- 行距（正文 1.15、标题 1.5、参考文献 1.25）、首行缩进字数
- 图题在图下/表题在表上、三线表、中英文双语摘要、公式编号方式

### 场景 B：我只想正确编译已有的中文 LaTeX

```bash
cd 你的论文目录
cnlatex compile main.tex
```

它会自动检测 `fontspec`/`xeCJK`/`ctex`，如果没有 `.latexmkrc` 就自动创建一个，然后调用正确的引擎。你的编辑器（VS Code LaTeX Workshop 等）之后也能照常一键编译。

编译失败时看中文诊断：

```bash
cnlatex diagnose main.log
# 或 compile 失败时自动打印
```

示例输出（正是 `exit code 12` 那条）：

```
[错误] 1. fontspec 宏包需要 XeLaTeX 或 LuaTeX，当前用的是 pdfLaTeX。
    修复建议: 改用 XeLaTeX 编译。项目中的 .latexmkrc 已自动处理；
              若手动编译请用 `xelatex main.tex`。
```

### 场景 C：直接用内置的期刊模板

```bash
cnlatex init -o my-paper
cd my-paper
cnlatex compile
```

## 它是怎么工作的

```
论文模板.docx
      │  python-docx：读 section / styles / XML
      ▼
WordTemplateParser ──► FormatSpec（页面/字体/字号/行距…的结构化数据）
                              │
                              ▼
                       LatexGenerator
                              │  render
                              ▼
            .cls + main.tex + .latexmkrc  ──►  XeLaTeX  ──►  PDF
```

Word 模板通常把关键信息写两遍：一遍是样式（结构化），一遍是正文里的说明文字（如"中文图名设置为黑体，小五，居中，加粗"）。解析器**两条通道都读**，结构化数据打底、说明文字精修各个角色，因此即使样式里没设、只写在说明文字里的规则也能提取出来。

## 项目结构

```
cn-latex-kit/
├── cn_latex_kit/
│   ├── word/parser.py        # Word 格式解析（结构 + 文字说明双通道）
│   ├── latex/spec.py         # 格式规格数据模型 + 中文字号换算
│   ├── latex/generator.py    # 生成 .cls / .tex / .latexmkrc
│   ├── build/doctor.py       # 环境检查
│   ├── build/compiler.py     # 智能编译
│   ├── build/diagnostics.py  # 报错翻译
│   └── cli.py                # 命令行入口
├── templates/                # 内置期刊模板（init 命令复制它）
├── examples/generated/       # 由真实 Word 模板生成的示例结果
└── tests/                    # 单元测试
```

## 开发

```bash
pip install -e ".[test]"
pytest -q
```

## 已知限制

- 解析针对中文期刊 Word 模板的常见写法；如果模板用了非常规的排版（如大量文本框嵌套、图片形式的规范说明），建议用 `doctor`/`diagnose` 辅助检查。
- 生成的是**起点模板**，内容（摘要、正文等示例文字）需要替换为你的论文内容。
- 仅支持 Windows/macOS/Linux 上安装了 XeLaTeX 的环境；字体名按 Windows 系统字体（`SimSun` 等）设置，其他平台可在生成的 `.cls` 中改成对应字体名。

## License

[MIT](LICENSE)
