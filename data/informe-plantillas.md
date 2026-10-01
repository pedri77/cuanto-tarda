# Informe: capacidad del sistema judicial (plantillas) — cci-13 «cuanto-tarda»

Fecha de comprobación: **2026-10-01**. Todo lo que sigue sale de `scripts/plantilla_fetch.py`
(descarga + `pdftotext`), `scripts/plantilla_build.py` (series CGPJ, Eurostat, ratios) y
`scripts/plantilla_contexto.py` (CEPEJ, necesidades, RCP, reparto territorial). Los crudos
viven en `raw/plantillas/` (57 MB, fuera del repo); los derivados en `data/plantilla_*.json`,
cada uno con bloque `meta` por campo (fuente, periodo, URL, unidad, salvedades). Ningún dato
de personas: solo totales por cuerpo y territorio.

---

## 1. Qué se encontró y dónde

### 1.1 CGPJ — «La Justicia dato a dato» (la fuente que lo resuelve casi todo)

- URL índice: <https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estadistica-por-temas/Actividad-de-los-organos-judiciales/Juzgados-y-Tribunales/Justicia-Dato-a-Dato>
- Un PDF por año, **ediciones 2003 a 2023 y 2025**. Las 23 descargas devolvieron HTTP 200.
- **No existe edición 2024**: la página oficial salta de 2023 a 2025 y las dos rutas que
  siguen el patrón de las demás (`/stfls/CGPJ/ESTADÍSTICA/FICHEROS/Justicia Dato a Dato - Año 2024.pdf`
  y `/stfls/ESTADISTICA/FICHEROS/JusticaDatoaDato/...2024.pdf`) devuelven **HTTP 404**.
- Qué trae (datos **a 1 de enero** de cada año, totales por TSJ y nacional):
  - «Número de jueces y magistrados» = **plazas orgánicas constituidas** (cubiertas o no).
  - «Pirámide de edad de los jueces y magistrados **en activo**» = miembros de la carrera
    judicial en activo (fila Total). Solo es tabla desde la edición 2009; en 2006-2008 es un
    gráfico sin cifras y en 2003-2005 no existe.
  - «Plantilla orgánica del Ministerio Fiscal» (pie: *Fuente: Fiscalía General del Estado*).
  - «Plantilla de Secretarios Judiciales» (hasta 2015) / «de Letrados de la Administración de
    Justicia» (desde 2016): **plantilla y, desde la edición 2014, también efectivos**. Es el
    único cuerpo con plazas y personas en la misma tabla.
  - «Plantilla de funcionarios judiciales» = cuerpos generales (Gestión, Tramitación, Auxilio)
    por TSJ, **incluidas las CCAA transferidas**, con pie *Fuente: Ministerio de Justicia*.
    Desde 2016 hay tablas aparte para fiscalías, juzgados de paz, registros civiles, IML y
    MUGEJU.
- Derivado: `data/plantilla_series.json` (`por_anio` + `extraccion_contexto` con la línea del
  PDF y el texto literal de cada fila Total usada, para auditar).

### 1.2 CGPJ — Memoria anual 2025 (ejercicio 2024)

- Capítulo «Panorámica de la Justicia»: <https://www.poderjudicial.es/stfls/CGPJ/SECRETARÍA%20GENERAL/MEMORIA%20ANUAL/FICHERO/20250905MemoriaCGPJ2025_07PanoramicaJusticia.pdf>
  - Gráfico «Número de plazas de juez constituidas a 1 de enero» 2015-2024 y «Nº de jueces por
    100.000 habitantes» 2015-2024 (usado para verificar, §4).
  - Indicadores de cobertura por tipo de órgano y cuerpo (solo 2024, no serie): PCNT (% de
    días cubiertos por no titulares), PDSC (% de días sin cubrir), IR (rotación). Ejemplo
    literal: Juzgados de 1ª Instancia/Instrucción, PCNT magistrado 14,9 %, LAJ 26,0 %,
    Tramitación 30,3 %, Auxilio 34,8 %; PDSC entre 1,2 % y 3,3 %.
