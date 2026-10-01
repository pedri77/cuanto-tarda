# Informe de datos — «Lo que tarda la justicia» (cci-13)

Generado por `scripts/cgpj_fetch.py` + `scripts/cgpj_build.py` el 2026-10-01.

## 1. Punto de entrada real y por qué

**Fuente elegida: las "Series estadísticas" en XLSX del CGPJ**, publicadas dentro de
*Informes por territorios sobre la actividad de los órganos judiciales*:
<https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estudios-e-Informes/Informes-por-territorios-sobre-la-actividad-de-los-organos-judiciales/Informes-por-territorios-sobre-la-actividad-de-los-organos-judiciales>

- Formato: **XLSX** (11 ficheros, uno por métrica; nacional y "por Provincias"), una hoja
  por orden jurisdiccional (Total/Civil/Penal/Contencioso/Social) + hojas anuales 2001-2025
  + hoja `Introducción` con la definición oficial de cada tasa.
- Granularidad: **nacional + comunidad autónoma, por orden jurisdiccional, 2001-2025**;
  **provincias, total jurisdicciones, 2001-2025**. No hay serie por partido judicial ni por
  órgano individual en estas series (los informes por territorio en PDF sí bajan a órgano).
- Por qué esta y no otra: es la única publicación con **serie histórica completa y
  descargable en un solo fichero por métrica**, con las tasas ya calculadas por el CGPJ con
  su definición oficial. La "Base de datos PC-Axis" del CGPJ está anunciada para mayo de
  2027 (ciclo 1995-2026) y hoy no ofrece descarga directa navegable; los "Indicadores Clave"
  son trimestrales y sin serie larga.

**Medido** (descarga con `curl`, 2026-10-01, HTTP 200 en los 11 ficheros):

| Fichero | Peso | Tiempo |
|---|---|---|
| Series Asuntos.xlsx | 324 KB | 1,0 s |
| Series Asuntos por Provincias.xlsx | 588 KB | 0,8 s |
| Series Tasas de Congestion.xlsx / por Provincias | 244 KB / 404 KB | 1,0 s / 1,1 s |
| Series Tasas de Resolucion.xlsx / por Provincias | 244 KB / 404 KB | 1,0 s / 0,8 s |
| Series Tasas de Pendencia.xlsx / por Provincias | 244 KB / 412 KB | 1,2 s / 1,0 s |
| Series Tasa Litigiosidad.xlsx / por Provincias | 260 KB / 436 KB | 1,1 s / 1,6 s |
| Evolución Asuntos en trámite final (Total nacional) | 68 KB | 0,6 s |

Total ≈ **3,6 MB en ~12 s**. Todo cacheado en `raw/` (no versionado).

Población INE (solo para el derivado por habitante): serie Tempus tabla **31304**
("Cifras de población", ambos sexos, total edad, a 1 de enero), consultada por serie
(~KB por territorio, 53 territorios).

## 2. Registros leídos y descartados

- **24.575 celdas de datos leídas** de las hojas de serie histórica; **0 celdas vacías**
  en los rangos esperados (contadas por el build, el recuento se imprime
  por pantalla en cada ejecución del build).
- Territorios: **17 CCAA + fila España** (nacional) y **50 provincias**.
- Años: **2001-2025 completos** en todas las series (25 años, muy por encima del mínimo
  de 5).
- Descartes explícitos:
  - **Ceuta y Melilla no aparecen como filas** ni en las series por CCAA ni por provincias,
    pero sí están dentro del total España: en 2025, suma de CCAA = 7.487.816 ingresados
    frente a 7.550.806 del total España (diferencia 62.990 asuntos). No se puede desagregar
    Ceuta/Melilla desde estas series.
  - **Órganos centrales excluidos del total España** (Tribunal Supremo, Audiencia Nacional,
    juzgados centrales), según avisa la hoja Introducción del propio fichero.
  - **Duración media: NO está en estas series.** Ver §5.

## 3. Definiciones oficiales (texto literal del CGPJ, ver `data/sources.json`)

- **Tasa de congestión**: "Cociente donde el numerador está formado por la suma de los
  asuntos pendientes al inicio del periodo y los registrados en ese periodo y donde el
  denominador son los asuntos resueltos en dicho periodo."
- **Tasa de resolución**: "cociente entre los asuntos resueltos en el período e ingresados
  en el mismo."
- **Tasa de pendencia**: "Cociente entre los asuntos pendientes al final del período y los
  resueltos en ese período."
- **Tasa de litigiosidad**: "nº de asuntos ingresados por cada 1000 habitantes."

