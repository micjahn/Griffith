\documentclass[a4paper]{article}
\usepackage{graphicx}
\usepackage[utf8]{inputenc}
\date{\today}
\author{Griffith (http://griffith.vasconunes.net)}
\title{<@header>@DATA@</@header>}
\begin{document}
\maketitle
<!-- ITEMS -->
<@movies_image>\includegraphics{./posters/@DATA@}
</@movies_image><@movies_title>
\section{@DATA@}</@movies_title>

\begin{itemize}
<@movies_number>
		\item {@TITLE@: @DATA@}
</@movies_number><@movies_title>
		\item {@TITLE@: @DATA@}
</@movies_title><@movies_o_title>
		\item {@TITLE@: @DATA@}
</@movies_o_title><@movies_year>
		\item {@TITLE@: @DATA@}
</@movies_year><@movies_director>
		\item {@TITLE@: @DATA@}
</@movies_director><@movies_rating>
		\item {@TITLE@: @DATA@}
</@movies_rating><@movies_runtime>
		\item {@TITLE@: @DATA@}
</@movies_runtime><@movies_country>
		\item {@TITLE@: @DATA@ min.}
</@movies_country><@movies_genre>
		\item {@TITLE@: @DATA@}
</@movies_genre><@movies_site>
		\item {@TITLE@: @DATA@}
</@movies_site><@movies_o_site>
		\item {@TITLE@: @DATA@}
</@movies_o_site><@movies_trailer>
		\item {@TITLE@: @DATA@}
</@movies_trailer><@media_name>
		\item {@TITLE@: @DATA@}
</@media_name><@movies_media_num>
		\item {@TITLE@: @DATA@}
</@movies_media_num><@vcodecs_name>
		\item {@TITLE@: @DATA@}
</@vcodecs_name><@collections_name>
		\item {@TITLE@: @DATA@}
</@collections_name><@volumes_name>
		\item {@TITLE@: @DATA@}
</@volumes_name><@movies_seen>
		\item {@TITLE@: @DATA@}
</@movies_seen><@movies_loaned>
		\item {@TITLE@: @DATA@}
</@movies_loaned><@movies_classification>
		\item {@TITLE@: @DATA@}
</@movies_classification><@movies_studio>
		\item {@TITLE@: @DATA@}
</@movies_studio><@movies_cast>
		\item {@TITLE@: @DATA@}
</@movies_cast><@movies_plot>
		\item {@TITLE@: @DATA@}
</@movies_plot><@movies_notes>
		\item {@TITLE@: @DATA@}
</@movies_notes><@movies_screenplay>
		\item {@TITLE@: @DATA@}
</@movies_screenplay><@movies_cameraman>
		\item {@TITLE@: @DATA@}
</@movies_cameraman><@movies_width>
		\item {@TITLE@: @DATA@}
</@movies_width><@movies_height>
		\item {@TITLE@: @DATA@}
</@movies_height><@movies_barcode>
		\item {@TITLE@: @DATA@}
</@movies_barcode>
\end{itemize}

<!-- /ITEMS -->
\emph{\small{
	<@copyright>@DATA@</@copyright>
}}
\end{document}
