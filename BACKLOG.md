# Backlog — unmsm-admision-stats

## Hecho
- [x] 2026-10-28 — 2027-I completo (95 escuelas, 28,829 postulantes, 2,474 ingresantes; 4 carreras nuevas) + seccion 'Examen 2027-I' al inicio del dashboard (cierres vs 2026-I, competencia, tabla 95 escuelas).
- [x] 2026-10-26 — Scrapeado 2027-I (Website20271): por ahora solo EBR/EBA publicada, 80 escuelas, 18,878 postulantes, 2,133 ingresantes (8.9 pos/vac). Faltan escuelas de Salud (Medicina, Psicologia, Enfermeria, Odontologia...) — probablemente examen/publicacion en otra fecha.
- [x] 2026-08-26 — Historico scrapeado de la OCA: 5 procesos (2024-1 a 2026-2), agregados por escuela x modalidad en historico/unmsm_historico.json. Validado vs dataset oficial 2026-1 (notas 95/95 exactas).
- [x] 2026-08-25 — GA4 instalado (G-GZQH73GDY4); evento support_click del boton BMC ya activo.
- [x] 2026-08-21 — Dashboard v1 desplegado: resumen, heatmap de cierres por escuela (EBR vs Pre), competencia, modalidades, vacantes sin cubrir, FAQ. Favicon + OG vino/dorado. Yape/BMC.
- [x] 2026-08-21 — Repo + pipeline: dataset oficial agregado 2026-1 (95 escuelas x modalidad, vacantes/postulantes/ingresantes/notas). Parseo de notas con decimal reconstruido (la fuente quita el punto decimal y agrupa con miles). stats.json validado (notas 428-1679, min<=max).

## Pendiente
- [ ] Re-scrapear 2027-I si publican otras modalidades (traslados, Pre-San Marcos...) (borrar .cache_scrape/Website20271* antes).
- [ ] Integrar historico al dashboard (evolucion de cierres y competencia por proceso).
- [ ] 2025-2: no esta en linea (Website20252 = 404); intentar via Wayback Machine.

## Notas
- La web de resultados marca "ALCANZO VACANTE" para todos los que cubrieron vacante;
  la columna Ingresantes del CSV oficial 2026-1 es menor (parece contar matriculados
  efectivos). Las notas max/cierre si coinciden exactamente entre ambas fuentes.
- Modalidades especiales (traslados, primeros puestos, etc.) usan otra escala de
  puntaje (notas bajas tipo 83-500 son normales ahi).
