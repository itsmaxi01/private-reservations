# Análisis de dominio — iteración 1

## Requisitos consistentes

- `Reservation` es una sola entidad compartida. `created_by` expresa autoría,
  no propiedad ni visibilidad.
- La relación entre `WatchItem` y `Reservation` es uno a muchos. No se debe
  imponer unicidad sobre `Reservation.watch_item_id`.
- `created_by`/`added_by` son claves foráneas obligatorias. La identidad se
  recibirá del mecanismo de autenticación, no del cuerpo de la petición.
- El límite semanal aplica globalmente a las reservas `DATE`; una consulta por
  creador sería incorrecta.
- `watch_item_id` es nullable en la tabla porque comparte entidad con `DATE`.

## Reglas reservadas para servicios

La capa de servicio deberá validar, dentro de la misma transacción:

1. que la combinación local de `date` y `time` no esté en el pasado;
2. forma de `DATE`: `title` y `reason` presentes, `watch_item_id` ausente;
3. máximo global de dos `DATE` entre lunes y domingo;
4. forma de `WATCH`: WatchItem existente, lunes/miércoles/viernes y hora a
   partir de las 22:40;
5. bloqueo de borrado de un WatchItem con reservas futuras;
6. existencia del usuario autor para cualquier creación.

La fecha y hora se interpretarán en `America/Mexico_City`. Un WatchItem en
estado `WATCHED` sigue siendo elegible para una nueva reservación `WATCH`.
Además, una reservación `WATCH` debe rechazar `title` y `reason` si el cliente
los envía; no se ignorarán silenciosamente.

### Concurrencia del límite semanal

La estrategia elegida es adquirir un bloqueo transaccional de PostgreSQL antes
de contar y crear una reserva `DATE`:

1. calcular el lunes correspondiente a la fecha solicitada;
2. derivar una clave estable a partir de ese lunes;
3. ejecutar `pg_advisory_xact_lock` con esa clave;
4. contar globalmente las reservas `DATE` de lunes a domingo;
5. rechazar si ya hay dos o insertar dentro de la misma transacción.

El bloqueo se libera automáticamente al confirmar o revertir la transacción.
Esto serializa únicamente las creaciones que compiten por la misma semana, no
requiere una tabla auxiliar y evita implementar reintentos de transacciones con
nivel `SERIALIZABLE`.

### Decisiones adicionales confirmadas

- No se permiten duplicados con el mismo título —ignorando mayúsculas y
  espacios externos— y el mismo tipo. Esto incluye elementos archivados: deben
  restaurarse, no duplicarse.
- Los WatchItems se archivan mediante `archived_at`; no se borran físicamente.
- El cambio a `WATCHED` es manual y no impide futuras reservas.
- Una reserva nueva debe ser estrictamente posterior al momento actual.
- No se editan reservas pasadas ni se cambia `DATE` por `WATCH` o viceversa.
- Solo `ADMIN` puede eliminar reservaciones y mensajes. El rol `MEMBER` conserva
  las demás capacidades compartidas. El rol no se acepta desde schemas públicos.
- Los correos se normalizan a minúsculas y tienen unicidad en base de datos
  ignorando mayúsculas y espacios externos.

Estas reglas no están en routers. Tampoco se duplican por usuario.

## Ambigüedades que conviene resolver

1. **Actualizaciones futuras.** Falta definir qué campos de una reservación
   futura pueden editarse y si el contenido de un mensaje puede modificarse.
2. **Eliminación administrativa.** Falta decidir si las reservaciones y mensajes
   eliminados por `ADMIN` desaparecen físicamente o también se archivan.
3. **Dos usuarios exactos.** No está definido cómo se aprovisionan ni si la base
   debe impedir un tercero. Esto debe resolverlo la estrategia de autenticación,
   no una restricción frágil de la tabla `users`.

## Estado de implementación

Ya existen migraciones, repositorios, servicios, API autenticada y frontend.
Las tablas se crean exclusivamente mediante Alembic, no al arrancar FastAPI.
Queda pendiente validar el sistema contra un proyecto Supabase/PostgreSQL real y
completar el despliegue con credenciales externas.
