#!/bin/zsh

mkdir -p downloads

while read url; do
    echo "Downloading: $url"

    filename=$(echo "$url" | sed 's#https\?://##' | sed 's#[/:?&]#_#g')

    curl -L \
         --connect-timeout 20 \
         --max-time 120 \
         -A "Mozilla/5.0" \
         "$url" \
         -o "downloads/${filename}.html"

    sleep 2

done < results/all_urls.txt
