# Cuánto tarda la justicia

Veinticinco años de estadística judicial oficial del **CGPJ** — asuntos ingresados, resueltos y en
trámite, y las tres tasas que el propio Consejo define con ellos — puestos en un buscador por año,
comunidad autónoma, provincia y orden jurisdiccional.

- **Web:** <https://pedri77.github.io/cuanto-tarda/>
- **Vídeo:** episodio `cci-13` de la serie [«Construido con IA»](https://iacedemy.com/free/yt/construido-con-ia/) de IAcademy.
- **Plantilla para hacer el tuyo:** [observatorio-datos-plantilla](https://github.com/pedri77/observatorio-datos-plantilla).

## Lo primero, y es lo más importante

**Aquí no está «cuántos días tarda un juicio».** La duración media de los procedimientos **no se
publica en las series descargables** del CGPJ: solo aparece en su herramienta interactiva de
transparencia y como estimación por modelo. Este observatorio trabaja con lo que sí se publica y se
puede verificar — el recuento de asuntos — y no estima la duración por su cuenta. Decirlo es parte
del dato.

Lo que sí se puede medir es la **carga**: cuántos asuntos quedan vivos en los juzgados al cerrar el
año. Y ahí la serie es contundente.

## Qué sale de los datos (2025)

| Indicador | Valor |
|---|---|
| Asuntos ingresados | 7.550.806 |
| Asuntos resueltos | 7.437.033 |
| **Quedaron en trámite** | **4.673.596** |
| Tasa de congestión | 1,62 |
| Litigiosidad | 153,7 asuntos por 1.000 habitantes |

- El stock de asuntos en trámite ha pasado de 2.031.888 en 2001 a 4.673.596 en 2025: **+130 %**.
- **Entra más de lo que sale**: en 16 de los 25 años los ingresados superaron a los resueltos, y en
  los tres últimos seguidos.
- Por orden jurisdiccional, el más congestionado en 2025 es el **social** (tasa 2,14).
- Por comunidad, la congestión va de Murcia (1,95) y Castilla-La Mancha (1,84) a Aragón (1,37).

## Las tres tasas, con la definición oficial

- **Congestión** = (asuntos en trámite al inicio + ingresados en el periodo) ÷ resueltos en el periodo.
- **Resolución** = resueltos ÷ ingresados. Por encima de 1, se resuelve más de lo que entra.
- **Pendencia** = en trámite al final ÷ ingresados en el periodo.

Definiciones literales del CGPJ, reproducidas en [`data/sources.json`](data/sources.json). **Congestión
alta no es sinónimo de lentitud**: significa que hay muchos asuntos vivos por cada uno que se cierra.

## Reproducirlo

```bash
python3 scripts/cgpj_fetch.py     # descarga las series XLSX del CGPJ + población INE a raw/ (cachea)
python3 scripts/cgpj_build.py     # agrega y escribe data/*.json (unos segundos)
```

| Fichero | Contenido |
|---|---|
| `data/nacional_anual.json` | España 2001-2025: ingresados, resueltos, en trámite y las cuatro tasas |
| `data/nacional_por_orden.json` | Desglose civil / penal / contencioso / social, 2021-2025 |
| `data/ccaa.json` | 17 comunidades, 2001-2025, con datos por habitante (derivados) |
| `data/provincias.json` | 50 provincias, 2001-2025 |
| `data/sources.json` | Definiciones oficiales de cada tasa, URLs y avisos |

`raw/` (3,7 MB de XLSX) no se versiona: `cgpj_fetch.py` lo repone.

## Trampas encontradas y cómo se han tratado

- **El desglose por orden jurisdiccional solo existe desde 2021.** Para años anteriores la web lo dice
  en vez de mostrar una tabla vacía o reventar.
- **El total de España no es la suma de las comunidades.** Faltan Ceuta y Melilla (sin fila propia) y
  están excluidos los órganos centrales (Tribunal Supremo, Audiencia Nacional, juzgados centrales): lo
  advierte el propio fichero.
- **La población provincial del INE llega hasta 2022.** Los datos «por 1.000 habitantes» de 2023-2025
  usan una población derivada y contrastada con 2022 (diferencia 0,5 %); se marcan como derivados.
- **La serie larga no es homogénea en causas.** Cambios como la desjudicialización de algunos asuntos
  o la Oficina Judicial (2021) alteran lo que se cuenta. Las comparaciones entre años lejanos van con
  cautela, y así lo advierte el CGPJ.
- **Un error del CGPJ en los ficheros «por Provincias»**: las hojas de congestión y pendencia llevan
  copiada la definición de resolución. Los valores numéricos se verificaron correctos; el fallo es solo
  del texto de la definición.

## Verificación

- **Contra la nota de prensa del CGPJ de 30-03-2026**: 7.550.806 ingresados y 7.437.033 resueltos en
  2025 — coincidencia exacta. Litigiosidad 153,70 frente a 153,7389 de la serie (redondeo).
- **Tasas recalculadas** con la definición oficial: congestión 1,623, resolución 0,985, pendencia 0,628
  en 2025 — coincidencia a cuatro decimales, nacional y por provincias (p. ej. Albacete 1,7558).
- **Cobertura**: 24.575 celdas leídas, 0 vacías.

## Fuente y licencia

Consejo General del Poder Judicial, Sección de Estadística Judicial — series estadísticas. Población:
INE. Reutilización permitida según las condiciones del CGPJ. Agregados y datos por habitante de
elaboración propia; el CGPJ no participa ni avala esta reutilización.

Código bajo **MIT** (`LICENSE`).
