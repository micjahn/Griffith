\documentclass[a4paper]{article}
\usepackage{graphicx}
\usepackage[utf8]{inputenc}
\date{\today}
\author{Griffith (http://griffith.vasconunes.net)}
\title{<@header>@DATA@</@header>}
\begin{document}
\maketitle
<!-- ITEMS -->
<@image>\includegraphics{./posters/@DATA@}
</@image><@title>
\section{@DATA@}</@title>

\begin{itemize}
<@number>
		\item {@TITLE@: @DATA@}
</@number><@title>
		\item {@TITLE@: @DATA@}
</@title><@o_title>
		\item {@TITLE@: @DATA@}
</@o_title><@year>
		\item {@TITLE@: @DATA@}
</@year><@director>
		\item {@TITLE@: @DATA@}
</@director><@rating>
		\item {@TITLE@: @DATA@}
</@rating><@runtime>
		\item {@TITLE@: @DATA@}
</@runtime><@country>
		\item {@TITLE@: @DATA@ min.}
</@country><@genre>
		\item {@TITLE@: @DATA@}
</@genre><@site>
		\item {@TITLE@: @DATA@}
</@site><@o_site>
		\item {@TITLE@: @DATA@}
</@o_site><@trailer>
		\item {@TITLE@: @DATA@}
</@trailer><@medium_id>
		\item {@TITLE@: @DATA@}
</@medium_id><@seen>
		\item {@TITLE@: @DATA@}
</@seen><@loaned>
		\item {@TITLE@: @DATA@}
</@loaned><@classification>
		\item {@TITLE@: @DATA@}
</@classification><@studio>
		\item {@TITLE@: @DATA@}
</@studio><@cast>
		\item {@TITLE@: @DATA@}
</@cast><@plot>
		\item {@TITLE@: @DATA@}
</@plot><@notes>
		\item {@TITLE@: @DATA@}
</@notes>
\end{itemize}

<!-- /ITEMS -->
\emph{\small{
	<@copyright>@DATA@</@copyright>
}}
\end{document}