Son tres cosas distintas y no son intercambiables: resolución > 1 un año puede convivir con
congestión creciente si el stock heredado es alto.

## 4. Cifras principales (total jurisdicciones, datos CGPJ)

**España, serie anual** (`data/nacional_anual.json`):

| Año | Ingresados | Resueltos | En trámite (31-dic) | Congestión | Resolución |
|---|---|---|---|---|---|
| 2005 | 7.723.132 | 7.626.299 | 2.174.878 | 1,29 | 0,99 |
| 2015 | 8.478.731 | 8.658.440 | 2.435.792 | 1,28 | 1,02 |
| 2019 | 6.279.302 | 6.079.137 | 2.835.149 | 1,46 | 0,97 |
| 2020 | 5.529.954 | 5.228.031 | 3.161.755 | 1,60 | 0,95 |
| 2021 | 6.273.090 | 6.323.819 | 3.144.583 | 1,49 | 1,01 |
| 2022 | 6.685.301 | 6.460.255 | 3.396.066 | 1,52 | 0,97 |
| 2023 | 6.999.331 | 6.441.132 | 3.976.329 | 1,61 | 0,92 |
| 2024 | 7.799.799 | 7.291.564 | 4.519.343 | 1,61 | 0,94 |
| 2025 | 7.550.806 | 7.437.033 | 4.673.596 | 1,62 | 0,98 |

**Tendencia (respuesta a "¿entra más de lo que se resuelve?")**: desde 2023 entra más de lo
que se resuelve tres años seguidos (2023: +558.199; 2024: +508.435; 2025: +113.773), y el
stock de asuntos en trámite ha crecido cada año desde 2021: de 3,14 M a 4,67 M (**+48,6 %
en cuatro años**). La propia serie CGPJ de variación de la pendencia confirma el repunte:
+17,2 % (2023), +13,7 % (2024), +3,4 % (2025), frente a caídas de 2012-2016. En 2025 la
resolución mejora (0,985) y el crecimiento de la pendencia se frena, pero no baja.

**Por orden jurisdiccional, 2025** (`data/nacional_por_orden.json`):

| Orden | Ingresados | Resueltos | En trámite | Congestión | Resolución |
|---|---|---|---|---|---|
| Civil | 3.287.980 | 3.308.215 | 2.672.464 | 1,81 | 1,01 |
| Penal | 3.550.118 | 3.451.206 | 1.255.950 | 1,35 | 0,97 |
| Contencioso | 198.961 | 212.680 | 219.492 | 2,00 | 1,07 |
| Social | 513.628 | 464.827 | 525.652 | **2,14** | **0,90** |

Lo social es hoy el orden más congestionado (2,14) y el único que resuelve claramente menos
de lo que entra (0,90). La litigiosidad nacional 2025: **153,74 asuntos/1.000 hab**.

**CCAA 2025** (`data/ccaa.json`): más congestión — Murcia (1,95), Castilla-La Mancha
(1,84), Madrid (1,72), Andalucía (1,62); menos — Aragón (1,37), Asturias y Navarra (1,38).

**Provincias 2025, pendientes por 1.000 habitantes** (DERIVADO, método en §6; campo
`en_tramite_por_1000_hab_derivada`): Murcia 137,7, Gipuzkoa 125,0, Toledo 118,7, Madrid y
Santa Cruz de Tenerife 113,7. Menos: ver `data/provincias.json`.

## 5. Duración media de los procedimientos

**No está publicada en las series XLSX** ni como serie descargable. El CGPJ la publica como
*estimación* en una herramienta interactiva de Transparencia ("Estimación de los tiempos
medios de duración de los procedimientos judiciales", por tipo de órgano, orden,
procedimiento, año y territorio, últimos 10 años, en meses):
<https://www.poderjudicial.es/cgpj/es/Temas/Transparencia/ch.Estimacion-de-los-tiempos-medios-de-duracion-de-los-procedimientos-judiciales.formato1?anio=2024>
El propio CGPJ avisa: es una "estimación obtenida por medio de un modelo matemático a partir
de las cifras de asuntos ingresados, resueltos y en trámite", no un dato observado. **No se
incluye en los agregados** y no se ha calculado ninguna duración por nuestra cuenta. Si el
episodio la quiere citar, que sea desde esa herramienta con su cautela.

## 6. Derivados por habitante (etiquetados como DERIVADO)

- INE Tempus (tabla 31304) publica población provincial a 1 de enero **solo hasta 2022**
  (verificado: último dato 1-1-2022, tanto en `DATOS_SERIE` como en `DATOS_TABLA`; las
  jaxiT3 del Censo Anual 2021-2025 no tienen descarga programática accesible — devuelven
  página HTML de error 599 en `/jaxiT3/files/t/es/67988.px`).
