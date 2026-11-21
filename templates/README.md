# 内置期刊模板

这是从《哈尔滨理工大学学报》Word 模板提取格式后制作的 LaTeX 模板，已经用 XeLaTeX 编译验证。

- `hustjournal.cls`：封装页面、字体、标题、摘要、图表公式、参考文献等全部格式
- `main.tex`：完整示例论文，填入自己的内容即可使用
- `.latexmkrc`：强制使用 XeLaTeX，解决 `latexmk -pdf` 误用 pdfLaTeX 导致的 `fontspec` 报错

## 使用

```bash
# 方式一：用本工具初始化
cnlatex init -o my-paper
cd my-paper
cnlatex compile main.tex

# 方式二：直接复制本目录三个文件到你的论文目录，然后
xelatex main.tex    # 或用你编辑器的 latexmk（.latexmkrc 会自动切到 XeLaTeX）
```

依赖字体：宋体 SimSun、黑体 SimHei、楷体 KaiTi、仿宋 FangSong、Times New Roman（Windows 系统通常自带）。
