#!/usr/bin/env bash
WIDTH=1920
HEIGHT=1080
INKSCAPE="$(which inkscape)"

if [ ! -x "$INKSCAPE" ]; then
    echo "Inkscape not installed"
    exit
fi

while getopts "w:h:" opt; do
    case "$opt" in
        w) WIDTH=$OPTARG;;
        h) HEIGHT=$OPTARG;;
    esac
done

SVGFILE=${@:$OPTIND:1}
if [ ! -f "$SVGFILE" ]; then
    echo "Input file not found"
    exit
fi
PNGFILE=$(basename -s .svg $SVGFILE).png

$INKSCAPE -z -e $PNGFILE -w $WIDTH -h $HEIGHT $SVGFILE