- Por eso: hasta 2022, `en_tramite_por_habitante` = en_trámite ÷ población INE.
  Desde 2023, `en_tramite_por_1000_hab_derivada` = (en_trámite ÷ ingresados) ×
  tasa_litigiosidad, **todo publicado por el CGPJ** (equivale a usar la población que el
  propio CGPJ emplea para su litigiosidad).
- Contraste entre métodos en 2022 (Albacete): 65,6 por 1.000 hab (INE) vs 65,9 (derivada
  CGPJ): diferencia 0,5 %. Coherentes.

## 7. Verificación manual contra publicaciones del CGPJ

1. Nota de prensa CGPJ 30-03-2026 ("Los órganos judiciales recibieron en 2025 un 3,2 %
   menos asuntos…"): cifra publicada **7.550.806 ingresados** y **7.437.033 resueltos** →
   nuestro `nacional_anual.json` 2025: **7.550.806 / 7.437.033**. ✅ Coincide exacto.
2. Misma nota: litigiosidad nacional 2025 **"153,70 asuntos por cada 1.000 habitantes"** →
   fichero CGPJ y nuestro agregado: **153,7389** (la nota redondea a 153,70). ✅
3. Nota TSJ Cantabria 09-04-2026 ("resolvieron en 2025 un 4 % más asuntos que los que
   entraron") → Cantabria 2025: 84.323 resueltos ÷ 81.196 ingresados = **1,0385 (+3,9 %)**. ✅
4. Recalculo de definiciones sobre los ficheros (España 2025):
   congestión (4.519.343 + 7.550.806) ÷ 7.437.033 = **1,6231** vs publicada **1,623**;
   resolución 7.437.033 ÷ 7.550.806 = **0,9849** vs publicada **0,9849**; pendencia
   4.673.596 ÷ 7.437.033 = **0,6284** vs publicada **0,6284**. ✅ Las tasas del fichero son
   exactamente las de su definición oficial.

## 8. Trampas documentadas

1. **Definiciones mal copiadas por el CGPJ**: los ficheros "Tasas de Congestion por
   Provincias" y "Tasas de Pendencia por Provincias" llevan en su hoja Introducción la
   definición de la tasa de *resolución* (error evidente de copy-paste). Los valores sí
   corresponden a la tasa del título del fichero: verificado numéricamente (§7.4 para
   congestión nacional; en provincias, p. ej. Albacete 2025: (35.462+48.275)÷47.692=1,7558
   vs 1,7558 publicada).
2. **España ≠ suma de CCAA**: el total España incluye Ceuta y Melilla, que no aparecen
   como filas propias (diferencia 2025: 62.990 ingresados). Y excluye los órganos
   centrales (TS, AN, juzgados centrales).
3. **Ceuta y Melilla sin serie territorial** en estas publicaciones: imposible compararlas
   con el resto de territorios.
4. **Provincias sin desglose por orden** en la serie histórica (solo total jurisdicciones);
   el desglose por orden existe solo a nivel CCAA/nacional.
5. **Población INE**: hasta 2022 son estimaciones intercensales con decimales (p. ej.
   Albacete 2022: 387.759,51); los años recientes se marcan Provisionales. El derivado por
   habitante hereda esa incertidumbre; para 2023-2025 usa la población implícita del CGPJ.
6. **2025: definitivo o provisional** — el CGPJ publicó los datos anuales 2025 el 30-03-2026
   como cierre anual (calendario de publicaciones: "Informes estadísticos por territorios
   Anual 2026" saldrá en marzo de 2027); los ficheros no marcan los datos de 2025 como
   provisionales, pero si el CGPJ los revisa, la serie se reejecuta y cambia (los scripts
   son reejecutables y no guardan nada transformado fuera de `data/`).
7. **Cambios de planta/denominación**: estas series agregan por territorio y orden, no por
   órgano, así que los cambios de denominación de órganos no las rompen; pero sí afecta la
   comparación de años si se crean o suprimen juzgados (p. ej. OFIM en 2021 hizo saltar el
   ingresado penal de 2021: caída de 8,37 M a 6,27 M entre 2010 y 2021 es también efecto
   de la desjudicialización, no solo de "menos litigio"). Se recomienda no presentar 2001-
   2025 como una comparación homogénea de causas sin esta cautela.
8. **Órganos con cero asuntos**: no aplica aquí (no hay datos por órgano); en la serie por
   provincias no hay celdas vacías.
