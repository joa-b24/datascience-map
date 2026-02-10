 # Decisiones

## Arquitectura: híbrida MD + índice YAML
- Los MD son la fuente de verdad para el contenido detallado de cada nodo.
- `index/*.yaml` es la fuente de verdad para metadatos y relaciones.

## Tipos mínimos de nodo
Dominio (Domain), Tema (Topic), Herramienta (Tool), Proyecto (Project), Artifact, Certificación (Certification)

## Relaciones mínimas
`BELONGS_TO`, `USES`, `COVERS`, `HAS`, `PREREQ` (usar con moderación)

## Inventario
`inventory/*` contiene borradores y backlog que pueden convertirse en nodos más adelante.