- Anexo «Relación de necesidades»: <https://www.poderjudicial.es/stfls/CGPJ/SECRETARÍA%20GENERAL/MEMORIA%20ANUAL/FICHERO/20250905MemoriaCGPJ2025_08AnexoRelacNecesid.pdf>
  - Órganos colegiados: la fila «Suma de plazas necesarias» publica **109**, pero sus propias
    columnas suman 148 y los totales por TSJ suman 123. Se entrega el valor publicado con la
    discrepancia.
  - Órganos unipersonales: fila de suma vacía y filas que no cuadran (Madrid: total 93 frente
    a 113 sumando columnas). **No se extrae total**.

### 1.3 CGPJ — Plan Estratégico 2024-2033 (nota 11/07/2024)

URL: <https://www.poderjudicial.es/cgpj/es/Poder-Judicial/En-Portada/El-CGPJ-considera-necesario-el-ingreso-de-350-nuevos-jueces-al-ano-hasta-2033-para-cubrir-las-vacantes-por-fallecimiento--jubilacion-y-renuncia-que-se-produzcan>
(HTTP 200). Es la única tabla oficial de **plazas necesarias frente a creadas**:

| Año | Plazas necesarias (CGPJ) | Plazas creadas (Gobierno) | Déficit |
|---|---|---|---|
| 2019 | 263 | 75 | 188 |
| 2020 | 40 | 33 | 7 |
| 2021 | 110 | 60 | 50 |
| 2022 | 176 | 70 | 106 |
| 2023 | 293 | 70 | 223 |
| 2024 | 421 | «¿?» (sin previsión conocida) | — |

Además, literal de la nota: plazas a 24/06/2024 **5.854** (3.938 unipersonales, 1.916
colegiadas); **vacantes a 03/06/2024: 277** (+38 de nombramiento discrecional bloqueadas);
«déficit estructural de planta» de **421 unidades judiciales**; ingresos por turno libre
190 (2018), 180 (2019), 168 (2020), 139 (2021), 120 (2022), 120 (2023); 4.º turno 12 (2018),
50 (2020), 85 (2023); **1.112 plazas de justicia interina** (sustitutos/suplentes) propuestas
para 2024/25; proyección del CGPJ a 2033: 6.554 unidades, 4.458 efectivos, 2.096 vacantes si
no se convocan 350 plazas/año. Derivado: `data/plantilla_necesidades.json`.

### 1.4 CEPEJ (Consejo de Europa) — Country fiche Spain, 2024 data

URL: <https://rm.coe.int/spain-country-fiche/48802c1531>. **curl recibe HTTP 403** (Cloudflare,
también vía Firecrawl); se descargó con un navegador headless (3,26 MB, `application/pdf`) y se
extrajo con `pdftotext`. Es la **única comparación europea con la misma definición de juez**.

| Año | Jueces profesionales ES | por 100k ES | mediana UE | Personal no juez ES | por 100k ES | mediana UE |
|---|---|---|---|---|---|---|
| 2014 | 5.353 | 11,5 | 19,2 | 48.563 | 104,6 | 54,9 |
| 2016 | 5.367 | 11,5 | 23,6 | 49.186 | 105,7 | 63,4 |
| 2018 | 5.419 | 11,5 | 21,8 | 47.645 | 101,4 | 56,5 |
| 2020 | 5.320 | 11,2 | 23,9 | 48.620 | 102,7 | 59,0 |
| 2022 | 5.728 | 11,9 | 22,9 | 49.802 | 103,6 | 59,4 |
| 2023 | 5.416 | 11,1 | 21,5 | 50.069 | 103,0 | 60,2 |
| 2024 | 5.431 | 11,1 | 23,4 | 50.628 | 103,2 | 59,4 |

