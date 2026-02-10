# Hoja de ruta (10 días completos)

## Objetivo
Construir un mapa de conocimiento (knowledge map) funcional: navegar por Dominios/Temas/Herramientas/Proyectos y encontrar evidencias (Artifacts), con validación y exportación a JSON listo para la interfaz.

---

## Día 1 — Configuración y convenciones
Entregables:
- [ ] Repositorio con estructura mínima completa (`schema/`, `index/`, `nodes/`, `inventory/`, `scripts/`, `build/`, `docs/`)
- [ ] `schema/*` definido y estable
- [ ] Convención de IDs (snake_case)
- [ ] `index/nodes.yaml` y `index/edges.yaml` inicializados correctamente

Definición de “hecho”:
- `python scripts/validate_graph.py` se ejecuta y pasa (aunque haya pocos nodos).

---

## Día 2 — Seed mínimo del sistema
Entregables:
- [ ] 3 dominios (MD + índice)
- [ ] 10 temas (MD + índice) distribuidos en esos dominios
- [ ] 6 herramientas (MD + índice)

Regla:
- Cada MD debe tener al menos 5 líneas (definición, bullets y enlaces placeholder)
- Cada nodo en el índice debe incluir `id,type,name,status,path` correctamente

Comprobación:
- Validación pasa
- `python scripts/stats.py` muestra conteos no nulos

---

## Día 3 — Proyectos núcleo (catálogo)
Entregables:
- [ ] 5 proyectos (MD + índice)
- [ ] Cada proyecto usa al menos 2 herramientas (aristas `USES`)
- [ ] Cada proyecto cubre al menos 2 temas (aristas `COVERS`)

Comprobación:
- Ningún proyecto queda sin aristas `USES`
- `COVERS` empieza a conectar el mapa

---

## Día 4 — Artifacts como evidencia
Entregables:
- [ ] 10 artifacts (MD + índice)
- [ ] Cada artifact incluye `artifact_type` en su MD
- [ ] Al menos una arista `HAS` por proyecto hacia un artifact
- [ ] Cada artifact `COVERS` ≥ 1 tema o herramienta

Comprobación:
- `stats.py` muestra "Projects with no HAS->Artifact edges" cercano a 0

---

## Día 5 — Certificaciones y organización
Entregables:
- [ ] 2–5 certificaciones (MD + índice)
- [ ] Relaciones `COVERS` desde certificaciones a temas/herramientas relevantes
- [ ] `inventory/*` con backlog real y priorizado

Comprobación:
- No hay temas huérfanos críticos en "orphan topics" (o queda justificado)

---

## Día 6 — Limpieza semántica del grafo
Entregables:
- [ ] Revisar nombres de temas (evitar duplicados)
- [ ] Añadir `PREREQ` solo donde aporte (máx. 1–3 por tema)
- [ ] Normalizar `tags` y `status`

Comprobación:
- Validación pasa sin advertencias graves
- ~80% de nodos tienen `status` (planned/in_progress/solid)

---

## Día 7 — Export para la UI
Entregables:
- [ ] `python scripts/export_json.py` genera `build/graph.json`
- [ ] `graph.json` contiene los campos necesarios (id,type,name,path,edges)

Comprobación:
- Export reproducible con un único comando

---

## Día 8 — Primer boceto de UI (mínimo)
Entregables:
- [ ] Decidir stack UI (D3 / React / etc.)
- [ ] Viewer mínimo que:
  - cargue `build/graph.json`
  - liste nodos por tipo
  - permita abrir el MD o ver su contenido

Comprobación:
- Navegación básica funcional

---

## Día 9 — Ajustes de UX
Entregables:
- [ ] Búsqueda por `name`/`tags`
- [ ] Filtros por `Domain`, `type`, `status`
- [ ] Vista de "vecinos" (nodos conectados)

---

## Día 10 — Cierre y checklist para portafolio
Entregables:
- [ ] Lista "Top 5 Projects" con puntos destacados
- [ ] 20–30 temas sólidos conectados a evidencia
- [ ] Decisiones documentadas en `docs/decisions.md`
