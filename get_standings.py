# import html
import json
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

# Liga auswählen (aus/ein-kommentieren)
# Herren 1
URL = (
    "https://www.basketball-bund.net/public/tabelle.jsp"
    "?print=1&viewDescKey=sport.dbb.views.TabellePublicView/index.jsp_&liga_id=53088"
)
# Herren 2
# URL = (
#     "https://www.basketball-bund.net/public/tabelle.jsp?print=1&"
#     "viewDescKey=sport.dbb.views.TabellePublicView/index.jsp_&liga_id=53322"
# )
# anderes Team
# URL = (
#     ""
# )

OUTPUT = "./HTML_Server/"

# Website abrufen
response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
response.raise_for_status()
response.encoding = response.apparent_encoding

# HTML-Tabellen auslesen
tables = pd.read_html(StringIO(response.text), displayed_only=False)

# Tabelle mit 14 Mannschaften suchen
candidates = [t for t in tables if len(t) > 2]

if not candidates:
    print("Gefundene Tabellen:")
    for i, table in enumerate(tables):
        print(i, table.shape, list(table.columns))
    raise RuntimeError("Keine Tabelle mit mindestens 2 Mannschaften gefunden.")

df = candidates[0].copy()

# Daten bereinigen
df = df.fillna("")
df = df.astype(str)

# columns = [str(c) for c in df.columns]
rows = df.values.tolist()

data = {
    "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
    "rows": rows,
}

# JSON speichern
with open(OUTPUT + "standings.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Tabelle erfolgreich gespeichert.")
print(f"{len(rows)} Mannschaften")
print(data["updated_at"])
