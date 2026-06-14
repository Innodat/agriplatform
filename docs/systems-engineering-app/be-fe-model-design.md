Yes — **use Pydantic**, but don’t use it for *every* “model” in your architecture.

Given your stack:

* Python backend
* likely FastAPI-style API
* frontend uses Zod
* hexagonal / app-silo architecture
* possible DSL-driven SE app

My recommendation is:

> **Use Pydantic v2 for API contracts, validation, config, and external data boundaries. Use plain domain models or dataclasses for core domain logic where you want purity.**

Pydantic is a very natural fit with FastAPI because Pydantic models generate JSON Schema/OpenAPI metadata, and FastAPI uses request/response models for validation, serialization, docs, and response filtering. [\[pydantic.dev\]](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/), [\[fastapi.tiangolo.com\]](https://fastapi.tiangolo.com/tutorial/response-model/)

***

## Recommended model split

I would not have one `models.py` that tries to represent everything.

Instead, split your Python models by purpose:

```text
apps/system-engineering/backend/src/
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   └── events.py
│
├── application/
│   ├── commands.py
│   ├── queries.py
│   └── services.py
│
├── api/
│   └── schemas.py
│
├── infrastructure/
│   └── persistence/
│       ├── orm_models.py
│       └── repositories.py
│
└── config.py
```

Use different tools in each layer.

***

# My recommended choices

## 1. API request/response schemas: **Pydantic**

Use Pydantic for anything crossing the HTTP boundary.

Example:

```python
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID

class ComponentCreateRequest(BaseModel):
    site_id: UUID
    name: str = Field(min_length=1, max_length=200)
    component_type: str
    installed_on: date | None = None

class ComponentResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    component_type: str
    installed_on: date | None = None
```

This is the best place for Pydantic because it gives you:

* validation
* serialization
* JSON Schema
* OpenAPI generation
* good FastAPI integration
* alignment with frontend contract generation

Pydantic models can generate JSON Schema, and FastAPI can use those models in OpenAPI documentation and request/response validation. [\[github.com\]](https://github.com/pydantic/pydantic/blob/main/docs/concepts/json_schema.md), [\[fastapi.tiangolo.com\]](https://fastapi.tiangolo.com/tutorial/response-model/)

***

## 2. Config/settings: **Pydantic settings**

For app configuration, use Pydantic-based settings.

Example:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "system-engineering"
    database_url: str
    cors_origins: list[str] = []

    model_config = SettingsConfigDict(env_file=".env")
```

This fits your scaffold approach well:

```text
platform/builder-cli/templates/backend/config.py
```

Then each app gets its own generated `config.py`.

***

## 3. Domain entities: **dataclasses or plain classes**

For your core domain, I would lean toward `dataclasses` or plain Python classes, especially for the SE app.

Example:

```python
from dataclasses import dataclass
from datetime import date
from uuid import UUID

@dataclass
class Component:
    id: UUID
    site_id: UUID
    name: str
    component_type: str
    installed_on: date | None = None

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Component name cannot be empty")
        self.name = new_name
```

Why?

Because your domain should express business behaviour, not just validation shape.

For example:

```python
component.rename("Main Borehole Pump")
component.mark_decommissioned()
component.attach_requirement(requirement)
component.schedule_maintenance(task)
```

Those behaviours are domain logic.

Pydantic is excellent for data validation and serialization, but I would avoid making your whole domain depend on API/serialization concerns.

***

## 4. Persistence/database models: **SQLAlchemy or SQLModel**

For persistence, use either:

### Option A: SQLAlchemy ORM

Best when you want clean separation and mature ORM control.

```text
domain model != database model != API schema
```

This is the stronger hexagonal architecture choice.

***

### Option B: SQLModel

SQLModel combines Pydantic and SQLAlchemy, reducing duplication by letting one class act as both a Pydantic model and SQL database model. [\[sqlmodel.t...angolo.com\]](https://sqlmodel.tiangolo.com/), [\[pypi.org\]](https://pypi.org/project/sqlmodel/)

Example:

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class ComponentRecord(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    site_id: UUID
    name: str
    component_type: str
```

SQLModel can be very productive, especially for CRUD-heavy apps, because it is based on Pydantic and SQLAlchemy and is designed to reduce model duplication. [\[sqlmodel.t...angolo.com\]](https://sqlmodel.tiangolo.com/), [\[pypi.org\]](https://pypi.org/project/sqlmodel/)

But I would be cautious using SQLModel as your **domain model**.

For SE, Budgeting, Governance, and Modelling, I would prefer:

```text
SQLAlchemy/SQLModel record
        ↓ mapper
Domain entity
        ↓ mapper
Pydantic API schema
```

That is more boilerplate, but it keeps boundaries clean.

***

# How this relates to Zod on the frontend

Since your frontend uses Zod, the key question is:

> Which side is the source of truth for the contract?

You have three realistic options.

***

## Option 1: Backend Pydantic → OpenAPI → frontend types/Zod

This is what I would choose for API contracts.

Flow:

```text
Pydantic schemas
    ↓
FastAPI OpenAPI schema
    ↓
Generated TypeScript client / Zod schemas
    ↓
Frontend validation
```

This is especially good if your backend owns the data contract.

FastAPI uses Pydantic models to generate OpenAPI schemas, and those schemas can be consumed by client code generation tools. [\[fastapi.tiangolo.com\]](https://fastapi.tiangolo.com/tutorial/response-model/), [\[compilenrun.com\]](https://www.compilenrun.com/docs/framework/fastapi/fastapi-pydantic/fastapi-json-schema/)

Your frontend can still use Zod, but ideally the Zod schemas are generated or derived from the API contract instead of hand-written separately.

Good:

```text
Pydantic -> OpenAPI -> generated TS/Zod
```

Risky:

```text
Pydantic schema hand-written in backend
Zod schema hand-written separately in frontend
```

The second approach will drift.

***

## Option 2: Shared JSON Schema as source of truth

This may become attractive for your SE app and UI DSL.

Flow:

```text
JSON Schema
    ↓
Python validation model
    ↓
Zod schema
    ↓
UI form renderer
```

This can work well for dynamic forms, inspections, parameter capture, and DSL-driven UI.

For example:

```text
inspection template schema
parameter capture schema
requirement control schema
```

could be stored as JSON Schema or a domain-specific schema in the database.

Then:

* backend validates submissions
* frontend renders forms
* Zod validates client-side
* reports understand the shape

This could be powerful for SE.

But I would not start with this for all normal API models.

***

## Option 3: Frontend Zod → backend generated models

I would not make this the default.

It can work for UI-first apps, but for your architecture, the backend will likely own system records, requirements, tasks, parameters, governance, and integrations. So backend-first contracts make more sense.

***

# My recommendation for your architecture

Use this pattern:

```text
Backend API contracts:
  Pydantic

Frontend API contracts:
  Generated from OpenAPI where possible

Frontend form validation:
  Zod

Dynamic SE forms/checklists:
  DSL/JSON Schema + Zod frontend validation + Pydantic backend validation

Domain core:
  dataclasses/plain classes

Persistence:
  SQLAlchemy or SQLModel records
```

***

# Practical folder pattern

For `system-engineering`, I would do something like:

```text
apps/system-engineering/backend/src/
├── domain/
│   ├── components/
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   └── events.py
│   ├── sites/
│   ├── requirements/
│   └── tasks/
│
├── api/
│   ├── components/
│   │   ├── routes.py
│   │   └── schemas.py
│   └── sites/
│
├── infrastructure/
│   └── persistence/
│       ├── models.py
│       ├── mappers.py
│       └── repositories.py
│
└── config.py
```

Example conversion flow:

```python
# api/schemas.py
class ComponentCreateRequest(BaseModel):
    site_id: UUID
    name: str
    component_type: str
```

```python
# domain/entities.py
@dataclass
class Component:
    id: UUID
    site_id: UUID
    name: str
    component_type: str
```

```python
# infrastructure/persistence/models.py
class ComponentRecord(Base):
    __tablename__ = "components"
    ...
```

```python
# infrastructure/persistence/mappers.py
def record_to_domain(record: ComponentRecord) -> Component:
    return Component(
        id=record.id,
        site_id=record.site_id,
        name=record.name,
        component_type=record.component_type,
    )
```

This avoids leaking API or database concerns into your domain.

***

# When Pydantic everywhere is okay

For smaller/simple CRUD apps, it is acceptable to use Pydantic/SQLModel more broadly.

For example, Scribeswell may be simple enough that this is fine:

```text
Pydantic schemas
SQLModel records
thin service layer
```

But for SE, I’d expect complexity to grow. So I’d avoid over-coupling the domain too early.

***

# Alternatives to consider

## `dataclasses`

Best for:

```text
domain entities
value objects
commands/events
simple internal structures
```

Pros:

* standard library
* no dependency
* clean and explicit
* good for domain logic

Cons:

* less validation/serialization support than Pydantic

***

## `attrs`

Good alternative to dataclasses if you want more features.

Best for:

```text
rich domain objects
value objects
immutability
validators
```

I would only introduce it if dataclasses feel limiting.

***

## `msgspec`

Worth considering for very high-performance validation/serialization.

Best for:

```text
large data ingestion
high-throughput event processing
simulation data
telemetry capture
```

But for normal FastAPI-style app development, Pydantic has the better ecosystem fit.

***

## `SQLModel`

Great for:

```text
simple CRUD apps
admin panels
fast prototyping
small app backends
```

Be cautious for:

```text
complex domain logic
strict hexagonal boundaries
large governance/SE domain
```

SQLModel’s strength is reducing duplication, but that can also blur boundaries between API, persistence, and domain. SQLModel itself is designed as a thin layer over Pydantic and SQLAlchemy. [\[sqlmodel.t...angolo.com\]](https://sqlmodel.tiangolo.com/), [\[pypi.org\]](https://pypi.org/project/sqlmodel/)

***

# My final recommendation

For your model files:

```text
Use Pydantic v2 for:
- API request models
- API response models
- external integration payloads
- config/settings
- command/query DTOs if useful
- validation at boundaries

Use dataclasses/plain classes for:
- domain entities
- value objects
- domain events
- business behaviour

Use SQLAlchemy or SQLModel for:
- persistence records
- database mapping

Use Zod on the FE:
- preferably generated from OpenAPI for API contracts
- hand-written for purely local UI state/forms
- schema-driven for SE DSL forms
```

The short version:

> **Pydantic is the right default for Python boundary models. Don’t make it your whole domain model by default. Pair it with generated Zod contracts on the frontend to avoid drift.**
