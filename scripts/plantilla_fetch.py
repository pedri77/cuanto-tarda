#!/usr/bin/env python3
"""plantilla_fetch.py — descarga las fuentes de plantilla judicial (capacidad).

Fuentes:
 1. CGPJ «La Justicia dato a dato» (anual, 2003-2025, PDF): jueces en activo,
    plazas orgánicas, plantilla de fiscales, LAJ y funcionarios.
 2. CGPJ «Memoria anual» (capítulo Panorámica de la Justicia).
 3. Eurostat `crim_just_job` (JSON-stat2): jueces profesionales por 100.000 hab.

Sin claves. Caché en raw/plantillas/: si el fichero existe y no está vacío,
no se vuelve a descargar.
"""
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.normpath(os.path.join(HERE, "..", "raw", "plantillas"))
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) cuantotarda/1.0"}

# (fichero local, URL) — URLs literales de la página oficial del CGPJ
# https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estadistica-por-temas/
#   Actividad-de-los-organos-judiciales/Juzgados-y-Tribunales/Justicia-Dato-a-Dato
PJ = "https://www.poderjudicial.es/stfls"
DAD_NEW = f"{PJ}/ESTADISTICA/FICHEROS/JusticaDatoaDato"

DAD_NEW2 = f"{PJ}/ESTADISTICA%20JUDICIAL%20NUEVO/FICHEROS/JusticaDatoaDato/Datos%20Anteriores"
DAD_OLD = f"{PJ}/ESTADISTICA/FICHEROS/JusticaDatoaDato/Datos%20Anteriores"
DAD_2325 = f"{PJ}/CGPJ/ESTAD%C3%8DSTICA/FICHEROS"

TARGETS = []
for year in range(2003, 2026):
    if year == 2024:
        # La página oficial no lista edición 2024 (salta de 2023 a 2025) y las
        # dos rutas candidatas devuelven 404 (comprobado 2026-10-01).
        continue
    fn = f"dato_a_dato_{year}.pdf"
    if year == 2025:
        urls = [f"{PJ}/ESTADISTICA/FICHEROS/JusticaDatoaDato/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%202025.pdf"]
    elif year >= 2023:
        urls = [f"{DAD_2325}/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%20{year}.pdf",
                f"{DAD_NEW}/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%20{year}.pdf"]
    elif year >= 2015:
        urls = [
            f"{DAD_NEW}/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%20{year}.pdf",
            f"{DAD_NEW}/Justicia%20Dato%20a%20Dato%20{year}.pdf",
            f"{DAD_NEW}/Justicia%20Dato%20a%20Dato%20{year}%20(v6).pdf",
            f"{DAD_NEW}/Datos%20Anteriores/Justicia%20Dato%20a%20Dato%20{year}.pdf",
            f"{DAD_NEW}/Datos%20Anteriores/Justicia%20Dato%20a%20Dato%20{year}%20(v6).pdf",
            f"{DAD_NEW}/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%20{year}%20(v6).pdf",
            f"{DAD_NEW}/Datos%20Anteriores/Justicia%20Dato%20a%20Dato%20-%20A%C3%B1o%20{year}.pdf",
            f"{DAD_NEW}/Datos%20Anteriores/Justicia%20Dato%20a%20Dato%20A%C3%B1o%20{year}.pdf",
        ]
    elif year == 2014:
        urls = [f"{DAD_NEW2}/Justicia%20Dato%20a%20Dato%20A%C3%B1o%202014.pdf"]
    else:
        urls = [f"{DAD_NEW2}/Justicia%20Dato%20a%20Dato%20A%C3%B1o%20{year}.pdf"]
    TARGETS.append((fn, urls))

TARGETS += [
    ("cgpj_memoria2025_panoramica.pdf",
     [f"{PJ}/CGPJ/SECRETAR%C3%8DA%20GENERAL/MEMORIA%20ANUAL/FICHERO/"
      "20250905MemoriaCGPJ2025_07PanoramicaJusticia.pdf"]),
    ("cgpj_memoria2025_anexo_necesidades.pdf",
     [f"{PJ}/CGPJ/SECRETAR%C3%8DA%20GENERAL/MEMORIA%20ANUAL/FICHERO/"
      "20250905MemoriaCGPJ2025_08AnexoRelacNecesid.pdf"]),
    ("cgpj_nota_350_jueces.html",
     ["https://www.poderjudicial.es/cgpj/es/Poder-Judicial/En-Portada/"
      "El-CGPJ-considera-necesario-el-ingreso-de-350-nuevos-jueces-al-ano-hasta-2033-"
      "para-cubrir-las-vacantes-por-fallecimiento--jubilacion-y-renuncia-que-se-produzcan"]),
    ("mj_2874.html",
     ["https://www.mjusticia.gob.es/es/institucional/gabinete-comunicacion/noticias-ministerio/"
      "Justicia-convoca-2874-plazas-para-diferentes-cuerpos-de-la-Administracion-de-Justicia"]),
    ("rcp_epsap_enero_2026.pdf",
     ["https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/2026_01/"
      "revision-agosto-2026/EPSAP_Enero_2026%20.pdf"]),
    ("eu_justice_scoreboard_2026.pdf",
     ["https://commission.europa.eu/document/download/d1367f58-9eed-4ebd-8eb3-68646b7c7ddc_en"
      "?filename=2026_eu_justice_scoreboard.PDF"]),
    ("eurostat_judges_full.json",
     ["https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
      "crim_just_job?format=JSON&lang=EN"]),
    # CEPEJ country fiche Spain (2024 data): rm.coe.int devuelve 403 a clientes
    # sin JavaScript (Cloudflare). Se descargó una vez con un navegador headless
    # y se guarda en raw/plantillas/cepej_spain_fiche_2024data.pdf; aquí solo se
    # intenta por si el bloqueo desaparece.
    ("cepej_spain_fiche_2024data.pdf",
     ["https://rm.coe.int/spain-country-fiche/48802c1531"]),
]


def to_text(fname):
    """pdftotext -layout sobre cada PDF (idempotente)."""
    src = os.path.join(RAW, fname)
    dst = src[:-4] + ".txt"
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return
    subprocess.run(["pdftotext", "-layout", src, dst], check=False)


def fetch(fname, urls):
    path = os.path.join(RAW, fname)
    if os.path.exists(path) and os.path.getsize(path) > 1024:
        return ("cache", fname)
    last = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            ok_pdf = b"%PDF" in data[:1024]
            ok_other = fname.endswith((".json", ".html")) and b"<title>CGPJ. - 404" not in data
            if len(data) > 1024 and (ok_pdf or ok_other):
                with open(path, "wb") as f:
                    f.write(data)
                return ("ok", fname)
            last = f"contenido no válido ({len(data)} bytes)"
        except Exception as e:  # noqa: BLE001
            last = getattr(e, "code", e)
    return (("error", f"{fname}: {last}"))


def main():
    os.makedirs(RAW, exist_ok=True)
    fails = 0
    for fname, urls in TARGETS:
        status, info = fetch(fname, urls)
        if status == "error":
            fails += 1
        print(f"{status:5} {info}")
        if status != "error" and fname.endswith(".pdf"):
            to_text(fname)
    print(f"\n{fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
