from duckduckgo_search import DDGS
from pathlib import Path
import time

queries = Path("queries/mass_queries.txt").read_text().splitlines()

out = Path("results/harvested_urls.txt")

seen = set()

with out.open("w") as f:

    for q in queries:

        print(f"[SEARCH] {q}")

        try:
            with DDGS() as ddgs:

                results = ddgs.text(
                    q,
                    max_results=20
                )

                for r in results:

                    url = r.get("href")

                    if not url:
                        continue

                    if url in seen:
                        continue

                    seen.add(url)

                    f.write(url + "\n")

                    print(url)

        except Exception as e:
            print(e)

        time.sleep(2)
