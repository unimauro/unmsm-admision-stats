#!/usr/bin/env python3
"""Scrapea los sitios de resultados de admisión UNMSM (admision.unmsm.edu.pe/Website{proc})
y genera historico/unmsm_historico.json con AGREGADOS por proceso x modalidad x escuela:
postulantes, ingresantes, nota máxima (general) y nota de cierre (mínima de ingresantes).

No almacena ningún dato personal: los nombres/códigos de postulantes se descartan al agregar.

Dos formatos de sitio:
- "viejo" (2024-1, 2024-2, 2025-1): modalidades en X.html, escuelas en ./X/<cod>/0.html,
  puntaje como texto en la 4ta celda, ingresante = "ALCANZO VACANTE".
- "nuevo" (2026-1, 2026-2): modalidades en X/X.html, escuelas en <cod>/results.html,
  puntaje en atributo data-score, ingresante = "ALCANZÓ VACANTE".

Los HTML descargados se cachean en --cache-dir para que re-ejecutar no vuelva a golpear
el servidor.
"""
import argparse
import datetime
import html as htmllib
import json
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://admision.unmsm.edu.pe"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"

PROCESOS = {  # proceso -> sitio
    "2024-1": "Website20241",
    "2024-2": "Website20242",
    "2025-1": "Website20251",
    "2026-1": "Website20261",
    "2026-2": "Website20262",
    "2027-1": "Website20271",
}

RE_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
RE_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
RE_SCORE_ATTR = re.compile(r'data-score="([\d.]+)"')
RE_LINK = re.compile(r'href="([^"]+\.html)"[^>]*>([^<]+)<')


def fetch(path, cache_dir, delay):
    """GET {BASE}/{path} con caché en disco."""
    cached = cache_dir / path.replace("/", "__")
    if cached.exists():
        return cached.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(f"{BASE}/{path}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(body, encoding="utf-8")
    time.sleep(delay)
    return body


def parse_rows(page_html):
    """Devuelve (postulantes, ingresantes, notas_todas, notas_ingresantes)."""
    pos = ing = 0
    notas, notas_ing = [], []
    for row in RE_ROW.findall(page_html):
        cells = RE_CELL.findall(row)
        if len(cells) < 6 or "Apellidos" in row:  # cabecera
            continue
        pos += 1
        m = RE_SCORE_ATTR.search(row)
        if m:
            nota = float(m.group(1))
        else:
            raw = re.sub(r"<[^>]+>", "", cells[3]).replace("&nbsp;", "").strip()
            nota = float(raw) if re.fullmatch(r"\d+(\.\d+)?", raw) else None
        alcanzo = "ALCANZ" in cells[5].upper()
        if nota is not None:
            notas.append(nota)
            if alcanzo:
                notas_ing.append(nota)
        if alcanzo:
            ing += 1
    return pos, ing, notas, notas_ing


def clean_name(s):
    return re.sub(r"\s+", " ", htmllib.unescape(s)).strip().upper()


def scrape_proceso(proceso, sitio, cache_dir, delay):
    index = fetch(f"{sitio}/", cache_dir, delay)
    modalidades = {}  # nombre_modalidad -> {escuela -> agregados}
    mod_links = [(h, t) for h, t in RE_LINK.findall(index) if "index" not in h]
    for mod_href, mod_name in mod_links:
        mod_name = clean_name(mod_name)
        mod_href = mod_href.lstrip("./")
        mod_html = fetch(f"{sitio}/{mod_href}", cache_dir, delay)
        # base de las rutas de escuela: relativas a la página de modalidad
        mod_dir = mod_href.rsplit("/", 1)[0] + "/" if "/" in mod_href else ""
        escuelas = {}
        for esc_href, esc_name in RE_LINK.findall(mod_html):
            if "index" in esc_href or esc_href.endswith((f"{mod_href}",)):
                continue
            if not esc_href.endswith(("0.html", "results.html")):
                continue
            esc_name = clean_name(esc_name)
            page = fetch(f"{sitio}/{mod_dir}{esc_href.lstrip('./')}", cache_dir, delay)
            pos, ing, notas, notas_ing = parse_rows(page)
            if not pos:
                continue
            escuelas[esc_name] = {
                "postulantes": pos,
                "ingresantes": ing,
                "nota_max": round(max(notas), 2) if notas else None,
                "nota_cierre": round(min(notas_ing), 2) if notas_ing else None,
            }
        if escuelas:
            modalidades[mod_name] = dict(sorted(escuelas.items()))
        print(f"  {proceso} {mod_name[:50]}: {len(escuelas)} escuelas", file=sys.stderr)
    return modalidades


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procesos", nargs="*", default=list(PROCESOS),
                    help="procesos a scrapear (default: todos)")
    ap.add_argument("--cache-dir", default=str(ROOT / ".cache_scrape"))
    ap.add_argument("--delay", type=float, default=0.15,
                    help="pausa entre requests no cacheados (s)")
    args = ap.parse_args()
    cache_dir = pathlib.Path(args.cache_dir)

    out_path = ROOT / "historico" / "unmsm_historico.json"
    data = json.loads(out_path.read_text()) if out_path.exists() else {}
    procesos = data.setdefault("procesos", {})

    for proceso in args.procesos:
        sitio = PROCESOS[proceso]
        print(f"== {proceso} ({sitio}) ==", file=sys.stderr)
        modalidades = scrape_proceso(proceso, sitio, cache_dir, args.delay)
        tot_pos = sum(e["postulantes"] for m in modalidades.values() for e in m.values())
        tot_ing = sum(e["ingresantes"] for m in modalidades.values() for e in m.values())
        procesos[proceso] = {
            "fuente": f"{BASE}/{sitio}/",
            "totales": {"postulantes": tot_pos, "ingresantes": tot_ing},
            "por_modalidad": modalidades,
        }
        print(f"  TOTAL {proceso}: {tot_pos} postulantes, {tot_ing} ingresantes",
              file=sys.stderr)

    data["generado_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["nota"] = ("Agregados calculados de las páginas públicas de resultados de la OCA-UNMSM. "
                    "Sin datos personales. nota_cierre = mínima entre ingresantes; "
                    "nota_max = máxima observada. Escala sobre 2,000 puntos.")
    data["procesos"] = dict(sorted(procesos.items()))
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"OK -> {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
