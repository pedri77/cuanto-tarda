#!/usr/bin/env python3
"""plantilla_contexto.py — fuentes complementarias de capacidad judicial.

Genera data/plantilla_cepej.json y data/plantilla_necesidades.json a partir de:
 - raw/plantillas/cepej_spain_fiche_2024data.txt  (CEPEJ, «Country fiche Spain,
   2024 data», descargado desde rm.coe.int con navegador: curl recibe 403)
 - raw/plantillas/cgpj_nota_350_jueces.html       (CGPJ, nota 11/07/2024,
   Plan Estratégico 2024-2033: plazas necesarias vs creadas, vacantes, ingresos)
 - raw/plantillas/cgpj_memoria2025_anexo_necesidades.txt (Memoria CGPJ 2025,
   anexo «Relación de necesidades»)
 - raw/plantillas/rcp_epsap_enero_2026.txt        (Boletín Estadístico del
   Personal al Servicio de las AAPP, enero 2026)
 - raw/ine_poblacion.json (población provincial, para el reparto Ministerio/CCAA)
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "raw", "plantillas")
DATA = os.path.join(ROOT, "data")


def esnum(tok):
    return float(tok.replace(" ", "").replace(".", "").replace(",", "."))


def parse_cepej():
    L = open(os.path.join(RAW, "cepej_spain_fiche_2024data.txt"), encoding="utf-8").read().splitlines()
    out = {"judges_evolution": {}, "non_judge_staff_evolution": {}}
    # La tabla resumen «Resources per 100 000 inh.» mezcla columnas de tendencia
    # (% 2014-2024) con la serie y no se parsea de forma fiable; se usan las dos
    # tablas de evolución (jueces y personal no juez), que traen año, absoluto,
    # ratio España y mediana UE por fila.
    # Evolución jueces: filas "2014  5 353  11,5  19,2"
    for i, s in enumerate(L):
        if "Evolution of the number of professional judges since 2014" in s:
            for j in range(i, i + 60):
                m = re.match(r"^\s*(20\d\d)\s+(\d[\d ]*\d)\s+(\d+,\d+)\s+(\d+,\d+)", L[j])
                if m:
                    out["judges_evolution"][m.group(1)] = {
                        "jueces_profesionales": esnum(m.group(2)),
                        "por_100k_espana": esnum(m.group(3)),
                        "por_100k_mediana_ue": esnum(m.group(4))}
            break
    for i, s in enumerate(L):
        if s.strip() == "Non-judge staff" and "Absolute Number" in " ".join(L[i:i + 5]):
            for j in range(i, i + 60):
                m = re.match(r"^\s*(20\d\d)\s+(\d[\d ]*\d)\s+(\d+,\d+)\s+(\d+,\d+)", L[j])
                if m:
                    out["non_judge_staff_evolution"][m.group(1)] = {
                        "personal_no_juez": esnum(m.group(2)),
                        "por_100k_espana": esnum(m.group(3)),
                        "por_100k_mediana_ue": esnum(m.group(4))}
            break
    # Fotografía 2024 (absolutos, ES, mediana UE)
    snap = {}
    for s in L:
        m = re.match(r"^\s*(Professional judges|Non-judge staff|Prosecutors|Non-prosecutor staff|Lawyers)\s+(\d[\d ]*\d)\s+(\d+,\d+)\s+(\d+,\d+)(\s|$)", s)
        if m and m.group(1) not in snap:
            snap[m.group(1)] = {"absoluto": esnum(m.group(2)), "por_100k_espana": esnum(m.group(3)),
                                "por_100k_mediana_ue": esnum(m.group(4))}
    out["snapshot_2024"] = snap
    for s in L:
        m = re.search(r"(\d[\d ]*\d) Rechtspfleger", s)
        if m:
            out["snapshot_2024"]["rechtspfleger_LAJ"] = esnum(m.group(1))
        m = re.search(r"Non-judge staff per judge\s+(\d+,\d+)\s+(\d+,\d+)", s)
        if m:
            out["snapshot_2024"]["no_juez_por_juez"] = {"espana": esnum(m.group(1)), "mediana_ue": esnum(m.group(2))}
    return out


def parse_cgpj_nota():
    t = open(os.path.join(RAW, "cgpj_nota_350_jueces.html"), encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    t = re.sub(r"\n\s*\n+", "\n", t)
    out = {"plazas_necesarias_vs_creadas": {}}
    m = re.search(r"Déficit de plazas\n((?:\d{4}\n[^\n]+\n[^\n]+\n[^\n]+\n)+)", t)
    if m:
        rows = m.group(1).strip().split("\n")
        for k in range(0, len(rows), 4):
            y, nec, cre, dfc = rows[k:k + 4]
            out["plazas_necesarias_vs_creadas"][y] = {
                "necesarias": int(nec), "creadas": None if "?" in cre else int(cre),
                "deficit": None if "?" in dfc else int(dfc)}
    m = re.search(r"turno libre ha sido de (.*?)\.", t)
    if m:
        out["ingresos_turno_libre"] = {y: int(n) for n, y in re.findall(r"(\d+) en (\d{4})", m.group(1))}
    m = re.search(r"Por el turno de juristas \(4º turno\), ingresaron (.*?)\.", t)
    if m:
        out["ingresos_cuarto_turno"] = {y: int(n) for n, y in re.findall(r"(\d+) en (\d{4})", m.group(1))}
    m = re.search(r"A (\d+ de \w+ de 2024), el número de plazas en juzgados y tribunales asciende a ([\d.]+), de las que ([\d.]+) son plazas en órganos unipersonales.*?y ([\d.]+) en órganos colegiados", t, re.S)
    if m:
        out["plazas_24_06_2024"] = {"fecha": m.group(1), "total": esnum(m.group(2)),
                                    "unipersonales": esnum(m.group(3)), "colegiados": esnum(m.group(4))}
    m = re.search(r"Respecto a las vacantes, a 3 de junio sumaban (\d+)", t)
    if m:
        out["vacantes_03_06_2024"] = int(m.group(1))
    m = re.search(r"déficit estructural de planta.*?asciende a (\d+) unidades judiciales", t, re.S)
    if m:
        out["deficit_estructural_unidades_2024"] = int(m.group(1))
    m = re.search(r"propusieron un total de ([\d.]+) plazas", t)
    if m:
        out["justicia_interina_plazas_propuestas_2024_2025"] = esnum(m.group(1))
    m = re.search(r"cifra en (\d+) las plazas de juez/a que deberían convocarse anualmente", t)
    if m:
        out["plazas_juez_a_convocar_por_anio_2024_2033"] = int(m.group(1))
    m = re.search(r"en 2033 se estima.*?unidades judiciales alcance una cifra de ([\d.]+).*?llegue a los ([\d.]+) efectivos.*?habría ([\d.]+) vacantes", t, re.S)
    if m:
        out["proyeccion_2033"] = {"unidades_judiciales": esnum(m.group(1)), "efectivos": esnum(m.group(2)),
                                  "vacantes": esnum(m.group(3))}
    return out


def parse_anexo():
    L = open(os.path.join(RAW, "cgpj_memoria2025_anexo_necesidades.txt"), encoding="utf-8").read().splitlines()
    out = {}
    for i, s in enumerate(L):
        if s.strip().startswith("Suma de plazas"):
            nums = [int(x) for x in re.findall(r"\d+", L[i + 1])]
            out["organos_colegiados_plazas_magistrado_necesarias"] = {
                "total_publicado": nums[-1], "columnas": nums[:-1],
                "suma_columnas": sum(nums[:-1]),
                "nota": "La fila 'Suma de plazas necesarias' publicada no cuadra con la suma de sus propias columnas ni con la suma de los totales por TSJ (123); se da el valor publicado y la discrepancia."}
    out["organos_unipersonales"] = "Tabla publicada pero la fila de suma viene vacía y los totales por fila no cuadran con sus columnas (ej. Madrid 93 frente a 113 sumando): no se extrae ningún total."
    return out


def parse_rcp():
    L = open(os.path.join(RAW, "rcp_epsap_enero_2026.txt"), encoding="utf-8").read().splitlines()
    out = {}
    for s in L:
        m = re.match(r"^Administración al servicio de tribunales de instancia\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", s)
        if m:
            out = {"funcionarios_carrera": esnum(m.group(1)), "laboral": esnum(m.group(2)),
                   "otro_personal_interinos": esnum(m.group(3)), "total_efectivos": esnum(m.group(4))}
            break
    return out


# Provincias del «territorio Ministerio» (CCAA sin competencias transferidas)
MINISTERIO = {
    "Castilla y León": ["Ávila", "Burgos", "León", "Palencia", "Salamanca", "Segovia", "Soria", "Valladolid", "Zamora"],
    "Castilla-La Mancha": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo"],
    "Extremadura": ["Badajoz", "Cáceres"],
    "Illes Balears": ["Balears, Illes"],
    "Región de Murcia": ["Murcia"],
    "Ceuta": ["Ceuta"], "Melilla": ["Melilla"],
}
TRANSFERIDAS = ["Andalucía", "Aragón", "Asturias", "Canarias", "Cantabria", "Cataluña",
                "Comunitat Valenciana", "Galicia", "La Rioja", "Madrid", "Navarra", "País Vasco"]


def reparto_poblacion():
    ine = json.load(open(os.path.join(ROOT, "raw", "ine_poblacion.json")))
    year = max(p["anyo"] for p in ine["Total Nacional"])
    def pob(name):
        return next(p["valor"] for p in ine[name] if p["anyo"] == year)
    total = pob("Total Nacional")
    mini = {k: sum(pob(p) for p in v) for k, v in MINISTERIO.items()}
    sm = sum(mini.values())
    return {"anio": year, "poblacion_total": total,
            "territorio_ministerio": {"ccaa": list(MINISTERIO), "poblacion": sm, "porcentaje": round(sm / total * 100, 1), "detalle": mini},
            "ccaa_transferidas": {"ccaa": TRANSFERIDAS, "n": len(TRANSFERIDAS),
                                  "poblacion": total - sm, "porcentaje": round((total - sm) / total * 100, 1)}}


def main():
    cepej = parse_cepej()
    with open(os.path.join(DATA, "plantilla_cepej.json"), "w") as f:
        json.dump({"meta": {
            "source": "CEPEJ (Consejo de Europa), «Study on the judicial systems in the EU Member States – Country fiche Spain (2024 data)», publicado para el EU Justice Scoreboard 2026",
            "url": "https://rm.coe.int/spain-country-fiche/48802c1531",
            "period": "2014-2024 (datos a 31 de diciembre de cada año)",
            "unit": "personas y personas por 100.000 habitantes; 'mediana UE' = mediana de los Estados miembros con dato",
            "acceso": "rm.coe.int devuelve HTTP 403 a curl (Cloudflare); el PDF se descargó con un navegador headless y se extrajo con pdftotext -layout",
            "definiciones": {
                "Professional judges": "jueces profesionales a tiempo completo que ejercen en tribunales (metodología CEPEJ, Q46); España reporta 5.431 en 2024 = jueces en activo a 1/1/2025 del CGPJ, pero 5.728 en 2022 = plazas constituidas del CGPJ: el dato español cambia de criterio entre años.",
                "Non-judge staff": "todo el personal no juez: en España 4.568 Rechtspfleger (= LAJ) + 46.060 'otros' (Gestión, Tramitación, Auxilio) + 1.164 médicos forenses fuera de la cifra.",
                "Prosecutors": "fiscales (2.812 en 2024).",
            },
            "caveat": "Es la ÚNICA fuente armonizada entre países con la misma definición de 'juez'. La serie Eurostat crim_just_job para España (6,2 en 2024) NO es comparable: Eurostat recoge en su cuestionario penal solo una parte de la carrera y la serie española rompe en 2017 (11,56 -> 6,38).",
        }, **cepej}, f, ensure_ascii=False, indent=1)

    nota = parse_cgpj_nota()
    anexo = parse_anexo()
    rcp = parse_rcp()
    rep = reparto_poblacion()
    with open(os.path.join(DATA, "plantilla_necesidades.json"), "w") as f:
        json.dump({
            "cgpj_plan_estrategico_2024_2033": {"meta": {
                "source": "CGPJ, nota de prensa 11/07/2024 «El CGPJ considera necesario el ingreso de 350 nuevos jueces al año hasta 2033…» (Plan Estratégico 2024-2033, Comisión Permanente)",
                "url": "https://www.poderjudicial.es/cgpj/es/Poder-Judicial/En-Portada/El-CGPJ-considera-necesario-el-ingreso-de-350-nuevos-jueces-al-ano-hasta-2033-para-cubrir-las-vacantes-por-fallecimiento--jubilacion-y-renuncia-que-se-produzcan",
                "period": "2018-2024 (datos) y 2024-2033 (proyección del CGPJ)",
                "unit": "plazas / personas",
                "caveat": "Las 'plazas necesarias' son las que el propio CGPJ pide crear cada año (unidades judiciales); las 'creadas' son las que aprueba el Gobierno por real decreto. La proyección 2033 es una estimación del CGPJ, no un dato.",
            }, **nota},
            "cgpj_memoria_2025_anexo_necesidades": {"meta": {
                "source": "CGPJ, Memoria anual 2025 (ejercicio 2024), anexo «Relación de necesidades» según valoraciones de los TSJ",
                "url": "https://www.poderjudicial.es/stfls/CGPJ/SECRETARÍA GENERAL/MEMORIA ANUAL/FICHERO/20250905MemoriaCGPJ2025_08AnexoRelacNecesid.pdf",
                "period": "2024", "unit": "plazas de magistrado / unidades judiciales",
            }, **anexo},
            "rcp_boletin_enero_2026": {"meta": {
                "source": "Ministerio para la Transformación Digital y de la Función Pública, Boletín Estadístico del Personal al Servicio de las AAPP (EPSAP), enero 2026, epígrafe «Administración al servicio de tribunales de instancia»",
                "url": "https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/2026_01/revision-agosto-2026/EPSAP_Enero_2026%20.pdf",
                "period": "1 de enero de 2026", "unit": "efectivos (personas, no plazas)",
                "caveat": "SOLO el personal de la Administración de Justicia dependiente del Ministerio (territorio no transferido). El personal de las 12 CCAA transferidas está dentro de 'Administración General de las CC.AA.' sin desglose por justicia. Desde enero 2023 el boletín excluye jueces y fiscales. La página 'Evolución de los efectivos de las CCAA por área de actividad' devolvía HTTP 500 el 2026-10-01.",
            }, **rcp},
            "reparto_territorial": {"meta": {
                "source": "INE, cifras de población a 1 de enero (raw/ine_poblacion.json) agregadas por provincia; lista de CCAA transferidas según el reparto competencial vigente (Ministerio: Castilla y León, Castilla-La Mancha, Extremadura, Illes Balears, Región de Murcia, Ceuta y Melilla)",
                "unit": "habitantes y %",
            }, **rep},
            "oposiciones_cuerpos_generales_2022": {"meta": {
                "source": "Ministerio de Justicia, nota 14/12/2022 «Justicia convoca 2.874 plazas para diferentes cuerpos de la Administración de Justicia»",
                "url": "https://www.mjusticia.gob.es/es/institucional/gabinete-comunicacion/noticias-ministerio/Justicia-convoca-2874-plazas-para-diferentes-cuerpos-de-la-Administracion-de-Justicia",
                "period": "OEP 2020+2021+2022 acumuladas, turno libre", "unit": "plazas",
                "caveat": "Convocatoria conjunta para todo el territorio (Ministerio + CCAA). Solo plazas de reposición. No se ha localizado una serie anual oficial de plazas convocadas en formato tabular.",
            }, "total": 2874, "gestion_procesal": 1091, "tramitacion_procesal": 1191, "auxilio_judicial": 592},
        }, f, ensure_ascii=False, indent=1)
    print(json.dumps({"cepej_snapshot": cepej["snapshot_2024"], "cepej_years": list(cepej["judges_evolution"]),
                      "nota": nota, "anexo": anexo, "rcp": rcp, "reparto": {k: v for k, v in rep.items() if k != "territorio_ministerio"}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
