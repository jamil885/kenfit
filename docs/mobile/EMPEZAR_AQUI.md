# KenFit móvil — empieza aquí

El código móvil está en `mobile/`. Usa Expo SDK 57, React Native y TypeScript. La navegación, formularios y cliente API están implementados; la validación final en dispositivos Android/iOS y PostgreSQL sigue pendiente.

## 1. Verlo en tu laptop sin instalar Node ni Docker

Se incluye una vista web compilada en `mobile/preview`. Desde la raíz del repositorio, en tu laptop Linux:

```bash
python3 -m http.server 8081 --directory mobile/preview
```

Abre **http://127.0.0.1:8081** y pulsa **Explorar demostración**.

- No necesitas levantar el backend.
- La demostración usa datos de ejemplo y no envía información al servidor.
- Puedes navegar por las pantallas, registrar comidas, pesos y sesiones de ejemplo.
- Los cambios duran hasta que vuelvas a entrar a la demostración o recargues la página.
- La plantilla del modo demostración es de fuerza. Las otras disciplinas requieren conectar el backend real.
- Esta vista previa usa `http://127.0.0.1:8000` para los flujos reales. En tu laptop, úsala como demostración mientras el backend no esté disponible.

En Windows puedes usar `py -3 -m http.server 8081 --directory mobile/preview`.

No abras `index.html` directamente como archivo: sirve la carpeta con el comando anterior para que carguen los recursos.

## 2. Ejecutar el código móvil en tu PC principal

Requisitos: Node.js 24 LTS (24.3 o posterior) y un Expo Go compatible con el SDK del proyecto, o un development build. Se incluyó `package-lock.json`; usa `npm ci` para reproducir las versiones verificadas.

```powershell
cd mobile
npm ci
Copy-Item .env.example .env
```

Si ya tienes `.env`, edítalo sin sobrescribirlo.

Para el navegador de la misma PC:

```dotenv
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
```

Para un teléfono físico en la misma red que tu PC, sustituye esa dirección por la IPv4 de la PC:

```dotenv
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```

Ese número es un ejemplo. Consulta tu dirección real con `ipconfig`.

Desde `backend`, con el entorno activado y la base migrada:

```powershell
uvicorn app.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Permite la conexión del teléfono en tu red privada si el firewall de Windows la bloquea. Usa esta exposición a la LAN solo para desarrollo.

Para probar desde un navegador, configura también en el `.env` del backend:

```dotenv
CORS_ORIGINS=["http://localhost:8081","http://127.0.0.1:8081"]
```

Ajusta el puerto/origen si Expo muestra otra URL. CORS corresponde al navegador; el teléfono necesita alcanzar la IP y el puerto del servidor.

Desde `mobile`:

```powershell
npm start -- --clear --max-workers 2
```

Escanea el QR con un Expo Go compatible. También puedes iniciar la vista web:

```powershell
npm run web -- --clear --max-workers 2
```

En el emulador Android, la dirección del host suele ser `http://10.0.2.2:8000`. En un teléfono, `localhost` apunta al propio teléfono y no a tu PC.

Windows puede ejecutar el cliente y un emulador Android. El simulador nativo de iOS requiere macOS; el código iOS se puede revisar con un dispositivo compatible o un build externo en una etapa posterior.

Reinicia Metro con `--clear` al cambiar la URL del backend. Las variables `EXPO_PUBLIC_*` se incluyen en el cliente: no contienen claves privadas, secretos JWT ni contraseñas de base de datos.

## 3. Flujo que debes probar en el teléfono

1. Registrar una cuenta y entrar.
2. Completar los tres pasos del perfil.
3. En Entreno, generar el plan inicial y abrir una sesión.
4. Ajustar resultados y marcar series realizadas; guardar la sesión.
5. Verla en Progreso y revisar sugerencias de progresión.
6. En Nutrición, guardar metas y registrar una comida por gramos o porciones.
7. Crear un alimento propio a partir de su etiqueta.
8. Crear y editar una sesión propia. Para personalizar una oficial, guarda primero una copia.
9. Guardar el peso de hoy y comprobar el historial.
10. Cerrar sesión y volver a entrar. Verificar el comportamiento al expirar el token.

Recuerda que el catálogo nutricional del backend contiene valores aproximados de demostración. Sustituirlos por datos verificados antes del lanzamiento.

## 4. Verificaciones del código

Desde `mobile`:

```powershell
npm run typecheck
npm test
npm run format:check
```

La suite de 11 pruebas cubre fechas, cantidades, headers de autenticación, errores, cierre de sesión, paginación y separación de datos demo.

### Prueba completa en navegador contra el backend

Primero instala las dependencias del backend en `backend/.venv`, como explica la guía de Windows. Luego, desde `mobile`:

```powershell
npx playwright install chromium
npm run test:e2e
```

El script:

- Crea una base SQLite temporal, aplica migraciones y seed.
- Compila una vista web de prueba con un puerto local separado.
- Arranca su propia API y servidor estático en puertos libres.
- Recorre demostración, registro, perfil, plan, sesión, historial, comidas, metas, peso y edición de sesiones.
- No utiliza la base `kenfit` ni un backend que tengas ejecutándose.
- Guarda capturas en `docs/mobile/screenshots`.

Si tu Python de pruebas está en otra ruta:

```powershell
$env:KENFIT_PYTHON="C:\ruta\backend\.venv\Scripts\python.exe"
npm run test:e2e
Remove-Item Env:KENFIT_PYTHON
```

Este recorrido utiliza SQLite; las pruebas de PostgreSQL siguen en `docs/PRUEBAS_PC_WINDOWS.md`.

## 5. Integrar la entrega

El ZIP incluye backend y frontend juntos. Conserva la carpeta `.git`, tus `.env` y el volumen PostgreSQL al copiar los cambios sobre tu clon.

No se subió nada a GitHub ni se publicó una app en las tiendas. Revisa el código, valida en tu PC y crea el commit cuando los flujos funcionen allí.
