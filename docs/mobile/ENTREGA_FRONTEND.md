# Entrega inicial del frontend móvil

## Lo implementado

| Área | Flujos |
|---|---|
| Acceso | Registro, login, validación, mostrar/ocultar password, restauración de sesión y logout local |
| Perfil | Onboarding en tres pasos y edición de datos, objetivo, experiencia, días, duración, equipo y disciplina |
| Inicio | Plan más reciente, resumen de nutrición del día y métricas de progreso |
| Entreno | Catálogo de planes, sesiones y splits; generación inicial; calendario por semanas y días |
| Ejecución | Registro de series reales por repeticiones, tiempo o distancia; carga y RPE; cronómetro y descanso |
| Sesiones propias | Crear ejercicios, crear sesiones, duplicar oficiales y editar una sesión privada |
| Historial | Registro completo/parcial/omitido; prescripción frente a resultados y sugerencias de progresión |
| Nutrición | Catálogo, alimentos propios, registro por gramos/porciones, eliminación de comidas y consulta por fecha |
| Metas | Estimación vista previa y guardado explícito de calorías/macros |
| Progreso | Peso por fecha, evolución relativa y lista de sesiones registradas |
| Demostración | Experiencia separada con estado en memoria y señalización constante de datos de ejemplo |

## Diseño

Interfaz en español, fondo oscuro y acentos verde lima/mint. Cinco pestañas: Inicio, Entreno, Nutrición, Progreso y Perfil. Componentes compartidos para tarjetas, formularios, errores, vacíos, cargas y botones.

La vista web incluida es una compilación del mismo código React Native. Las capturas disponibles en `screenshots/` corresponden a esa vista en un tamaño de 390 × 844; no son fotografías de un dispositivo nativo.

## Arquitectura

- `App.tsx`: navegación y proveedores.
- `src/state/Session.tsx`: sesión, restauración y perfil.
- `src/lib/api.ts`: cliente tipado, Bearer, timeout, errores, paginación y 401.
- `src/lib/storage.ts`: SecureStore nativo; en web, el token permanece solo en memoria.
- `src/lib/demo.ts`: datos y operaciones de ejemplo; nunca llama a la API.
- `src/screens/`: pantallas de cada flujo.
- `src/components/ui.tsx` y `src/theme.ts`: sistema visual compartido.
- `tests/core.test.ts`: pruebas de lógica y comunicación.
- `scripts/e2e-web.cjs`: recorrido contra FastAPI con SQLite aislado.

TanStack Query administra caché, cargas y recargas. La caché se vacía al cambiar de sesión; las escrituras invalidan los datos relacionados. La identidad y los permisos definitivos se validan en el backend.

## Verificación realizada

- TypeScript estricto sin errores, incluyendo control de variables sin uso.
- 11 pruebas unitarias/de cliente pasaron.
- Exportación web y paquetes JavaScript/Hermes para Android e iOS completada. Esto verifica la compilación; no produce un APK/IPA ni sustituye las pruebas en dispositivos.
- Flujos de interfaz contra el backend real usando SQLite temporal: registro, login, perfil, generación de plan, ejecución e historial, sugerencias, comidas, macros y peso.
- Se verificó la creación y edición de sesiones propias después de corregir una carrera al cargar el editor.
- Navegación de demostración y revisión de capturas de Inicio y Nutrición.
- No se observaron errores de JavaScript en el recorrido completo.

## Pendiente para una app publicable

1. Ejecutar y revisar Android/iOS reales: teclado, áreas seguras, navegación atrás, SecureStore, accesibilidad, red y ciclo de vida.
2. Repetir la integración con PostgreSQL en la PC principal.
3. Añadir recuperación de contraseña, verificación de email, refresh/revocación de sesiones y gestión/eliminación de cuenta al backend y cliente.
4. Incorporar editores avanzados de splits/planes, activación de un plan con fecha inicial, cambios de fases y selección de entrenamiento por fecha.
5. Guardar borradores y una cola de registros offline. Actualmente, cerrar una pantalla puede perder un borrador sin guardar; el modo real necesita conexión.
6. Añadir historial/versionado completo de plantillas, contenido compartido, recursos multimedia y automatización avanzada.
7. Sustituir catálogo demo y revisar reglas deportivas/nutricionales con profesionales.
8. Ajustar icono final, pantalla de arranque, identificadores de tienda, HTTPS, builds, privacidad y publicación.

La app maneja los access tokens existentes. Al recibir un 401, limpia la sesión y pide entrar de nuevo; no inventa un endpoint de refresh que el backend aún no tiene. Logout elimina la sesión del cliente, pero no revoca el JWT en el servidor.

La vista de peso utiliza una escala relativa etiquetada; el peso no se presenta como única medida de progreso. Las estimaciones nutricionales se revisan antes de guardarlas. El registro de entrenamiento exige marcar lo realizado; no convierte la prescripción automáticamente en un resultado.

## Fuentes técnicas

- Expo: https://docs.expo.dev/get-started/create-a-project/
- Expo SecureStore: https://docs.expo.dev/versions/latest/sdk/securestore/
- Versiones nativas alineadas con `expo/bundledNativeModules.json` del SDK instalado y fijadas por `package-lock.json`.
