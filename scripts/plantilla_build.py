#!/usr/bin/env python3
"""plantilla_build.py — construye data/plantilla_*.json desde raw/plantillas/.

Fuentes parseadas:
 - raw/plantillas/dato_a_dato_{year}.txt  (pdftotext -layout del PDF
   «La Justicia dato a dato» del CGPJ, años 2003-2023 y 2025).
 - raw/plantillas/eurostat_judges_full.json (Eurostat crim_just_job).
 - data/nacional_anual.json (asuntos ingresados, ya existente).

Salidas (nuevas, no toca nada existente):
 - data/plantilla_series.json : plantillas por año (jueces, fiscales, LAJ,
   funcionarios) con meta por campo.
 - data/plantilla_europa.json : jueces profesionales por 100.000 hab.
   (Eurostat) España y países de referencia.
 - data/plantilla_ratios.json : asuntos ingresados por juez (cruce con la
   demanda ya medida) y jueces por 100.000 hab.
 - data/plantilla_sources.json : catálogo de fuentes.

Extracción best-effort con verificación: cada cifra lleva la línea del PDF
de la que procede (contexto) para auditoría manual.
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "raw", "plantillas")
DATA = os.path.join(ROOT, "data")

NUM = re.compile(r"\d[\d.]*,\d+|\d[\d.]*")  # números españoles con puntos


def numbers(line):
    out = []
    for tok in NUM.findall(line):
        try:
            out.append(float(tok.replace(".", "")))
        except ValueError:
            pass
    return out


def is_int(n):
    return abs(n - round(n)) < 1e-6


def to_es(n):
    return f"{round(n):,}".replace(",", ".")


def find_total(lines, start, window=90, also_lower=True):
    """Busca la primera fila 'TOTAL'/'Total' tras `start` que lleve números."""
    for i in range(start, min(len(lines), start + window)):
        s = lines[i].strip()
        if re.match(r"^TOTAL\b", s) or (also_lower and re.match(r"^Total\b", s)):
            nums = [n for n in numbers(s) if n >= 10]  # descarta ceros/índices
            if nums:
                return i, nums, s
    return None, None, None

def grab_total(lines, header_pat, window=90):
    """Total nacional de una tabla: última columna si hay columna TOTAL,
    suma de la fila si solo hay desglose por cuerpos. Si la tabla no trae
    fila Total (ed. 2004), suma la última columna de las filas territoriales."""
    h = section_line(lines, header_pat)
    if h is None:
        return None
    end = h + window
    for j in range(h + 1, min(len(lines), h + window)):
        if re.match(r"^\s*(\d+\s+)?Fuente:", lines[j]):
            end = j
            break
    i, nums, raw = find_total(lines, h + 1, end - h)
    if nums:
        has_total_col = any(re.search(r"total", lines[j], re.I)
                            for j in range(h + 1, i))
        val = nums[-1] if has_total_col else sum(nums)
        return {"valor": val, "linea_pdf": i + 1, "columna_total": has_total_col,
                "texto": re.sub(r"\s+", " ", raw)[:120]}
    rows = []
    for j in range(h + 1, end):
        s = lines[j].strip()
        if re.match(r"^[A-ZÁÉÍÓÚa-záéíóúñ]", s) and len(numbers(s)) >= 3:
            rows.append(numbers(s)[-1])
    if len(rows) >= 15:
        return {"valor": sum(rows), "linea_pdf": h + 1,
                "texto": f"sin fila Total: suma de la última columna de {len(rows)} filas"}
    return None


def section_line(lines, pattern, after=0):
    rx = re.compile(pattern, re.I)
    for i in range(after, len(lines)):
        s = lines[i]
        if rx.search(s) and "..." not in s and "…" not in s \
                and not re.match(r"^\s*\d+\s+\S", s) \
                and not any("...." in x or "……" in x for x in lines[i - 2:i + 3]):  # excluye índice
            return i
    return None


def parse_dato_a_dato(txt_path):
    """Extrae los totales nacionales de un año del informe."""
    lines = open(txt_path, encoding="utf-8", errors="replace").read().splitlines()
    out = {}

    # 1. Plazas judiciales constituidas (plantilla orgánica de jueces, por TSJ,
    #    incluidos órganos centrales). Ed. 2003: tabla por tipo de órgano.
    #    Ed. 2004: solo por TSJ, sin TS/AN y sin fila Total -> clave aparte.
    out["plazas_jueces_constituidas"] = grab_total(
        lines,
        r"(N[UÚ]MERO DE JUECES Y MAGISTRADOS|Número de jueces y magistrados)\s*\d*\s*$|"
        r"N[UÚ]MERO DE JUECES Y MAGISTRADOS \d|"
        r"Número de Magistrados y Jueces por tipo de órgano")
    if not out["plazas_jueces_constituidas"]:
        out["plazas_jueces_tsj_sin_centrales"] = grab_total(
            lines, r"Número de jueces y magistrados en los Tribunales")

    # 2. Jueces y magistrados en activo (pirámide de edad): la fila Total trae
    #    tramos de edad + total + edad media + antigüedad; el total es el mayor
    #    entero de la fila. Ed. 2006-2008: la pirámide es solo gráfico, sin tabla.
    h = section_line(lines, r"JUECES Y MAGISTRADOS EN ACTIVO|ACTIVO A 1 DE ENERO|"
                            r"en activo a 1 de enero|magistrados en activo\s*$")
    if h is not None:
        for i in range(h + 1, min(len(lines), h + 40)):
            s = lines[i].strip()
            if re.search(r"Juzgados de Paz", s, re.I):
                break  # siguiente sección: la pirámide era solo gráfico
            if re.match(r"^(TOTAL|Total)\b", s):
                ints = [float(t.replace(".", "")) for t in NUM.findall(s) if "," not in t]
                if ints and max(ints) >= 1000:
                    out["jueces_en_activo"] = {
                        "valor": max(ints), "linea_pdf": i + 1,
                        "texto": re.sub(r"\s+", " ", s)[:120]}
                    break

    # 3. Fiscales (plantilla orgánica del Ministerio Fiscal)
    out["fiscales_plantilla_organica"] = grab_total(
        lines, r"PLANTILLA ORG[AÁ]NICA DEL MINISTERIO FISCAL|Plantilla orgánica de Fiscales")

    # 4. Secretarios judiciales / LAJ (plantilla y, desde 2014, efectivos)
    h = section_line(lines, r"PLANTILLA DE (LETRADOS( DE LA)? ADMINISTRACI|SECRETARIOS JUDICIALES)")
    if h is not None:
        cuerpo = "laj" if "LETRADO" in lines[h].upper() else "secretarios"
        i, nums, raw = find_total(lines, h + 1, 40)
        if nums:
            d = {"tipo": cuerpo, "linea_pdf": i + 1,
                 "texto": re.sub(r"\s+", " ", raw)[:120], "plantilla": nums[0],
                 "efectivos": nums[1] if len(nums) >= 2 else None}
            out["cuerpo_secretarial"] = d

    # 5. Funcionarios judiciales en órganos judiciales (cuerpos generales:
    #    Gestión + Tramitación + Auxilio). Hasta 2015 la tabla trae además
    #    médicos forenses (1ª columna) y no tiene columna Total: se suman solo
    #    las tres últimas columnas. Desde 2016 trae Total propio.
    fj = grab_total(lines, r"[Pp]lantilla de [Ff]uncionarios [Jj]udiciales\s*\d*\s*$")
    if fj:
        nums = [n for n in numbers(fj["texto"]) if n >= 10]
        if len(nums) == 4 and not fj["columna_total"]:
            # 4 columnas sin total: forenses + 3 cuerpos
            fj["valor"] = sum(nums[-3:])
            fj["nota"] = "suma Gestión+Tramitación+Auxilio; excluye la columna de médicos forenses"
        fuente = ""
        for j in range(fj["linea_pdf"], min(len(lines), fj["linea_pdf"] + 8)):
            if "Fuente" in lines[j]:
                fuente = re.sub(r"\s+", " ", lines[j] + " " + lines[j + 1]).strip()
                break
        fj["fuente_pdf"] = fuente[:200]
    out["funcionarios_judiciales"] = fj
    # Desde 2016 el informe desglosa otras sedes en tablas aparte
    out["funcionarios_en_fiscalias"] = grab_total(
        lines, r"PLANTILLA DE FUNCIONARIOS JUDICIALES EN FISCAL[IÍ]AS|^\s*en Fiscal[ií]as\s*\d*\s*$")
    out["funcionarios_en_juzgados_de_paz"] = grab_total(
        lines, r"PLANTILLA DE FUNCIONARIOS JUDICIALES EN JUZGADOS Y", window=45)
    return out


def load_eurostat():
    d = json.load(open(os.path.join(RAW, "eurostat_judges_full.json")))
    dims, size = d["id"], d["size"]
    idx, vals = d["dimension"], d["value"]

    def get(**coord):
        i = 0
        for dim in dims:
            c = idx[dim]["category"]["index"].get(coord.get(dim))
            if c is None:
                return None
            i = i * size[dims.index(dim)] + c
        return vals.get(str(i))

    out = {}
    for geo in ["ES", "DE", "FR", "IT", "PT", "AT", "BE", "NL", "EL", "EU15"]:
        row = {}
        for y in range(2012, 2025):
            v = get(freq="A", isco08="OC2612A", sex="T", unit="P_HTHAB",
                    geo=geo, time=str(y))
            if v is not None:
                row[str(y)] = v
        if row:
            out[geo] = row
    return out


DAD_URL = ("https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estadistica-por-temas/"
           "Actividad-de-los-organos-judiciales/Juzgados-y-Tribunales/Justicia-Dato-a-Dato")

FIELD_META = {
    "plazas_jueces_constituidas": {
        "label": "Plazas de juez/magistrado constituidas (plantilla orgánica)",
        "source": "CGPJ, «La Justicia dato a dato», tabla «Número de jueces y magistrados» (por TSJ, incluye TS y AN)",
        "unit": "plazas a 1 de enero", "url": DAD_URL,
        "caveat": "Plazas orgánicas, cubiertas o no. Ed. 2015 incluye 395 jueces en expectativa de destino (rompe la serie; la propia fuente lo advierte). Ed. 2003: tabla por tipo de órgano."},
    "plazas_jueces_tsj_sin_centrales": {
        "label": "Jueces y magistrados en los TSJ (sin Tribunal Supremo ni Audiencia Nacional)",
        "source": "CGPJ, «La Justicia dato a dato» 2004, tabla por TSJ sin fila total (suma de la última columna)",
        "unit": "plazas a 1 de enero", "url": DAD_URL,
        "caveat": "No comparable con plazas_jueces_constituidas: faltan los órganos centrales."},
    "jueces_en_activo": {
        "label": "Jueces y magistrados en activo (carrera judicial)",
        "source": "CGPJ, «La Justicia dato a dato», tabla «Pirámide de edad de los jueces y magistrados en activo» (fila Total)",
        "unit": "personas a 1 de enero", "url": DAD_URL,
        "caveat": "Miembros de la carrera judicial en activo; no incluye jueces sustitutos ni magistrados suplentes. Las ediciones 2014 y 2015 publican la misma tabla (5.219): hallazgo de la fuente, no del extractor."},
    "fiscales_plantilla_organica": {
        "label": "Plantilla orgánica del Ministerio Fiscal",
        "source": "Fiscalía General del Estado, vía CGPJ «La Justicia dato a dato»",
        "unit": "plazas a 1 de enero", "url": DAD_URL,
        "caveat": "Plantilla orgánica (plazas), no efectivos. Ed. 2003-2004: suma Fiscal de Sala + Fiscal + Abogado Fiscal."},
    "cuerpo_secretarial_plantilla": {
        "label": "Secretarios judiciales (hasta 2015) / Letrados de la Administración de Justicia: plantilla",
        "source": "Ministerio de Justicia, vía CGPJ «La Justicia dato a dato»",
        "unit": "plazas a 1 de enero", "url": DAD_URL,
        "caveat": "Mismo cuerpo, renombrado por la LO 7/2015."},
    "cuerpo_secretarial_efectivos": {
        "label": "Secretarios judiciales / LAJ: efectivos (plazas cubiertas)",
        "source": "Ministerio de Justicia, vía CGPJ «La Justicia dato a dato»",
        "unit": "personas a 1 de enero", "url": DAD_URL,
        "caveat": "Solo publicado desde la edición 2014. Único cuerpo con plantilla y efectivos en la misma tabla."},
    "funcionarios_judiciales": {
        "label": "Cuerpos generales (Gestión + Tramitación + Auxilio)",
        "source": "Ministerio de Justicia (ed. 2005-2007, 2010-2025) / Estadística Judicial CGPJ (ed. 2008-2009), vía «La Justicia dato a dato»",
        "unit": "plazas a 1 de enero", "url": DAD_URL,
        "caveat": "Plantilla orgánica, no efectivos. Cubre todo el territorio (incluidas CCAA transferidas) porque el Ministerio consolida las plantillas. CAMBIO DE CRITERIO: hasta la ed. 2015 la tabla es única e incluye todas las sedes (órganos judiciales, fiscalías, juzgados de paz, registros civiles, IML, órganos centrales); desde la ed. 2016 esta cifra es SOLO órganos judiciales, decanatos y servicios comunes, y el resto va en tablas aparte (funcionarios_en_fiscalias, funcionarios_en_juzgados_de_paz…). Por eso baja de ~45.000 (2015) a ~39.000 (2016). Ed. 2008-2009 cambia de fuente (CGPJ, solo órganos judiciales): tampoco comparable. Hasta 2015 la tabla trae médicos forenses en una columna aparte que aquí se excluye."},
    "funcionarios_en_fiscalias": {
        "label": "Cuerpos generales destinados en fiscalías",
        "source": "Ministerio de Justicia, vía CGPJ «La Justicia dato a dato» (desde ed. 2016)",
        "unit": "plazas a 1 de enero", "url": DAD_URL, "caveat": "Tabla aparte solo desde 2016."},
    "funcionarios_en_juzgados_de_paz": {
        "label": "Cuerpos generales en juzgados y agrupaciones de juzgados de paz",
        "source": "Ministerio de Justicia, vía CGPJ «La Justicia dato a dato» (desde ed. 2016)",
        "unit": "plazas a 1 de enero", "url": DAD_URL, "caveat": "Tabla aparte solo desde 2016."},
}


def main():
    os.makedirs(DATA, exist_ok=True)
    series, ctx = {}, {}
    for path in sorted(glob.glob(os.path.join(RAW, "dato_a_dato_*.txt"))):
        year = str(int(re.search(r"(\d{4})", os.path.basename(path)).group(1)))
        parsed = {k: v for k, v in parse_dato_a_dato(path).items() if v}
        row = {}
        for k, v in parsed.items():
            if k == "cuerpo_secretarial":
                row["cuerpo_secretarial_tipo"] = v["tipo"]
                row["cuerpo_secretarial_plantilla"] = v["plantilla"]
                if v["efectivos"] is not None:
                    row["cuerpo_secretarial_efectivos"] = v["efectivos"]
            else:
                row[k] = v["valor"]
        series[year] = row
        ctx[year] = parsed

    descartes = {
        "2024": "No existe edición «Justicia dato a dato» 2024 (HTTP 404 en las dos rutas del portal; la página oficial salta de 2023 a 2025).",
        "2001-2002": "La serie «Justicia dato a dato» empieza en 2003; no hay denominador de jueces para los asuntos de 2001-2002.",
        "2004 plazas": "La edición 2004 solo trae la tabla por TSJ (sin TS/AN) y sin fila Total: se guarda en plazas_jueces_tsj_sin_centrales y no se usa en ratios.",
        "2008-2009 funcionarios": "Cambio de fuente (CGPJ en vez de Ministerio, solo órganos judiciales): se guarda pero se marca como no comparable.",
        "2015 plazas": "Incluye 395 jueces en expectativa de destino como refuerzo (la fuente lo advierte): no comparable con 2014 ni 2016.",
    }
    with open(os.path.join(DATA, "plantilla_series.json"), "w") as f:
        json.dump({"meta": {
            "source": "CGPJ, «La Justicia dato a dato» (ediciones 2003-2023 y 2025)",
            "url": DAD_URL, "period": "datos a 1 de enero de cada año",
            "unit": "personas o plazas (totales nacionales)",
            "campos": FIELD_META, "descartes": descartes,
            "extraido_con": "scripts/plantilla_fetch.py + pdftotext -layout + scripts/plantilla_build.py",
        }, "por_anio": series, "extraccion_contexto": ctx}, f, ensure_ascii=False, indent=1)

    eu = load_eurostat()
    with open(os.path.join(DATA, "plantilla_europa.json"), "w") as f:
        json.dump({"meta": {
            "source": "Eurostat, dataset crim_just_job «Personnel in the criminal justice system by sex», ISCO-08 OC2612A «Professional judges», unidad P_HTHAB",
            "url": "https://ec.europa.eu/eurostat/databrowser/view/crim_just_job/default/table?lang=en",
            "api": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/crim_just_job?format=JSON&lang=EN",
            "period": "2012-2024 (a 31 de diciembre)",
            "unit": "jueces profesionales por 100.000 habitantes",
            "caveat": "Definición Eurostat/ONU (UNODC) de 'juez profesional': España reporta 6,2 en 2024 mientras el CGPJ publica 11,9 plazas por 100.000 hab. No son la misma magnitud: Eurostat la recoge en el cuestionario de justicia PENAL (UN-CTS). Se publica solo para comparar entre países bajo la misma definición, nunca mezclada con la serie CGPJ. Austria y Chequia solo incluyen jueces penales; EU27 no viene como agregado en el dataset (Eurostat lo calculó ad hoc para su nota de 17/07/2026: 15,7 en 2024, 17,7 en 2014).",
            "eu_aggregate_published": {"2014": 17.7, "2024": 15.7,
                                       "url": "https://ec.europa.eu/eurostat/web/products-eurostat-news/w/edn-20260717-1"},
        }, "por_pais": eu}, f, ensure_ascii=False, indent=1)

    # ---- ratios: cruce con demanda (asuntos ingresados) y con población ----
    nac = json.load(open(os.path.join(DATA, "nacional_anual.json")))["nacional"]
    ine = json.load(open(os.path.join(ROOT, "raw", "ine_poblacion.json")))["Total Nacional"]
    pob = {str(p["anyo"]): p["valor"] for p in ine}
    ratios = {}
    for y, row in sorted(series.items()):
        act = row.get("jueces_en_activo")
        plz = row.get("plazas_jueces_constituidas")
        ing = nac.get(y, {}).get("total_ingresados")
        res = nac.get(y, {}).get("total_resueltos")
        p = pob.get(y)
        r = {"asuntos_ingresados": ing, "asuntos_resueltos": res,
             "jueces_en_activo": act, "plazas_constituidas": plz, "poblacion_ine": p}
        if ing and act:
            r["ingresados_por_juez_activo"] = round(ing / act, 1)
            r["resueltos_por_juez_activo"] = round(res / act, 1) if res else None
        if ing and plz:
            r["ingresados_por_plaza"] = round(ing / plz, 1)
        if p and act:
            r["jueces_activo_por_100k"] = round(act / p * 1e5, 2)
        if p and plz:
            r["plazas_por_100k"] = round(plz / p * 1e5, 2)
        if len(r) > 5:
            ratios[y] = r
    with open(os.path.join(DATA, "plantilla_ratios.json"), "w") as f:
        json.dump({"meta": {
            "source": "Cruce: jueces (CGPJ «Justicia dato a dato», a 1 de enero del año Y) × asuntos ingresados/resueltos del año Y (CGPJ series estadísticas, data/nacional_anual.json) × población INE a 1 de enero (raw/ine_poblacion.json)",
            "period": "solo años con jueces Y asuntos: " + ", ".join(y for y, r in ratios.items() if "ingresados_por_juez_activo" in r),
            "unit": {"ingresados_por_juez_activo": "asuntos ingresados en el año / jueces en activo a 1 de enero",
                     "resueltos_por_juez_activo": "asuntos resueltos en el año / jueces en activo a 1 de enero",
                     "ingresados_por_plaza": "asuntos ingresados / plazas constituidas",
                     "jueces_activo_por_100k": "jueces en activo por 100.000 hab.",
                     "plazas_por_100k": "plazas constituidas por 100.000 hab. (debe coincidir con la cifra que publica el CGPJ, ±0,1)"},
            "caveat": "Es un promedio bruto nacional: todos los asuntos de todos los órdenes entre todos los jueces, incluidos los de órganos colegiados y centrales. No mide carga real por juzgado ni ponderación por tipo de asunto. Sirve para ver la tendencia, no para fijar 'cuántos jueces faltan'. RUPTURA 2016: el ingresado penal pasa de 5,81 M (2015) a 3,37 M (2016) por cambio de criterio en la serie de asuntos (reforma penal de 2015 / registro de diligencias), no porque bajase la carga: comparar solo dentro de cada tramo, 2009-2015 y 2016-2025. 2015: ratio por plaza distorsionado por los 395 jueces en expectativa de destino (ver descartes). Jueces en activo excluye sustitutos y suplentes (1.112 plazas de justicia interina propuestas para 2024/25 según el CGPJ): el ratio real por persona que juzga es menor.",
        }, "por_anio": ratios}, f, ensure_ascii=False, indent=1)

    for y, r in sorted(series.items()):
        print(y, r)
    print("\nRATIOS:")
    for y, r in sorted(ratios.items()):
        print(y, r.get("ingresados_por_juez_activo"), r.get("ingresados_por_plaza"),
              r.get("jueces_activo_por_100k"), r.get("plazas_por_100k"))


if __name__ == "__main__":
    main()
