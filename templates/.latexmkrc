# Force XeLaTeX: this template uses fontspec/xeCJK + system CJK fonts.
# pdfLaTeX cannot compile it. With this file, `latexmk -pdf` auto-uses xelatex.
$pdf_mode = 1;
$pdflatex = 'xelatex %O %S';
