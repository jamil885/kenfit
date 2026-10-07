# KenFit móvil

Aplicación Expo + React Native + TypeScript, conectada al backend FastAPI del monorepo.

**Empieza por [la guía](../docs/mobile/EMPEZAR_AQUI.md).**

## Vista ligera, sin Node ni backend

Desde la raíz del repositorio:

```bash
python3 -m http.server 8081 --directory mobile/preview
```

Abre http://127.0.0.1:8081 y elige **Explorar demostración**.

## Desarrollo

```bash
npm ci
# Copia .env.example a .env y configura la URL de la API.
npm start -- --clear --max-workers 2
```

## Validación

```bash
npm run typecheck
npm test
npm run format:check
npx playwright install chromium
npm run test:e2e
```

`test:e2e` requiere las dependencias del backend en `backend/.venv` o la ruta indicada por `KENFIT_PYTHON`; crea sus propios datos temporales.

La sesión real se guarda en SecureStore en Android/iOS. La vista web mantiene el token solo en memoria. La demostración siempre está identificada y reinicia sus datos al entrar de nuevo.

No hay secrets en `.env.example`. No añadas secretos a variables `EXPO_PUBLIC_*`.

Estado y límites: [entrega inicial](../docs/mobile/ENTREGA_FRONTEND.md).
