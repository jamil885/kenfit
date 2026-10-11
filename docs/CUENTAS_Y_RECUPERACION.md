# Recuperación de contraseña y eliminación de cuenta

## Actualizar la PC

Detener la API, obtener un respaldo como en `INTEGRACION_PC.md`, descargar la rama y ejecutar desde `backend` con el entorno virtual activo:

```powershell
python -m pip install -r requirements-lock.txt
python -m alembic upgrade head
```

La revisión nueva es `b37a84d915c2`. La base ya convertida en `9c4a10b2d7ef` solo necesita esta migración; **no repetir `app.migrate_pc`**. Añade versión de sesión, códigos de recuperación hasheados y límites persistentes. Para bases antiguas `fea8b9182489`, seguir primero la guía de conversión; el conversor ya utiliza la nueva revisión final.

## Prueba local sin proveedor de correo

Añadir en `backend/.env`:

```env
APP_ENV=development
MAIL_MODE=file
MAIL_OUTBOX=.local-mail
```

Reiniciar API y Expo. En Acceso → Olvidé mi contraseña, solicitar un código para una cuenta de prueba existente. Los mensajes se escriben en `backend/.local-mail/*.eml`; abrir el más reciente desde el explorador y copiar únicamente su código al formulario. No se envía correo real en este modo. No mostrar códigos ni compartir esos archivos. La carpeta está ignorada por Git; se intenta crear con permisos privados y debe quedar bajo el usuario de Windows.

Introducir la nueva contraseña dos veces y guardar. Comprobar que el código no funciona de nuevo, la contraseña anterior ya no entra y las sesiones anteriores vencen. No inicia sesión automáticamente. También se genera una notificación de cambio de contraseña.

## Correo para la beta

Configurar un proveedor SMTP real en el servidor: `MAIL_MODE=smtp`, `APP_ENV=production`, `SMTP_HOST`, `SMTP_PORT` (587 por defecto), `SMTP_USER`, `SMTP_PASSWORD` y `SMTP_FROM` con un remitente verificado. Se exige STARTTLS con verificación de certificado. No guardar credenciales en Git. El modo file se rechaza en producción; disabled devuelve 503 al solicitar recuperación.

El endpoint responde el mismo mensaje para cuentas existentes y ausentes; el correo se entrega después de la respuesta. Código aleatorio de 256 bits, hash SHA-256 en base de datos, vencimiento 15 minutos y consumo atómico. Cambiar contraseña invalida todos los códigos pendientes y JWT anteriores mediante token_version. Los JWT antiguos sin versión continúan funcionando mientras la versión de la cuenta sea 0.

Límites en base de datos: hasta 3 correos por dirección/hora, 20 solicitudes por IP/hora y 20 intentos de restablecimiento por IP/hora. No se confía en cabeceras X-Forwarded-For arbitrarias. Antes de desplegar tras un proxy, configurar en Uvicorn los proxies de confianza; de lo contrario las solicitudes pueden compartir la IP del proxy. Las claves de límite están hasheadas con HMAC y los registros caducados se limpian durante nuevas solicitudes.

La entrega SMTP es síncrona en una tarea de fondo con timeout; no es una cola durable. Los fallos se registran sin correos, tokens ni credenciales. Para producción añadir monitoreo de entrega y una cola con reintentos si el volumen lo requiere. Probar entregabilidad real y spam antes de invitar al equipo.

## Eliminación de cuenta

Perfil → Eliminar mi cuenta requiere contraseña actual y escribir ELIMINAR. Utilizar una **cuenta de prueba**: es una eliminación real, no una desactivación.

Borra perfil, comidas, metas, peso, logs/resultados, sesiones, códigos y plantillas privadas. Conserva catálogo oficial y usuarios ajenos. Limpia referencias parent_id a contenido eliminado. También busca los esquemas `kenfit_pc_*` y borra los datos de la misma cuenta por email; todas esas operaciones comparten la transacción. Si aparece una referencia incompatible, falla y revierte en vez de borrar datos de otro usuario. No existe aún cambio de email; si se añade, actualizar la identificación de archivos de esquema.

En modo local se limpian también los mensajes de esa cuenta del buzón. Los dumps externos, backups del proveedor y registros de entrega SMTP necesitan una política operacional de retención/eliminación: la aplicación no puede borrar copias fuera de su almacenamiento activo. Si se restaura un respaldo, aplicar las solicitudes de eliminación posteriores antes de habilitar acceso. Antes de una beta pública, definir ese procedimiento y comunicar la retención en la política de privacidad.

## Límites actuales

Sin refresh tokens, recuperación por enlace profundo, MFA o verificación de correo. La pantalla usa un código que se pega desde el correo. Logout normal sigue siendo local; restablecer contraseña sí invalida JWT del servidor. La demostración oculta eliminación de cuenta; la recuperación se usa solo en el acceso real. La vista `mobile/preview` es un artefacto anterior: usar Expo o regenerar el export web para ver estas pantallas nuevas.

Referencia de diseño: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
