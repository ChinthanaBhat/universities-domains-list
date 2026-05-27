#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Serve brand.json + logos/ as a browsable HTML page.

Run with uv (sets up an isolated env automatically -- no install step):

    uv run preview.py            # http://localhost:8000
    uv run preview.py 4444       # custom port

Or with plain Python (stdlib-only, no install needed):

    python3 preview.py

Visit `/` for the dynamically-built browser; `/logos/*` is served
directly from disk.
"""

import json
import sys
from html import escape
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

REPO = Path(__file__).resolve().parent
BRAND_JSON = REPO / "brand.json"

ISO_NAMES = {
    "AE": "United Arab Emirates", "AF": "Afghanistan", "AR": "Argentina",
    "AT": "Austria", "AU": "Australia", "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina", "BD": "Bangladesh", "BE": "Belgium",
    "BG": "Bulgaria", "BH": "Bahrain", "BR": "Brazil", "BY": "Belarus",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "CN": "China",
    "CO": "Colombia", "CR": "Costa Rica", "CU": "Cuba", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "DZ": "Algeria",
    "EC": "Ecuador", "EE": "Estonia", "EG": "Egypt", "ES": "Spain",
    "ET": "Ethiopia", "FI": "Finland", "FR": "France", "GB": "United Kingdom",
    "GE": "Georgia", "GH": "Ghana", "GR": "Greece", "HK": "Hong Kong",
    "HR": "Croatia", "HU": "Hungary", "ID": "Indonesia", "IE": "Ireland",
    "IL": "Israel", "IN": "India", "IQ": "Iraq", "IR": "Iran",
    "IS": "Iceland", "IT": "Italy", "JO": "Jordan", "JP": "Japan",
    "KE": "Kenya", "KR": "South Korea", "KW": "Kuwait", "KZ": "Kazakhstan",
    "LB": "Lebanon", "LK": "Sri Lanka", "LT": "Lithuania",
    "LU": "Luxembourg", "LV": "Latvia", "MA": "Morocco",
    "MK": "North Macedonia", "MN": "Mongolia", "MT": "Malta",
    "MX": "Mexico", "MY": "Malaysia", "NG": "Nigeria", "NL": "Netherlands",
    "NO": "Norway", "NP": "Nepal", "NZ": "New Zealand", "OM": "Oman",
    "PA": "Panama", "PE": "Peru", "PH": "Philippines", "PK": "Pakistan",
    "PL": "Poland", "PR": "Puerto Rico", "PS": "Palestine", "PT": "Portugal",
    "QA": "Qatar", "RO": "Romania", "RS": "Serbia", "RU": "Russia",
    "SA": "Saudi Arabia", "SE": "Sweden", "SG": "Singapore",
    "SI": "Slovenia", "SK": "Slovakia", "SY": "Syria", "TH": "Thailand",
    "TN": "Tunisia", "TR": "Turkey", "TW": "Taiwan", "UA": "Ukraine",
    "UG": "Uganda", "US": "United States", "UY": "Uruguay",
    "VE": "Venezuela", "VN": "Vietnam", "ZA": "South Africa",
    "ZW": "Zimbabwe",
}

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>University logos</title>
<style>
  :root{--bg:#f6f7f9;--card:#fff;--border:#e3e6eb;--text:#1a1d23;--muted:#6c757d;--link:#0d6efd}
  *{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text)}
  a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
  header{position:sticky;top:0;z-index:10;background:#fff;border-bottom:1px solid var(--border);padding:10px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  header h1{margin:0;font-size:15px;font-weight:600}header .stats{color:var(--muted);font-size:13px}
  header input[type=text]{flex:1;min-width:200px;max-width:400px;padding:5px 10px;border:1px solid var(--border);border-radius:6px;font-size:13px}
  header select{padding:5px 8px;border:1px solid var(--border);border-radius:6px;font-size:13px;max-width:200px}
  header label{font-size:12px;display:flex;gap:4px;align-items:center;cursor:pointer}
  .grid{display:grid;gap:14px;padding:14px;grid-template-columns:1fr}
  @media(min-width:700px){.grid{grid-template-columns:repeat(2,1fr)}}
  @media(min-width:1100px){.grid{grid-template-columns:repeat(3,1fr)}}
  @media(min-width:1600px){.grid{grid-template-columns:repeat(4,1fr)}}
  .card{background:var(--card);border:1px solid var(--border);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
  .card .imgs{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;min-height:120px;background:#fff}
  .card .imgs.dark{background:#2b2d31}
  .card img{max-width:100%;max-height:90px;object-fit:contain}
  .card .pair{display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;max-width:50%}
  .card .pair small{color:var(--muted);font-size:10px}
  .card .meta{padding:8px 12px;border-top:1px solid var(--border);font-size:12px}
  .card .meta .domain{font-weight:600;font-family:ui-monospace,monospace}
  .card .meta .name{color:var(--muted);margin-top:2px}
  .card .meta .country{color:var(--muted);font-size:11px}
  .card.hidden{display:none}
</style></head><body>
<header>
  <h1>University logos</h1><span class="stats" id="stats"></span>
  <input type="text" id="filter" placeholder="Filter by domain, name, or country..." autofocus>
  <select id="country-select"><option value="">All countries</option></select>
  <label><input type="checkbox" id="dark"> Dark bg</label>
  <label><input type="checkbox" id="missing-logo"> Logo missing</label>
  <label><input type="checkbox" id="missing-shield"> Shield missing</label>
</header>
<div class="grid" id="grid">
"""