(serie completa 2014-2024 en `data/plantilla_cepej.json`). Fotografía 2024: fiscales 2.812
(5,7/100k frente a mediana UE 14,5); personal no fiscal 2.378; **9,3 personas de apoyo por
juez frente a 3,3 de mediana UE**; de los 50.628 no jueces, 4.568 son «Rechtspfleger» (= LAJ)
y 46.060 «otros» (Gestión, Tramitación, Auxilio), más 1.164 forenses fuera del cómputo. La
propia fiche dice que el reparto por sexo solo se conoce para «las 5 CCAA de competencia
directa del Ministerio (5 de 17)».

El EU Justice Scoreboard 2026 (<https://commission.europa.eu/document/download/d1367f58-9eed-4ebd-8eb3-68646b7c7ddc_en?filename=2026_eu_justice_scoreboard.PDF>,
HTTP 200), figura 36, ordena los 27 países por jueces/100k: España es el **tercero con
menos**, solo por delante de Malta, Dinamarca e Irlanda. El PDF trae el gráfico sin cifras.

### 1.5 Eurostat — `crim_just_job` (jueces profesionales por 100.000 hab.)

API: <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/crim_just_job?format=JSON&lang=EN> (HTTP 200).
Serie España: 10,76 (2012) · 11,51 (2014) · 11,56 (2016) · **6,38 (2017)** · 6,18 (2024).
La serie **rompe en 2017** sin que la plantilla real cambie (CGPJ: 5.367 → 5.377 jueces en
activo): España pasó a reportar a Eurostat con otro criterio (cuestionario de justicia
penal UN-CTS). Por tanto el «6,2 jueces por 100.000» que Eurostat difundió el 17/07/2026
(<https://ec.europa.eu/eurostat/web/products-eurostat-news/w/edn-20260717-1>, media UE 15,7)
**no es comparable** ni con el 11,1 de CEPEJ ni con el 11,9 del CGPJ. Se guarda en
`data/plantilla_europa.json` con la advertencia y **no se usa para comparar**.

### 1.6 Registro Central de Personal — Boletín EPSAP enero 2026

URL: <https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/2026_01/revision-agosto-2026/EPSAP_Enero_2026%20.pdf> (HTTP 200).
Epígrafe «Administración al servicio de tribunales de instancia»: **14.381 efectivos**
(10.044 funcionarios de carrera, 467 laborales, 3.870 «otro personal», es decir interinos)
a 1/1/2026. Es la única cifra de **personas reales** (no plazas) de cuerpos generales, pero
**solo del territorio Ministerio**. Desde enero 2023 el boletín excluye jueces y fiscales.

### 1.7 Ministerio de Justicia — oposiciones

Nota 14/12/2022 (<https://www.mjusticia.gob.es/es/institucional/gabinete-comunicacion/noticias-ministerio/Justicia-convoca-2874-plazas-para-diferentes-cuerpos-de-la-Administracion-de-Justicia>,
HTTP 200): **2.874 plazas** de turno libre (Gestión 1.091, Tramitación 1.191, Auxilio 592),
OEP 2020+2021+2022 acumuladas, «solo plazas de reposición», convocatoria conjunta para todo el
territorio. No se ha localizado una serie anual tabulada de plazas convocadas.

---

## 2. Qué NO existe (hallazgos negativos, con evidencia)

| Dato | Estado | Evidencia |
|---|---|---|
| «Dato a dato» 2024 | no existe | HTTP 404 en las dos rutas; ausente del índice oficial |
| Jueces en activo 2003-2008 | no publicado en tabla | ed. 2003-2005 sin pirámide; ed. 2006-2008 pirámide solo como gráfico (texto extraído: cabecera y a continuación «Número de Juzgados de Paz») |
| Plazas de juez 2004 comparables | no | la ed. 2004 solo trae jueces por TSJ sin TS/AN ni fila Total (suma de filas 3.997, guardada aparte) |
| Efectivos (no plazas) de fiscales y cuerpos generales, serie estatal | no publicado | el «Dato a dato» solo da efectivos para LAJ; el RCP solo cubre territorio Ministerio |
| Efectivos de cuerpos generales en las 12 CCAA transferidas | no en fuentes estatales | RCP los agrega en «Administración General de las CCAA»; la página «Evolución de efectivos de las CCAA por área de actividad» devuelve HTTP 500 |
| Vacantes de jueces como serie anual | no publicado | solo fotografías: 277 a 03/06/2024 (nota CGPJ) y los indicadores PDSC/PCNT de la Memoria 2025 para un solo ejercicio |
| Plazas de juez convocadas por año | parcial | ingresos por turno 2018-2023 en la nota CGPJ; no hay tabla oficial de plazas convocadas |
| Empleo en justicia según EPA | no existe a esa granularidad | la EPA publica CNAE 84 completa (AAPP, defensa, SS); no separa 84.23 |
| Nota CGPJ «53,2 % mujeres en la carrera judicial» | enlace roto | HTTP 404 con curl y con Firecrawl |
| CEPEJ por descarga automática | bloqueada | HTTP 403 a curl; se necesita navegador; `raw/` no se versiona, así que quien reejecute debe repetir la descarga a mano |
| Módulos de carga de trabajo por juez (cuántos asuntos «debería» llevar un juez) | no localizado | no hay publicación vigente del CGPJ con módulos; **sin esto no se puede calcular «necesidad»** |

---

## 3. Series y ratios

### 3.1 Plantillas (totales nacionales a 1 de enero; `data/plantilla_series.json`)

| Año | Plazas juez | Jueces activo | Fiscales (plantilla) | Secret./LAJ plantilla | LAJ efectivos | Cuerpos generales |
|---|---|---|---|---|---|---|
| 2003 | 4.109 | — | 1.610 | — | — | — |
| 2004 | (3.997 sin TS/AN) | — | 1.630 | — | — | — |
| 2005 | 4.413 | — | 1.740 | 3.330 | — | 36.593 |
| 2006 | 4.576 | — | 1.874 | 3.536 | — | 38.098 |
| 2007 | 4.543 | — | 1.973 | 3.976 | — | 39.069 |
| 2008 | 4.674 | — | 2.178 | 3.662 | — | 32.362 (†) |
| 2009 | 4.836 | 4.439 | 2.189 | 3.778 | — | 33.429 (†) |
| 2010 | 4.984 | 4.536 | 2.307 | 4.115 | — | 43.747 |
| 2011 | 5.171 | 4.689 | 2.407 | 4.148 | — | 44.576 |
| 2012 | 5.171 | 4.890 | 2.407 | 4.180 | — | 44.748 |
| 2013 | 5.211 | 5.036 | 2.407 | 4.191 | — | 44.839 |
| 2014 | 5.362 | 5.219 | 2.407 | 4.193 | 3.665 | 44.896 |
| 2015 | 5.847 (‡) | 5.219 (§) | 2.407 | 4.308 | 3.615 | 44.937 |
| 2016 | 5.692 | 5.366 | 2.473 | 4.185 | 3.701 | 39.042 (¶) |
| 2017 | 5.507 | 5.367 | 2.473 | 4.185 | 3.746 | 39.058 |
| 2018 | 5.552 | 5.377 | 2.473 | 4.209 | 3.802 | 39.058 |
| 2019 | 5.594 | 5.419 | 2.553 | 4.280 | 3.807 | 39.924 |
| 2020 | 5.635 | 5.341 | 2.553 | 4.310 | 3.746 | 40.155 |
| 2021 | 5.668 | 5.320 | 2.553 | 4.422 | 3.563 | 40.829 |
| 2022 | 5.728 | 5.408 | 2.553 | 4.389 | 3.543 | 41.483 |
| 2023 | 5.799 | 5.343 | 2.613 | 4.456 | 3.449 | 42.699 |
| 2025 | 5.846 | 5.431 | 2.762 | 4.543 | 3.512 | 42.528 |

(†) Ed. 2008-2009 cambian de fuente (Estadística Judicial CGPJ en vez de Ministerio) y solo
cuentan órganos judiciales y servicios comunes de notificaciones: no comparables.
(‡) La ed. 2015 incluye 395 jueces en expectativa de destino; la propia fuente avisa de que
«rompe el criterio de contabilizar plazas orgánicas».
(§) Las ediciones 2014 y 2015 publican **la misma tabla** de activos (5.219): hallazgo de la
fuente, no del extractor (verificado leyendo ambos PDF).
(¶) Desde 2016 la cifra es **solo órganos judiciales**; fiscalías (2.061-2.401), juzgados de
paz (≈2.500-2.700), registros civiles, IML y MUGEJU van en tablas aparte. De ahí la caída
44.937 → 39.042. Hasta 2015 se excluye además la columna de médicos forenses.

Lectura rápida que sí aguanta: **jueces en activo 2009 → 2025: 4.439 → 5.431 (+22 %)**;
plazas 2010 → 2025: 4.984 → 5.846 (+17 %); fiscales 2.307 → 2.762; LAJ efectivos siempre
≈ 77-88 % de la plantilla (2025: 3.512 de 4.543, **1.031 plazas de LAJ sin cubrir**, 22,7 %).

### 3.2 El cruce con la demanda: asuntos por juez (`data/plantilla_ratios.json`)

Años en que existen **las dos** series (jueces en activo a 1 de enero del año Y y asuntos
ingresados del año Y): **2009-2023 y 2025** (16 años). 2024 no tiene denominador.

| Año | Ingresados | Jueces activo | **Ingresados por juez** | Resueltos por juez | Jueces activo / 100k hab. | Plazas / 100k hab. |
|---|---|---|---|---|---|---|
| 2009 | 9.567.676 | 4.439 | 2.155 | 2.063 | 9,60 | 10,46 |
| 2010 | 9.427.927 | 4.536 | 2.079 | 2.047 | 9,76 | 10,72 |
| 2011 | 9.140.567 | 4.689 | 1.949 | 1.970 | 10,05 | 11,08 |
| 2012 | 9.108.037 | 4.890 | 1.863 | 1.888 | 10,44 | 11,04 |
| 2013 | 8.749.336 | 5.036 | 1.737 | 1.786 | 10,78 | 11,15 |
| 2014 | 8.749.452 | 5.219 | 1.677 | 1.703 | 11,22 | 11,53 |
| 2015 | 8.478.731 | 5.219 | 1.625 | 1.659 | 11,24 | 12,59 (‡) |
| — ruptura de la serie de asuntos (ver abajo) — |
| 2016 | 5.813.170 | 5.366 | 1.083 | 1.120 | 11,55 | 12,26 |
| 2017 | 5.875.887 | 5.367 | 1.095 | 1.071 | 11,54 | 11,84 |
| 2018 | 5.994.102 | 5.377 | 1.115 | 1.075 | 11,52 | 11,90 |
| 2019 | 6.279.302 | 5.419 | 1.159 | 1.122 | 11,55 | 11,92 |
| 2020 | 5.529.954 | 5.341 | 1.035 | 979 | 11,28 | 11,91 |
| 2021 | 6.273.090 | 5.320 | 1.179 | 1.189 | 11,22 | 11,96 |
| 2022 | 6.685.301 | 5.408 | 1.236 | 1.195 | 11,40 | 12,08 |
| 2023 | 6.999.331 | 5.343 | 1.310 | 1.206 | (sin INE) | (sin INE) |
| 2025 | 7.550.806 | 5.431 | **1.390** | 1.369 | (sin INE) | (sin INE) |

- **Ruptura 2016**: el ingresado penal cae de 5,81 M (2015) a 3,37 M (2016) por cambio de
  criterio en la serie de asuntos (reforma penal de 2015), no porque bajara la carga. Solo se
  comparan años dentro de cada tramo: 2009-2015 y 2016-2025.
- Dentro del tramo homogéneo 2016-2025: **de 1.083 a 1.390 asuntos ingresados por juez en
  activo (+28 %)**, con los jueces en activo casi planos (5.366 → 5.431, +1,2 %) y los asuntos
  +30 %. 2020 (pandemia) es el mínimo.
- Es un promedio bruto nacional (todos los órdenes, todos los jueces incluidos TS/AN y
  colegiados). No mide carga por juzgado ni pondera por tipo de asunto. **No incluye** a los
  jueces sustitutos y magistrados suplentes (1.112 plazas propuestas para 2024/25): el ratio
  por persona que realmente juzga es algo menor. Sirve para la tendencia, no para decir
  «faltan N jueces».
- Población INE del repo llega a 2022; por eso 2023 y 2025 no tienen ratio por habitante
  propio. Para esos años valen las cifras que publica el CGPJ (11,9 en 2024 y 2025) y CEPEJ
  (11,1 en 2023 y 2024).

### 3.3 Comparación europea (misma definición, CEPEJ)

España 2024: **11,1 jueces/100k frente a 23,4 de mediana UE** (menos de la mitad); fiscales
5,7 frente a 14,5; personal no juez **103,2 frente a 59,4** (casi el doble); 9,3 empleados
de apoyo por juez frente a 3,3. Tendencia 2014-2024: España plana (11,5 → 11,1) mientras la
mediana UE sube (19,2 → 23,4). Esta es la única frase sobre «suficiencia» que se puede decir
sin opinar: **por comparación, España tiene pocos jueces y mucho personal de apoyo por juez.**

---

## 4. Verificación manual (cifras contrastadas con lo que publica la fuente)

1. **Plazas de juez 2015-2023, extractor vs gráfico de la Memoria CGPJ 2025** (texto del PDF
   `cgpj_memoria2025_panoramica.txt`, líneas ~590-605): memoria 5.847 / 5.692 / 5.507 /
   5.551 / 5.593 / 5.635 / 5.668 / 5.728 / 5.799; extractor 5.847 / 5.692 / 5.507 / **5.552** /
   **5.594** / 5.635 / 5.668 / 5.728 / 5.799. Coinciden 7 de 9; en 2018 y 2019 el CGPJ se
   desvía 1 plaza entre sus propias publicaciones. Para 2024 la memoria da 5.785 (no hay
   «Dato a dato» 2024).
2. **Jueces por 100.000**: memoria CGPJ 2022 = 12,1; calculado aquí con INE = 12,08. Dato a
   dato 2025 = 11,9 (texto literal «ESPAÑA 11,9», p. 11); con las 5.846 plazas y la población
   INE 2025 de 49,08 M que cita CEPEJ sale 11,9.
3. **CEPEJ frente a CGPJ**: CEPEJ «professional judges» 2024 = 5.431 = jueces en activo a
   1/1/2025 del CGPJ (5.431, p. 12 del Dato a dato 2025); CEPEJ 2017 = 5.377 = activo
   1/1/2018; CEPEJ 2020 = 5.320 = activo 1/1/2021. **Pero** CEPEJ 2022 = 5.728 = *plazas*
   1/1/2022 del CGPJ, no activos (5.408): España cambió de criterio ese año en lo que reporta
   al Consejo de Europa. CEPEJ Rechtspfleger 4.568 ≈ plantilla LAJ 4.543 (1/1/2025).
4. **Dato a dato 2025, lectura directa del PDF** (p. 15-17): fiscales 2.762 (30 de Sala +
   2.305 + 427 abogados fiscales); LAJ 4.543 plantilla / 3.512 efectivos; cuerpos generales
   13.059 + 21.150 + 8.319 = 42.528. Idéntico a `plantilla_series.json["2025"]`.

---

## 5. Límites que hay que decir en el vídeo

1. **Plazas ≠ jueces en activo ≠ jueces sustitutos.** Plazas orgánicas: 5.846 (1/1/2025).
   Carrera judicial en activo: 5.431. Diferencia (415) no son «vacantes» exactas (hay
   jueces en comisión, excedencia, órganos centrales…), pero el CGPJ cifró las vacantes
   reales en 277 (03/06/2024). Encima hay 1.112 plazas de justicia interina propuestas:
   personas que juzgan sin ser de carrera. Nunca se suman.
2. **Plantilla ≠ efectivos.** Para fiscales y cuerpos generales solo hay plantilla (plazas).
   Solo los LAJ tienen efectivos: 22,7 % de plazas sin cubrir en 2025. Para cuerpos generales
   la Memoria CGPJ 2025 da el % de días cubiertos por interinos (PCNT) por tipo de órgano:
   entre 20 % y 37 % en juzgados de primera instancia, mercantil y violencia sobre la mujer.
3. **CCAA transferidas.** 12 comunidades (Andalucía, Aragón, Asturias, Canarias, Cantabria,
   Cataluña, C. Valenciana, Galicia, La Rioja, Madrid, Navarra, País Vasco) con **39,0 M de
   habitantes (82,3 % de España, INE 2022)** gestionan su propio personal. Sus **plantillas**
   sí están en el «Dato a dato» (las fija el Ministerio); sus **efectivos** no están en ninguna
   fuente estatal. El 14.381 del RCP cubre solo el 17,7 % de la población. Cualquier «total
   de personas trabajando en justicia» a escala estatal es, hoy, incompleto.
4. **Cambios de criterio**: edición 2015 (plazas con jueces en expectativa de destino), 2016
   (cuerpos generales solo en órganos judiciales), 2008-2009 (otra fuente), 2014=2015 (tabla
   de activos repetida), serie de asuntos 2016 (penal), Eurostat 2017 (reporte español),
   CEPEJ 2022 (plazas en vez de activos). Todos marcados en los `meta`.
5. **No hay módulos de carga oficiales vigentes** que digan cuántos asuntos «debe» llevar un
   juez, luego no se puede calcular una «necesidad» objetiva desde la demanda.

---

## 6. ¿Se puede responder a «¿es suficiente el personal?» con estos datos, y hasta dónde?

**Sí, solo por comparación y por lo que dicen los organismos; no por necesidad calculada.**

- **Por comparación europea (CEPEJ, misma definición):** España tiene 11,1 jueces por
  100.000 habitantes frente a una mediana UE de 23,4, y es el tercer país de la UE con menos
  jueces por habitante (Scoreboard 2026). En personal de apoyo ocurre lo contrario: 103 por
  100.000 frente a 59. Fiscales: 5,7 frente a 14,5. Esto se puede afirmar con fuente y fecha.
- **Por lo que afirma el propio CGPJ (fuente, no opinión):** «déficit estructural de planta
  de 421 unidades judiciales» (informe de 04/07/2024); entre 2019 y 2023 pidió 882 plazas y
  se crearon 308; necesita 350 ingresos al año hasta 2033 solo para reponer jubilaciones.
- **Por la tendencia medida aquí:** en el tramo homogéneo 2016-2025 los asuntos ingresados
  por juez en activo pasan de 1.083 a 1.390 (+28 %), con los jueces en activo prácticamente
  igual. Es decir: la demanda crece y el denominador no.
- **Lo que NO se puede decir:** cuántos jueces o funcionarios «faltan» en términos absolutos
  (no hay módulo de carga oficial ni efectivos reales de las CCAA transferidas), ni que el
  personal de apoyo sea «suficiente» porque la ratio europea sea alta (la fiche CEPEJ
  advierte de que las categorías no son comparables entre países).

Frase que sí aguanta en el guion: *«España tiene menos de la mitad de jueces por habitante
que la mediana de la UE, el propio CGPJ dice que faltan 421 unidades judiciales, y desde
2016 cada juez recibe un 28 % más de asuntos que entonces con la misma plantilla. Cuántos
faltan exactamente, nadie lo publica.»*

---

## 7. Ficheros entregados

- `scripts/plantilla_fetch.py` — descarga con caché (31 ficheros, 0 fallos tras excluir 2024
  como inexistente) + `pdftotext -layout`.
- `scripts/plantilla_build.py` — `data/plantilla_series.json`, `data/plantilla_europa.json`,
  `data/plantilla_ratios.json`.
- `scripts/plantilla_contexto.py` — `data/plantilla_cepej.json`, `data/plantilla_necesidades.json`.
- `data/plantilla_sources.json` — catálogo de fuentes con si sirven y por qué.
- Sin tocar: `site/`, `scripts/cgpj_*.py`, `data/*.json` previos. Sin git.
