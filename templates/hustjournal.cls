%% hustjournal.cls
%% 《哈尔滨理工大学学报》论文 LaTeX 模板类文件
%% 依据"论文模板.docx（哈尔滨理工大学学报论文格式规范）"编写
%% 编译方式：XeLaTeX（推荐）或 LuaLaTeX
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hustjournal}[2026/11/21 v1.0 Harbin Univ. Sci. Tech. Journal Thesis Template]

% ============================================================
% 0. 载入基类
%    基于 ctexart：UTF-8 编码、A4、正文五号(10.5pt)、双栏
%    fontset=none 以便下面手动指定字体（避免与系统字体冲突）
% ============================================================
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexart}}
\ProcessOptions\relax
\LoadClass[UTF8, a4paper, zihao=5, twocolumn, fontset=none, scheme=chinese]{ctexart}

% ============================================================
% 1. 所需宏包
% ============================================================
\RequirePackage{geometry}        % 页面尺寸与页边距
\RequirePackage{amsmath,amssymb} % 数学公式
\RequirePackage{graphicx}        % 图片
\RequirePackage{caption}         % 图表标题
\RequirePackage{booktabs}        % 三线表
\RequirePackage{fancyhdr}        % 页眉页脚
\RequirePackage{etoolbox}        % 工具宏
\RequirePackage{float}           % [H] 精确定位浮动体

% ============================================================
% 2. 字体设置（XeLaTeX + fontspec / xeCJK）
%    中文：正文宋体、标题黑体、摘要/作者楷体
%    西文：Times New Roman
% ============================================================
\RequirePackage{fontspec}
\RequirePackage{xeCJK}

\setmainfont{Times New Roman}[
  BoldFont     = Times New Roman Bold,
  ItalicFont   = Times New Roman Italic,
  BoldItalicFont = Times New Roman Bold Italic]

\setCJKmainfont{SimSun}[BoldFont = SimHei, ItalicFont = KaiTi]   % 宋体（正文），粗体映射到黑体
\setCJKsansfont{SimHei}                                           % 黑体
\setCJKmonofont{FangSong}                                         % 仿宋

% 字体快捷命令
\newcommand{\song}{\setCJKfamilyfont{song}{SimSun}\CJKfamily{song}}  % 宋体
\newcommand{\hei}{\setCJKfamilyfont{hei}{SimHei}\CJKfamily{hei}}     % 黑体
\newcommand{\kai}{\setCJKfamilyfont{kai}{KaiTi}\CJKfamily{kai}}      % 楷体
\newcommand{\fs}{\setCJKfamilyfont{fs}{FangSong}\CJKfamily{fs}}      % 仿宋

% ============================================================
% 3. 页面设置
%    A4 纸；页边距按 Word 模板：上 90.7pt≈32mm，下 70.9pt≈25mm，
%    左/右 56.7pt≈20mm；双栏间距 425twip≈21.25pt≈7.5mm
% ============================================================
\geometry{
  a4paper,
  top    = 32mm,
  bottom = 25mm,
  left   = 20mm,
  right  = 20mm,
  columnsep = 7.5mm,
  headheight = 14pt,
  headsep    = 4mm,
  footskip   = 8mm
}

% 正文行距：多倍行距 1.15，段前段后 0
\linespread{1.15}
\setlength{\parindent}{2em}       % 首行缩进 2 字
\setlength{\parskip}{0pt}

