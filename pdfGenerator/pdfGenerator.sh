#!/bin/bash

SOURCE_DIR=/home/hyungro/fg/fg-github/clone/cloud-metrics/results/build/html/results
DESTINATION_DIR=$SOURCE_DIR/pdf

for file in `ls $SOURCE_DIR/*Q*.html`
do
	filename=$(basename "$file")
	filename="${filename%.*}"

	pdf_filename=$filename".pdf"
	pdf_generator=$pdf_filename".generator"

	# Create the list
	awk -F"\"|?" 'BEGIN {count=0;}/<iframe/{print "xvfb-run -a -s \"-screen 0 1920x1024x24\" wkhtmltopdf --redirect-delay 1000 https://portal.futuregrid.org/metrics/html/results/"$10 " 2012-Q3-"count".pdf";count++;} END {"seq  -f \"2012-Q3-%g.pdf\" -s\" \" 0 "count-1|getline filelist;print "pdftk "filelist " cat output output.pdf"}' $file > $pdf_generator

	# Execute the list
	bash $pdf_generator

	# Be ready to upload
	mv output.pdf $pdf_filename

done