FOOT = """</div>
<script>
const grid=document.getElementById('grid'),input=document.getElementById('filter'),stats=document.getElementById('stats');
const dark=document.getElementById('dark'),mLogo=document.getElementById('missing-logo'),mShield=document.getElementById('missing-shield');
const sel=document.getElementById('country-select'),total=grid.children.length;
const cc=new Map();
for(const c of grid.children){const v=c.querySelector('.country')?.textContent.trim()||'';c.dataset.country=v;if(v)cc.set(v,(cc.get(v)||0)+1);}
[...cc.entries()].sort((a,b)=>a[0].localeCompare(b[0])).forEach(([n,v])=>{const o=document.createElement('option');o.value=n;o.textContent=`${n} (${v})`;sel.appendChild(o);});
function u(){const q=input.value.trim().toLowerCase(),cn=sel.value;let v=0;
  for(const c of grid.children){let s=c.dataset.search.includes(q);
    if(cn&&c.dataset.country!==cn)s=false;
    if(mLogo.checked&&c.dataset.hasLogo==='1')s=false;
    if(mShield.checked&&c.dataset.hasShield==='1')s=false;
    c.classList.toggle('hidden',!s);if(s)v++;}
  stats.textContent=`${v}/${total} institutions`;
  for(const e of grid.querySelectorAll('.imgs'))e.classList.toggle('dark',dark.checked);}
[input,sel,dark,mLogo,mShield].forEach(e=>{e.addEventListener('input',u);e.addEventListener('change',u);});u();
</script></body></html>
"""


def render_card(entry: dict, logos_prefix: str = "logos/") -> str:
    domain = entry["domain"]
    name = entry.get("name") or ""
    country = ISO_NAMES.get(entry.get("country") or "", entry.get("country") or "")
    branding = entry.get("branding") or {}
    has_logo = "1" if branding.get("logo") else "0"
    has_shield = "1" if branding.get("shield") else "0"
    pairs = []
    for kind in ("logo", "shield"):
        rel = branding.get(kind)
        if not rel:
            continue
        # brand.json stores bare filenames; assets live under logos/
        url = rel if "/" in rel else f"{logos_prefix}{rel}"
        pairs.append(
            f'<div class="pair"><img src="{url}" alt="{kind}" loading="lazy">'
            f'<small>{kind}</small></div>'
        )
    search = f"{domain} {name} {country}".lower()
    return (
        f'<div class="card" data-search="{escape(search, quote=True)}" '
        f'data-has-logo="{has_logo}" data-has-shield="{has_shield}">'
        f'<div class="imgs">{"".join(pairs)}</div>'
        f'<div class="meta">'
        f'<div class="domain"><a href="https://www.{domain}/" target="_blank" rel="noopener">{escape(domain)}</a></div>'
        f'<div class="name">{escape(name)}</div>'
        f'<div class="country">{escape(country)}</div>'
        f'</div></div>'
    )


def build_index(logos_prefix: str = "logos/") -> bytes:
    entries = json.loads(BRAND_JSON.read_text())
    entries.sort(key=lambda e: e["domain"])
    body = HEAD + "\n".join(render_card(e, logos_prefix) for e in entries) + FOOT
    return body.encode("utf-8")


def write_static() -> Path:
    out = REPO / "preview" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(build_index(logos_prefix="../logos/"))
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO), **kwargs)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            body = build_index()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def main() -> int:
    out = write_static()
    print(f"wrote static copy to {out.relative_to(REPO)}", flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == "--static":
        return 0
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"serving brand browser on http://127.0.0.1:{port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
