# unmsm-admision-stats

Estadísticas agregadas de la admisión a la Universidad Nacional Mayor de San Marcos (UNMSM), proceso 2026-1.

- Fuente: dataset oficial agregado en la [Plataforma Nacional de Datos Abiertos](https://www.datosabiertos.gob.pe/dataset/proceso-de-admisi%C3%B3n-de-pregrado-2026-1) (sin datos personales).
- Pipeline: `build_stats.py` -> `data/stats.json`.
- Histórico: `scrape_historico.py` agrega las páginas públicas de resultados de la OCA (`admision.unmsm.edu.pe/Website{proc}`) -> `historico/unmsm_historico.json`. Cubre 2024-1, 2024-2, 2025-1, 2026-1 y 2026-2; solo agregados por escuela x modalidad (postulantes, ingresantes, nota máxima y de cierre), sin datos personales. Validado contra el dataset oficial 2026-1: notas de cierre y máximas coinciden 95/95 escuelas.
- Dashboard: `index.html` (GitHub Pages).

Proyecto independiente sin afiliación con la UNMSM. Hermano de [uni-admision-stats](https://github.com/unimauro/uni-admision-stats) y [unsa-admision-stats](https://github.com/unimauro/unsa-admision-stats).
