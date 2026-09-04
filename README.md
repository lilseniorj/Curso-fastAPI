# API de Clientes, Planes y Transacciones

API REST construida con **FastAPI** y **SQLModel** durante el curso de Backend con FastAPI de Platzi.

Gestiona clientes, planes de suscripción y transacciones, con relaciones uno-a-muchos y muchos-a-muchos, validaciones personalizadas, filtros, paginación, autenticación básica y una suite de pruebas con pytest.

## Stack

| Herramienta | Versión | Para qué |
|---|---|---|
| Python | 3.14 | |
| FastAPI | 0.141 | Framework web |
| SQLModel | 0.0.39 | ORM (SQLAlchemy + Pydantic) |
| Pydantic | 2.13 | Validación de datos |
| SQLite | — | Base de datos |
| pytest | 9.1 | Pruebas |

## Qué incluye

- **CRUD completo de clientes** — crear, listar, consultar, actualizar (PATCH parcial) y eliminar
- **Relación uno-a-muchos** — un cliente tiene muchas transacciones
- **Relación muchos-a-muchos** — clientes y planes, con tabla intermedia que guarda el estado de la suscripción
- **Validaciones personalizadas** con `field_validator`: formato de email, unicidad, normalización de teléfono y documento
- **Filtros con Enum** — listar planes por uno o varios estados (`?plan_status=active&plan_status=inactive`)
- **Paginación** con `skip` y `limit`
- **Middlewares** para medir tiempo de respuesta y registrar cabeceras
- **Autenticación HTTP Basic** con credenciales en variables de entorno
- **16 pruebas** con pytest, base en memoria y fixtures

## Estructura

```
.
├── app/
│   ├── main.py              # App, middlewares, endpoints raíz y /time
│   ├── routers/
│   │   ├── customers.py     # CRUD de clientes y suscripción a planes
│   │   ├── plans.py         # Planes
│   │   └── transactions.py  # Transacciones (con paginación)
│   └── test/
│       ├── test_customers.py
│       └── test_main.py
├── models.py                # Modelos SQLModel y validadores
├── db.py                    # Engine, sesión y creación de tablas
├── conftest.py              # Fixtures de pytest (session, client, customer)
└── create_multiple_transactions.py   # Genera datos de prueba
```

## Instalación

```bash
git clone git@github.com:lilseniorj/Curso-fastAPI.git
cd Curso-fastAPI

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install fastapi[standard] sqlmodel python-dotenv email-validator pytest
```

Copia el archivo de ejemplo y define tus credenciales:

```bash
cp .env.example .env
```

```env
API_USERNAME=tu_usuario
API_PASSWORD=tu_contraseña
```

> El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

## Uso

```bash
fastapi dev app/main.py
```

Los comandos se ejecutan **desde la raíz del proyecto**. La base de datos SQLite se crea automáticamente al arrancar.

- API: http://127.0.0.1:8000
- Documentación interactiva: http://127.0.0.1:8000/docs

Para generar 100 transacciones de prueba y probar la paginación:

```bash
python create_multiple_transactions.py
```

## Endpoints

### Clientes

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/customers` | Crear un cliente |
| `GET` | `/customers` | Listar todos |
| `GET` | `/customers/{customer_id}` | Consultar uno |
| `PATCH` | `/customers/{customer_id}` | Actualizar campos parciales |
| `DELETE` | `/customers/{customer_id}` | Eliminar |

### Planes y suscripciones

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/plans` | Crear un plan |
| `GET` | `/plans` | Listar planes |
| `POST` | `/customers/{customer_id}/plans/{plan_id}` | Suscribir un cliente a un plan |
| `GET` | `/customers/{customer_id}/plans` | Planes del cliente, filtrados por estado |

La suscripción acepta `?plan_status=active|inactive` (por defecto `active`). El listado acepta varios estados a la vez:

```
GET /customers/1/plans?plan_status=active&plan_status=inactive
```

### Transacciones

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/transactions` | Crear una transacción |
| `GET` | `/transactions` | Listar con paginación |

```
GET /transactions?skip=10&limit=5
```

### Otros

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Saludo — **requiere autenticación** |
| `GET` | `/time/{iso_code}` | Hora del país (`CO`, `US`, `MX`, `BR`, `PE`) |

`/time` acepta `?format_24=false` para formato de 12 horas con AM/PM. Un país no registrado devuelve la hora UTC.

## Modelo de datos

```
Customer ──< Transaction              uno a muchos
Customer >──< Plan  (CustomerPlan)    muchos a muchos
```

`CustomerPlan` no es solo una tabla de enlace: guarda el `status` de cada suscripción (`active` / `inactive`), porque el estado describe la relación y no a ninguna de las dos entidades por separado.

### Validaciones

| Campo | Reglas |
|---|---|
| `email` | Formato válido (`EmailStr`), único, normalizado a minúsculas |
| `phone` | Solo dígitos, 10 caracteres; se limpian espacios y guiones |
| `document_id` | Solo dígitos, único |

## Pruebas

```bash
pytest app/test -v
```

Las pruebas usan una base de datos **SQLite en memoria**, independiente de la de desarrollo. Cada ejecución empieza limpia.

Fixtures disponibles en `conftest.py`:

- `session` — sesión contra la base en memoria
- `client` — `TestClient` con la dependencia de sesión sustituida
- `customer` — un cliente ya creado, listo para usar

## Limitaciones conocidas

Este es un proyecto de aprendizaje. Cosas identificadas pero no resueltas:

- **Sin migraciones.** Cambiar un modelo obliga a borrar `db.sqlite3` y recrear las tablas. En un proyecto real se usaría Alembic.
- **Los validadores consultan la base directamente.** `models.py` importa el engine, así que las validaciones de unicidad no usan la sesión inyectada. Esto acopla los modelos a la base de datos y hace que las pruebas dependan del archivo `db.sqlite3`.
- **PATCH con el mismo email falla.** Como `CustomerUpdate` hereda el validador de unicidad, actualizar un cliente enviando su propio email lo detecta como duplicado.
- **Autenticación solo en `/`.** El resto de endpoints están sin proteger.
- **Basic Auth** envía credenciales en cada petición. Para producción correspondería OAuth2 con JWT y contraseñas hasheadas.

## Licencia

Proyecto educativo, de uso libre.
