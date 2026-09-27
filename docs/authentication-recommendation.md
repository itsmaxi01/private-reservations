# Recomendación de autenticación

## Elección

Usar **Supabase Auth** con acceso passwordless por correo —Magic Link u OTP— y
Supabase PostgreSQL para la base de datos.

Para esta aplicación reduce proveedores e infraestructura: el mismo proyecto
proporciona PostgreSQL y autenticación. FastAPI y SQLAlchemy siguen siendo el
backend y la capa de persistencia; no se sustituyen por la API generada de
Supabase.

## Flujo propuesto

1. Invitar únicamente a los dos usuarios autorizados y desactivar el registro
   público.
2. El frontend inicia sesión mediante Magic Link u OTP.
3. Envía el access token en `Authorization: Bearer <token>` a FastAPI.
4. FastAPI valida firma, emisor, audiencia y expiración mediante el JWKS público
   de Supabase.
5. El claim `sub` se relaciona con el usuario local mediante un identificador
   externo único que se añadirá al integrar autenticación.
6. FastAPI obtiene `created_by` del usuario autenticado; nunca se acepta desde
   el cuerpo de la petición.
7. FastAPI consulta el rol local `ADMIN`/`MEMBER`; no confía en un rol enviado
   por el navegador.

## Límites y costes operativos

- La integración está implementada, pero necesita un proyecto Supabase y sus
  variables de entorno para probarse de extremo a extremo.
- El plan gratuito de Supabase puede pausar proyectos tras inactividad.
- La entrega de correos passwordless en producción puede requerir SMTP propio.
