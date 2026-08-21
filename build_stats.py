#!/usr/bin/env python3
"""Genera data/stats.json con estadísticas de admisión UNMSM (San Marcos).

Fuente: dataset oficial AGREGADO de la UNMSM en la Plataforma Nacional de
Datos Abiertos (datosabiertos.gob.pe), "Proceso de admisión de pregrado
2026-1": vacantes, postulantes, ingresantes y nota máx/mín por escuela
profesional y modalidad. No contiene datos personales.

Escala: examen UNMSM sobre 2,000 puntos (máx observado ~1,679).
"""
import csv
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CSV = ROOT / "historico" / "unmsm_admision_2026_1.csv"

MODALIDAD_CORTA = {
    "EDUCACIÓN BÁSICA REGULAR (EBR) Y EDUCACIÓN BÁSICA ALTERNATIVA (EBA)": "EBR/EBA (examen ordinario)",
    "CENTRO PREUNIVERSITARIO": "Pre-San Marcos (CEPREUNMSM)",
}


def parse_nota(s):
    """El CSV codifica las notas quitando el punto decimal y agrupando TODOS los
    dígitos con puntos de miles: '1.679.125' = 1679.125, '11.112.135' = 1111.2135,
    '8.535.228' = 853.5228; también hay decimales normales ('1622.34') y enteros
    ('1469'). Estrategia: si el valor literal cae en el rango plausible de una
    nota UNMSM [300, 2000) se usa tal cual; si no, se reconstruye desde la tira
    de dígitos probando cuántos decimales dejan la parte entera en rango."""
    s = (s or "").strip()
    if not s:
        return None
    if s.count(".") <= 1:
        try:
            v = float(s)
            if 300 <= v < 2000:
                return round(v, 2)
        except ValueError:
            pass
    digits = s.replace(".", "")
    if not digits.isdigit():
        return None
    for dec in (3, 4, 2, 5, 1, 0):
        if dec >= len(digits):
            continue
        ent = digits[:len(digits) - dec]
        cand = int(ent) + (int(digits[len(digits) - dec:]) / 10**dec if dec else 0)
        if 300 <= cand < 2000:
            return round(cand, 2)
    return None


def main():
    escuelas = {}
    modalidades = {}
    tot = {"vacantes": 0, "postulantes": 0, "ingresantes": 0}

    with open(CSV, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            esc = (r.get("Nomb_Escuela") or "").strip().upper()
            mod = MODALIDAD_CORTA.get((r.get("Nomb. Modalidad") or "").strip(),
                                      (r.get("Nomb. Modalidad") or "").strip())
            if not esc:
                continue
            vac = int(r.get("Cant. Vacantes") or 0)
            pos = int(r.get("Postulantes") or 0)
            ing = int(r.get("Ingresantes") or 0)
            nmax = parse_nota(r.get("Nota_Maxima"))
            nmin = parse_nota(r.get("Nota_Minima"))

            e = escuelas.setdefault(esc, {"vacantes": 0, "postulantes": 0, "ingresantes": 0,
                                          "por_modalidad": {}})
            e["vacantes"] += vac
            e["postulantes"] += pos
            e["ingresantes"] += ing
            e["por_modalidad"][mod] = {"vacantes": vac, "postulantes": pos, "ingresantes": ing,
                                       "nota_max": nmax, "nota_min": nmin}

            m = modalidades.setdefault(mod, {"vacantes": 0, "postulantes": 0, "ingresantes": 0})
            m["vacantes"] += vac
            m["postulantes"] += pos
            m["ingresantes"] += ing

            tot["vacantes"] += vac
            tot["postulantes"] += pos
            tot["ingresantes"] += ing

    # Validaciones básicas
    notas = [v["nota_min"] for e in escuelas.values() for v in e["por_modalidad"].values() if v["nota_min"]]
    notas += [v["nota_max"] for e in escuelas.values() for v in e["por_modalidad"].values() if v["nota_max"]]
    assert notas and 300 < min(notas) and max(notas) < 2000, f"notas fuera de rango: {min(notas)}–{max(notas)}"
    malas = [(e, m) for e, d in escuelas.items() for m, v in d["por_modalidad"].items()
             if v["nota_min"] and v["nota_max"] and v["nota_min"] > v["nota_max"]]
    assert not malas, f"nota_min > nota_max en: {malas[:3]}"

    stats = {
        "generado_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "universidad": "Universidad Nacional Mayor de San Marcos (UNMSM)",
        "fuente": "Dataset oficial agregado UNMSM en la Plataforma Nacional de Datos Abiertos (datosabiertos.gob.pe): 'Proceso de admisión de pregrado 2026-1'. Sin datos personales.",
        "escala": {"max_teorico": 2000, "max_observado": round(max(notas), 2),
                   "nota": "Puntaje del examen UNMSM sobre 2,000; sin conversión vigesimal oficial."},
        "proceso": "2026-1",
        "totales": tot,
        "por_modalidad": modalidades,
        "por_escuela": {k: escuelas[k] for k in sorted(escuelas)},
    }

    out = ROOT / "data" / "stats.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(stats, ensure_ascii=False, indent=1))
    print(f"OK -> {out} ({out.stat().st_size} bytes)")
    print(f"  {len(escuelas)} escuelas | totales: {tot} | notas {min(notas)}–{max(notas)}")


if __name__ == "__main__":
    main()
