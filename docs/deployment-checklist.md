# Checklist de despliegue

## Supabase

- [ ] Proyecto creado en una región adecuada.
- [ ] Registro público desactivado.
- [ ] Dos usuarios invitados y correos confirmados.
- [ ] Signing keys asimétricas habilitadas.
- [ ] SMTP configurado para entregar Magic Links/OTP a ambos usuarios.
- [ ] Site URL y Redirect URLs configuradas.
- [ ] Cadena del pooler de sesión copiada con SSL habilitado.

## Render

- [ ] Repositorio publicado en GitHub.
- [ ] Blueprint creado desde `render.yaml`.
- [ ] `DATABASE_URL`, `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` configuradas.
- [ ] `ADMIN_EMAIL` y `MEMBER_EMAIL` configurados y distintos.
- [ ] Build y migración inicial completados.
- [ ] `/api/health` responde `200`.

## Aceptación

- [ ] Ambos usuarios reciben el enlace de acceso.
- [ ] El primer acceso crea exactamente un `ADMIN` y un `MEMBER`.
- [ ] Ambos ven los mismos datos.
- [ ] `MEMBER` recibe `403` al intentar eliminar o archivar.
- [ ] La tercera reserva `DATE` de una semana recibe `409`.
- [ ] Una reserva `WATCH` inválida recibe `400`.
- [ ] Cerrar sesión elimina el acceso a la API.
