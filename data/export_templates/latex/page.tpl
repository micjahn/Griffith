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
</@title><@original_title>
		\item {@TITLE@: @DATA@}
</@original_title><@year>
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
</@genre><@imdb>
		\item {@TITLE@: @DATA@}
</@imdb><@site>
		\item {@TITLE@: @DATA@}
</@site><@trailer>
		\item {@TITLE@: @DATA@}
</@trailer><@media>
		\item {@TITLE@: @DATA@}
</@media><@seen>
		\item {@TITLE@: @DATA@}
</@seen><@loaned>
		\item {@TITLE@: @DATA@}
</@loaned><@classification>
		\item {@TITLE@: @DATA@}
</@classification><@studio>
		\item {@TITLE@: @DATA@}
</@studio><@actors>
		\item {@TITLE@: @DATA@}
</@actors><@plot>
		\item {@TITLE@: @DATA@}
</@plot><@obs>
		\item {@TITLE@: @DATA@}
</@obs>
\end{itemize}

<!-- /ITEMS -->
\emph{\small{
	<@copyright>@DATA@</@copyright>
}}
\end{document}
