all: report.pdf

report.pdf: report.tex
	pdflatex report
	bibtex report
	pdflatex report
	pdflatex report


clean:
	rm -f *.aux *.bbl *.blg *.cut *.dvi *.log *.out *.synctex.gz *.fdb_latexmk *.fls *.toc *.nav *.snm *.vrb *.pdf *.run.xml

crop:
	for f in figures/*.pdf; do pdfcrop $$f $$f; done
