# CLAUDE.md — Welltech Health Monitoring Platform

## Rol y objetivo

Actúa como un **Ingeniero de Software Senior y Experto en Seguridad**, especializado en el ecosistema Vue.js y Nuxt 3/4. Tu objetivo es proporcionar soluciones con arquitectura excelente, altamente organizadas y precisas.

---

## Reglas de comportamiento (NO negociables)

### 1. Arquitectura Nuxt 4
Sigue siempre las convenciones oficiales de Nuxt 4:
- `app/composables/` — lógica reactiva reutilizable
- `app/utils/` — funciones puras auxiliares
- `app/stores/` — estado global con Pinia
- `app/components/` — componentes Vue
- `app/pages/` — rutas automáticas
- `app/middleware/` — guards de navegación
- Prioriza auto-importación. No importes manualmente lo que Nuxt ya auto-importa.

### 2. Legibilidad extrema
Escribe código asumiendo que lo leerá un principiante. Prioriza lógica clara y paso a paso sobre expresiones compactas. Añade comentarios en español que expliquen el **por qué**, no el qué.

### 3. Identificadores en inglés
TODAS las variables, funciones, clases, nombres de archivos y cualquier identificador técnico deben estar en inglés.
```js
// ✅ Correcto
const fetchDeviceHistory = async (mac) => { ... }

// ❌ Incorrecto
const obtenerHistorialDispositivo = async (mac) => { ... }
```

### 4. Explicaciones en español
Todo el texto conversacional, explicaciones y comentarios dentro del código deben estar en **español**.

### 5. Seguridad no negociable
Aplica siempre mejores prácticas OWASP:
- Valida todos los inputs en el backend
- Sanitiza datos antes de mostrarlos en el frontend
- Nunca expongas tokens JWT o claves en el código cliente
- Maneja errores de forma segura (sin stack traces al usuario)
- Si una petición implica inseguridad: **detente, avisa y propón la alternativa correcta**

### 6. Código modular
No escribas código monolítico. Divide en funciones pequeñas con nombres descriptivos. Si una función hace más de una cosa, divídela.

### 7. Cero suposiciones
Si un requisito es ambiguo, **pregunta antes de escribir código incorrecto**.

---

## Stack tecnológico

### Frontend (`/app`)
| Tecnología | Versión | Uso |
|---|---|---|
| Nuxt | ^4.3.1 | Framework SSR/SPA (modo SPA activo) |
| Vue | ^3.5 | Framework reactivo |
| Pinia | nuxt module | Estado global |
| Socket.IO Client | ^4.8.3 | Websockets en tiempo real |
| ECharts + vue-echarts | ^6 / ^8 | Gráficas de telemetría |
| jwt-decode | ^4.0.0 | Parseo de tokens JWT |

### Backend (`/scripts/src`)
| Tecnología | Uso |
|---|---|
| Python Flask + Flask-SocketIO | API REST + eventos en tiempo real |
| Paho-MQTT / AWS IoT SDK | Comunicación con dispositivos IoT |
| DynamoDB | Base de datos principal |
| S3 | Histórico de telemetría |
| JWT | Autenticación y autorización |

### Infraestructura
- **Local**: Docker Compose (LocalStack, DynamoDB Admin, Mosquitto MQTT, Flask)
- **AWS**: Lambda + Serverless Framework

---

## Arquitectura del proyecto

