#!/bin/zsh

cd ~/alaska_aidc_research

source .venv/bin/activate

echo "=== Harvest URLs ==="
python scripts/harvest_urls.py

echo "=== Filter URLs ==="
grep -Ei '(energy\.gov|eia\.gov|lbl\.gov|iea\.org|meti\.go\.jp|soumu\.go\.jp|msit\.go\.kr|motie\.go\.kr|kpx\.or\.kr|kepco\.co\.kr|ndrc\.gov\.cn|ndc\.gov\.tw|europa\.eu|fcc\.gov|ntia\.gov|usgs\.gov|noaa\.gov|aws\.amazon\.com|microsoft\.com|meta\.com|oracle\.com|google\.com)' \
results/harvested_urls.txt \
> results/high_value_urls.txt

echo "=== Download Sources ==="
python scripts/download_urls.py results/high_value_urls.txt downloads

echo "=== Extract HTML ==="
python scripts/extract_html.py

echo "=== Extract PDF ==="
python scripts/extract_pdfs.py

echo "=== Metadata ==="
python scripts/metadata_index.py

echo "=== Categorize ==="
python scripts/categorize.py

echo "=== Summaries ==="
python scripts/summarize.py

echo "=== Insights ==="
python scripts/insight_extraction.py

echo "=== Knowledge Graph ==="
python scripts/knowledge_graph.py

echo "=== Vector DB ==="
python scripts/vector_index.py

echo "=== Done ==="