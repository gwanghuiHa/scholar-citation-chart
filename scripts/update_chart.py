import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests


AUTHOR_ID = "PYBcymoAAAAJ"
SERPAPI_KEY = os.environ["SERPAPI_KEY"]

PUBLIC_DIR = Path("public")
PUBLIC_DIR.mkdir(exist_ok=True)

params = {
    "engine": "google_scholar_author",
    "author_id": AUTHOR_ID,
    "hl": "en",
    "api_key": SERPAPI_KEY,
}

response = requests.get("https://serpapi.com/search", params=params, timeout=30)
response.raise_for_status()
data = response.json()

cited_by = data.get("cited_by", {})
graph = cited_by.get("graph", [])

if not graph:
    raise RuntimeError("No citation graph found in SerpApi response.")

years = [str(item["year"]) for item in graph]
citations = [int(item["citations"]) for item in graph]

table = cited_by.get("table", [])

total_citations = None
h_index = None
i10_index = None

for row in table:
    if "citations" in row:
        total_citations = row["citations"].get("all")
    if "h_index" in row:
        h_index = row["h_index"].get("all")
    if "i10_index" in row:
        i10_index = row["i10_index"].get("all")

last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Google Scholar Citations</title>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: Arial, Helvetica, sans-serif;
      color: #222;
    }}

    .card {{
      width: 100%;
      max-width: 760px;
      box-sizing: border-box;
      border: 1px solid #e5e5e5;
      border-radius: 14px;
      padding: 18px 20px 14px 20px;
      background: #ffffff;
    }}

    h3 {{
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 650;
    }}

    .metrics {{
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
      margin: 8px 0 14px 0;
      font-size: 13px;
      color: #444;
    }}

    .metric strong {{
      color: #111;
    }}

    .chart-wrap {{
      position: relative;
      height: 290px;
      width: 100%;
    }}

    .caption {{
      margin-top: 10px;
      font-size: 11px;
      color: #666;
    }}
  </style>
</head>

<body>
  <div class="card">
    <h3>Google Scholar citations</h3>

    <div class="metrics">
      <div class="metric"><strong>Total citations:</strong> {total_citations if total_citations is not None else "N/A"}</div>
      <div class="metric"><strong>h-index:</strong> {h_index if h_index is not None else "N/A"}</div>
      <div class="metric"><strong>i10-index:</strong> {i10_index if i10_index is not None else "N/A"}</div>
    </div>

    <div class="chart-wrap">
      <canvas id="citationChart"></canvas>
    </div>

    <div class="caption">
      Citation data from Google Scholar. Last updated: {last_updated}.
    </div>
  </div>

  <script>
    const years = {json.dumps(years)};
    const citations = {json.dumps(citations)};

    const ctx = document.getElementById("citationChart");

    new Chart(ctx, {{
      type: "bar",
      data: {{
        labels: years,
        datasets: [{{
          label: "Citations",
          data: citations,
          borderWidth: 1
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            display: false
          }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                return context.parsed.y + " citations";
              }}
            }}
          }}
        }},
        scales: {{
          x: {{
            title: {{
              display: true,
              text: "Year"
            }}
          }},
          y: {{
            beginAtZero: true,
            title: {{
              display: true,
              text: "Citations"
            }},
            ticks: {{
              precision: 0
            }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""

(PUBLIC_DIR / "index.html").write_text(html, encoding="utf-8")

print("Wrote public/index.html")