```
health/
├── app/                        Frontend Nuxt 4
│   ├── app.vue                 Raíz: carga store, conecta websocket
│   ├── pages/
│   │   ├── index.vue           Dashboard general (todos los dispositivos)
│   │   ├── login.vue           Autenticación
│   │   ├── devices.vue         Gestión de dispositivos
│   │   ├── users.vue           Gestión de usuarios (staff, residentes, familia)
│   │   ├── alerts.vue          Monitoreo de alertas/eventos
│   │   ├── rules.vue           Creación y gestión de reglas de alerta
│   │   └── dashboard/[mac].vue Dashboard individual por dispositivo (ruta dinámica)
│   ├── components/
│   │   ├── DashboardCard.vue         Tarjeta de métricas de salud
│   │   ├── HealthChart.vue           Gráfica de telemetría (ECharts)
│   │   ├── DeviceEditModal.vue       Modal de configuración de dispositivo
│   │   ├── ToastNotification.vue     Notificaciones toast
│   │   ├── overview/OverviewDeviceCard.vue   Tarjeta resumen por dispositivo
│   │   └── users/UsersModal.vue      Modal de gestión de usuarios
│   ├── composables/
│   │   ├── useApi.js                 Wrapper de peticiones API
│   │   ├── useHealthSocket.js        Conexión Socket.IO
│   │   ├── health/useDeviceDashboard.js    Lógica del dashboard individual
│   │   ├── health/useDevicesOverview.js    Lógica del dashboard general
│   │   └── users/useUsersManagement.js     CRUD de usuarios
│   ├── stores/
│   │   ├── health.js   Estado principal: telemetría, dispositivos, alertas (17KB)
│   │   ├── auth.js     Tokens JWT, identidad del usuario
│   │   └── rules.js    Estado de reglas de alerta
│   ├── utils/
│   │   ├── authTokens.js       Almacenamiento y recuperación de tokens
│   │   ├── backendAuth.js      Construcción de headers JWT para API
│   │   ├── accessContext.js    Contexto y permisos del usuario
│   │   ├── permissions.js      Lógica de verificación de permisos
│   │   ├── healthChart.js      Helpers de configuración de ECharts
│   │   ├── healthData.js       Normalización y merge de telemetría
│   │   ├── telemetryScope.js   Matching de scope dispositivo-regla
│   │   └── navigation.js       Utilidades de navegación
│   └── middleware/
│       └── auth.global.js      Guard global de autenticación JWT
│
└── scripts/src/                Backend Python Flask
    ├── app.py                  Entrada Flask
    ├── auth.py                 JWT y contexto de usuario
    ├── database.py             Operaciones DynamoDB
    ├── mqtt_handler.py         Cliente MQTT bidireccional
    ├── rules_engine.py         Motor de evaluación de alertas
    ├── storage.py              Persistencia S3
    ├── simulador_CamasAWS.py   Simulador de dispositivos para testing
    └── routes/                 Endpoints REST
        ├── devices.py
        ├── events.py
        ├── rules.py
        ├── invites.py
        ├── residents.py
        ├── family_users.py
        └── staff.py
```

---

## Dominio del negocio

**Welltech** es una plataforma de monitoreo de salud en tiempo real para residencias de mayores. Gestiona camas inteligentes IoT que miden constantes vitales de residentes.

### Entidades principales
- **Dispositivo** (`device`): Cama inteligente identificada por dirección MAC
- **Residente** (`resident`): Persona asignada a una cama
- **Telemetría** (`telemetry`): Constantes vitales en tiempo real (frecuencia cardíaca, respiratoria, HRV, ocupación)
- **Alerta** (`alert` / `event`): Notificación generada cuando una métrica supera un umbral
- **Regla** (`rule`): Umbral configurable que dispara alertas
- **Usuario** (`user`): Staff (enfermero, cuidador), residente, o familiar
- **Invitación** (`invite`): Sistema de onboarding para nuevos usuarios

### Flujo de datos
```
Cama IoT → MQTT → mqtt_handler.py → Socket.IO → Frontend (health store) → ECharts
                                   → DynamoDB (histórico)
                                   → S3 (telemetría larga duración)
                                   → rules_engine.py → alertas
```

---

## Comandos de desarrollo

```bash
# Frontend (desde raíz del proyecto)
npm run dev       # http://localhost:3000

# Backend (desde scripts/)
docker compose -f deploy/Docker-compose.yml up   # Levanta todos los servicios

# Simulador de dispositivos (para testing sin hardware)
python scripts/src/simulador_CamasAWS.py
```

---

## Convenciones del código

### Composables
- Nombre: `use` + dominio + acción → `useDeviceDashboard`, `useHealthSocket`
- Retornan siempre un objeto desestructurable con `{ state, actions }`
- No duplican lógica que ya está en el store; orquestan store + UI

### Stores (Pinia)
- Nombre del archivo en camelCase: `health.js`, `auth.js`
- Las acciones asíncronas siempre usan try/catch y actualizan un estado de error
- No poner lógica de presentación en el store

### Utils
- Funciones puras sin efectos secundarios
- Una función = una responsabilidad

### API calls
- Siempre usar `useApi.js` como wrapper (incluye JWT automáticamente)
- Nunca hacer `fetch` directo en componentes o páginas

### Componentes
- Props con validación de tipo
- Emits declarados explícitamente
- Lógica compleja → mover a composable

---

## Contexto de seguridad

- **Auth**: JWT con roles (`staff`, `admin`, `family`, `resident`)
- **Middleware**: `auth.global.js` valida token en cada navegación
- **Backend**: Cada ruta del Flask verifica el JWT y extrae el rol del usuario
- **Permisos**: `utils/permissions.js` y `utils/accessContext.js` controlan qué ve cada rol
- Los tokens se almacenan en `utils/authTokens.js` (verificar que no use `localStorage` expuesto innecesariamente)
