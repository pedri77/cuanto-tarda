#!/usr/bin/env python3
"""Descarga las series estadísticas del CGPJ (actividad judicial) y población del INE.

Caché en raw/: si el fichero ya existe no se vuelve a descargar.
Sin claves, sin servidor. Ejecutar: python3 scripts/cgpj_fetch.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "raw"
RAW.mkdir(exist_ok=True)

# Página de origen de todas las series:
# https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estudios-e-Informes/Informes-por-territorios-sobre-la-actividad-de-los-organos-judiciales/Informes-por-territorios-sobre-la-actividad-de-los-organos-judiciales
CGPJ_BASE = (
    "https://www.poderjudicial.es/stfls/ESTADISTICA/FICHEROS/"
    "3002%20Series%20estadisticas"
)

CGPJ_FILES = [
    "Series Asuntos.xlsx",
    "Series Asuntos por Provincias.xlsx",
    "Series Tasas de Congestion.xlsx",
    "Series Tasas de Congestion por Provincias.xlsx",
    "Series Tasas de Resolucion.xlsx",
    "Series Tasas de Resolucion por Provincias.xlsx",
    "Series Tasas de Pendencia.xlsx",
    "Series Tasas de Pendencia por Provincias.xlsx",
    "Series Tasa Litigiosidad.xlsx",
    "Series Tasa Litigiosidad por Provincias.xlsx",
    "Evolución Asuntos en trámite final Período Total nacional.xlsx",
]

# INE Tempus (wstempus). Tabla 31304 = Cifras de población, Total Nacional/CCAA/Provincias,
# ambos sexos, total de edad, a 1 de enero. Los códigos por territorio se guardaron en
# raw/ine_series_codigos.json (extraídos de la tabla; si falta el fichero se regenera).
INE_TABLA_POBLACION = 31304
INE_BASE = "https://servicios.ine.es/wstempus/js/ES"


def fetch(url: str, dest: Path, binary: bool = True) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[cache] {dest.name}")
        return
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "cuanto-tarda/1.0"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())
    dt = time.time() - t0
    print(f"[ok] {dest.name}: {dest.stat().st_size / 1024:.0f} KB en {dt:.1f}s")


def ine_extract_codes() -> dict:
    """Extrae el código de serie INE por territorio (regenerable, ~217 MB, ~35 s)."""
    codes_path = RAW / "ine_series_codigos.json"
    if codes_path.exists():
        return json.loads(codes_path.read_text())
    url = f"{INE_BASE}/DATOS_TABLA/{INE_TABLA_POBLACION}?det=0&tip=AM"
    print(f"[descarga] tabla INE {INE_TABLA_POBLACION} (pesada: ~217 MB)")
    req = urllib.request.Request(url, headers={"User-Agent": "cuanto-tarda/1.0"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    codes = {}
    for serie in data:
        meta = {m["T3_Variable"]: m["Nombre"] for m in serie["MetaData"]}
        if meta.get("Sexo") != "Ambos sexos" or meta.get("Totales de edad") != "Total":
            continue
        if meta.get("Conceptos demográficos", "Población") != "Población":
            continue
        if meta.get("Tipo de dato") != "Número":
            continue
        for var in ("Total Nacional", "Comunidades y Ciudades Autónomas", "Provincias"):
            if var in meta:
                codes[meta[var]] = serie["COD"]
                break
    codes_path.write_text(json.dumps(codes, ensure_ascii=False, indent=1))
    print(f"[ok] {len(codes)} códigos de serie INE -> {codes_path.name}")
    return codes


def ine_population(codes: dict) -> None:
    """Descarga cada serie de población por territorio (solo lo necesario, ~KB cada una)."""
    dest = RAW / "ine_poblacion.json"
    if dest.exists():
        print("[cache] ine_poblacion.json")
        return
    out = {}
    for nombre, cod in sorted(codes.items()):
        url = f"{INE_BASE}/DATOS_SERIE/{cod}?nult=120"
        req = urllib.request.Request(url, headers={"User-Agent": "cuanto-tarda/1.0"})
        with urllib.request.urlopen(req) as r:
            serie = json.load(r)
        puntos = []
        for d in serie["Data"]:
            # Fecha en ms epoch (hora peninsular); nos quedamos el 1 de enero de cada año.
            # La serie reciente tiene más puntos por año, por eso nult=120.
            fecha = time.gmtime(d["Fecha"] / 1000 + 3600)  # +1h: hora peninsular
            if fecha.tm_mon == 1 and fecha.tm_mday == 1:
                puntos.append(
                    {
                        "anyo": d["Anyo"],
                        "valor": d["Valor"],
                        "tipo_dato": "Provisional" if d.get("FK_TipoDato") == 2 else "Definitivo",
                    }
                )
        out[nombre] = puntos
        time.sleep(0.1)
    dest.write_text(json.dumps(out, ensure_ascii=False))
    print(f"[ok] población INE de {len(out)} territorios -> {dest.name}")


def main() -> int:
    for name in CGPJ_FILES:
        enc = urllib.parse.quote(name)
        dest = RAW / name.replace(" ", "_")
        fetch(f"{CGPJ_BASE}/{enc}", dest)
    codes = ine_extract_codes()
    ine_population(codes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