% ============================================================
% 4. 元数据变量（作者在 main.tex 中通过命令填充）
% ============================================================
\newcommand{\cnTitle}[1]{\def\@cnTitle{#1}}
\newcommand{\cnAuthor}[1]{\def\@cnAuthor{#1}}
\newcommand{\cnAffil}[1]{\def\@cnAffil{#1}}
\newcommand{\cnAbstract}[1]{\def\@cnAbstract{#1}}
\newcommand{\cnKeywords}[1]{\def\@cnKeywords{#1}}

\newcommand{\enTitle}[1]{\def\@enTitle{#1}}
\newcommand{\enAuthor}[1]{\def\@enAuthor{#1}}
\newcommand{\enAffil}[1]{\def\@enAffil{#1}}
\newcommand{\enAbstract}[1]{\def\@enAbstract{#1}}
\newcommand{\enKeywords}[1]{\def\@enKeywords{#1}}

% 中图分类 / 文献标志码 / 文章编号 / DOI（编辑填写项，可留空）
\newcommand{\doi}[1]{\def\@doi{#1}}
\newcommand{\clc}[1]{\def\@clc{#1}}
\newcommand{\docCode}[1]{\def\@docCode{#1}}
\newcommand{\articleID}[1]{\def\@articleID{#1}}

% 收稿日期 / 基金项目 / 作者简介 / 通信作者
\newcommand{\received}[1]{\def\@received{#1}}
\newcommand{\foundation}[1]{\def\@foundation{#1}}
\newcommand{\authorBio}[1]{\def\@authorBio{#1}}
\newcommand{\corresponding}[1]{\def\@corresponding{#1}}

% 页眉用短信息 & 期刊卷期
\newcommand{\runningAuthor}[1]{\def\@runningAuthor{#1}}
\newcommand{\runningTitle}[1]{\def\@runningTitle{#1}}
\newcommand{\journalVol}[1]{\def\@journalVol{#1}}
\newcommand{\journalIssue}[1]{\def\@journalIssue{#1}}
\newcommand{\journalYear}[1]{\def\@journalYear{#1}}
\newcommand{\journalMonth}[1]{\def\@journalMonth{#1}}
\newcommand{\journalMonthEN}[1]{\def\@journalMonthEN{#1}}

% 默认值
\def\@cnTitle{} \def\@cnAuthor{} \def\@cnAffil{} \def\@cnAbstract{} \def\@cnKeywords{}
\def\@enTitle{} \def\@enAuthor{} \def\@enAffil{} \def\@enAbstract{} \def\@enKeywords{}
\def\@doi{} \def\@clc{} \def\@docCode{} \def\@articleID{}
\def\@received{} \def\@foundation{} \def\@authorBio{} \def\@corresponding{}
\def\@runningAuthor{} \def\@runningTitle{}
\def\@journalVol{} \def\@journalIssue{} \def\@journalYear{} \def\@journalMonth{} \def\@journalMonthEN{}

% ============================================================
% 5. 页眉页脚
% ============================================================
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
% 普通页页眉：左"第 X 期"，右"作者：短题目"
\fancyhead[L]{\zihao{-5}\hei 第~\@journalIssue~期}
\fancyhead[R]{\zihao{-5}\hei \@runningAuthor：\@runningTitle}
% 首页特殊页眉（期刊刊头，横跨版心的两行）
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyhead[C]{\zihao{-5}
    \begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lll@{}}
      第~\@journalVol~卷~第~\@journalIssue~期 & \hei 哈 尔 滨 理 工 大 学 学 报 & Vol.~\@journalVol~~No.~\@journalIssue\\[-2pt]
      \@journalYear 年~\@journalMonth 月 & Journal of Harbin University of Science and Technology & \@journalMonthEN~\@journalYear
    \end{tabular*}
  }
}

% ============================================================
% 6. 标题层级（对应 Word 大纲）
%    一级标题（引言/正文标题/结论）：黑体 小三(15pt)，1.5 倍行距
%    二级标题（小节）：宋体 五号加粗，1.15 倍行距
% ============================================================
\ctexset{
  section = {
    format   = \hei\zihao{-3}\linespread{1.5}\selectfont\centering,
    name     = {},
    number   = \arabic{section},
    aftername= \quad,
    beforeskip = 6pt,
    afterskip  = 6pt
  },
  subsection = {
    format   = \song\zihao{5}\bfseries\raggedright,
    name     = {},
    number   = \arabic{section}.\arabic{subsection},
    aftername= \quad,
    beforeskip = 6pt,
    afterskip  = 3pt
  }
}

% "引言""结论"等无编号一级标题的便捷命令
\newcommand{\sectionNC}[1]{\section*{#1}\addcontentsline{toc}{section}{#1}}

% ============================================================
% 7. 图表标题
%    中文图名：黑体 小五 居中 加粗；英文图名：Times 小五 居中 加粗
%    图题在图下，表题在表上
% ============================================================
\DeclareCaptionFont{cncap}{\hei\zihao{-5}\bfseries}
\captionsetup{
  format       = plain,
  labelsep     = quad,
  justification= centering,
  font         = cncap,
  labelfont    = cncap
}
\captionsetup[figure]{position=bottom, aboveskip=4pt, belowskip=2pt}
\captionsetup[table] {position=top,    aboveskip=6pt, belowskip=4pt}
\renewcommand{\figurename}{图}
\renewcommand{\tablename}{表}

% 英文图题 / 表题（放在 \caption 之后或之前）
\newcommand{\figCaptionEN}[1]{%
  {\zihao{-5}\centering \textbf{Fig.~\thefigure\quad #1}\par}}
\newcommand{\tabCaptionEN}[1]{%
  {\zihao{-5}\centering \textbf{Table~\thetable\quad #1}\par}}

% 三线表样式
\newcommand{\threeLineTableBegin}{\toprule}
\newcommand{\threeLineTableMid}{\midrule}
\newcommand{\threeLineTableEnd}{\bottomrule}

% ============================================================
% 8. 公式：整行居中，编号右对齐，形如 (1)
% ============================================================
\numberwithin{equation}{section}
\renewcommand{\theequation}{\arabic{section}-\arabic{equation}}
% 若需全文连续编号（即 (1)(2)...），取消上面的 numberwithin 并启用下一行
% \renewcommand{\theequation}{\arabic{equation}}

% 上标引用文献，形如 [1]、[1-5]
\newcommand{\upcite}[1]{\textsuperscript{\cite{#1}}}

% ============================================================
% 9. 参考文献
%    标题：黑体 小五 左对齐 1.5 倍行距，段前 1 行、段后 0
%    正文：宋体 小五 左对齐 1.25 倍行距，段前后 0
% ============================================================
\renewcommand{\refname}{参考文献}
\newcommand{\bibHeading}{%
  \vspace{1\baselineskip}%
  {\hei\zihao{-5}\raggedright\linespread{1.5}\selectfont 参考文献\par}
  \vspace{2pt}}

\renewenvironment{thebibliography}[1]{%
  \bibHeading
  \song\zihao{-5}\raggedright\linespread{1.25}\selectfont
  \setlength{\parindent}{0pt}
  \setlength{\leftmargin}{2em}
  \list{\@biblabel{\@arabic\c@enumiv}}{%
    \settowidth\labelwidth{\@biblabel{#1}}
    \leftmargin\labelwidth
    \advance\leftmargin\labelsep
    \setlength{\itemsep}{0pt}
    \setlength{\parsep}{0pt}
    \usecounter{enumiv}}
  \sloppy
}{%
  \endlist
}

% ============================================================
% 10. \maketitle：输出完整中英文题名、作者、摘要、关键词等
%     在 main.tex 中用 \twocolumn[\maketitle] 使其横跨双栏
% ============================================================
\renewcommand{\maketitle}{%
  \thispagestyle{firstpage}
  \begin{center}
    % 中文题目：黑体 小二(18pt)，行距 2，段前后 0，居中
    {\hei\zihao{-2}\linespread{2}\selectfont \@cnTitle\par}
    \vspace{4pt}
    % 作者：楷体 小三(15pt)，居中
    {\kai\zihao{-3} \@cnAuthor\par}
    \vspace{2pt}
    % 单位：宋体 小五(9pt)，居中
    {\song\zihao{-5} \@cnAffil\par}
    \vspace{8pt}
    % 中文摘要：楷体 五号(10.5pt)，行距 1.15
    {\kai\zihao{5}\linespread{1.15}\selectfont
      \noindent \hei\textbf{摘\; 要：}\@cnAbstract\par}
    \vspace{4pt}
    % 关键词：楷体 五号
    {\kai\zihao{5}\linespread{1.15}\selectfont
      \noindent \hei\textbf{关键词：}\@cnKeywords\par}
    \vspace{2pt}
    % 中图分类号 / 文献标志码 / 文章编号 / DOI
    {\song\zihao{-5}
      \noindent DOI:\@doi \quad
      中图分类号：\@clc \quad
      文献标志码：\@docCode \quad
      文章编号：\@articleID\par}
    \vspace{10pt}
    % 英文题目：Times New Roman 三号(16pt)
    {\zihao{3} \@enTitle\par}
    \vspace{4pt}
    % 英文作者
    {\zihao{-4} \@enAuthor\par}
    % 英文单位
    {\zihao{-5} \@enAffil\par}
    \vspace{8pt}
    % 英文摘要
    {\zihao{5}\linespread{1.15}\selectfont
      \noindent \textbf{Abstract:} \@enAbstract\par}
    \vspace{4pt}
    % 英文关键词
    {\zihao{5}\linespread{1.15}\selectfont
      \noindent \textbf{Keywords:} \@enKeywords\par}
    \vspace{8pt}
  \end{center}
  % 作者信息：楷体 小五，左对齐
  {\kai\zihao{-5}\raggedright\linespread{1.15}\selectfont
    \noindent \textbf{收稿日期：}\@received\par
    \noindent \textbf{基金项目：}\@foundation\par
    \noindent \textbf{作者简介：}\@authorBio\par
    \noindent \textbf{通信作者：}\@corresponding\par}
  \vspace{6pt}
  \hrule height 0.6pt
  \vspace{4pt}
}

\endinput
