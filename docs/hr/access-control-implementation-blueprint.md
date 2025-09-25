# 🚜 Farm Access Control – Implementation Blueprint

---

## 1. Overview

A **multi‑site, vendor‑agnostic, offline‑capable biometric access control system** for:

- Clinic
- School
- Storeroom
- Main Gate
- Office

**Core features:**

- Bias‑friendly **on‑device enrollment**
- Central logging of all granted/denied events
- Real‑time or delayed sync over PtMP/Starlink
- **Zambia Data Protection Act, 2021** compliance built in

---

## 2. Hexagonal + Multi‑Site Architecture

```mermaid
flowchart LR
    subgraph Domain[Domain Layer]
        SVC[AccessControlService]
        PORT[AccessControlPort Interface]
        DB[(Central Farm DB)]
    end

    subgraph App[Application Layer]
        UC1[Activate / Deactivate User]
        UC2[Enroll User - Local or Remote]
        UC3[Sync Enrollment from Device]
        UC4[Fetch & Store Access Events]
    end

    subgraph Infra[Infrastructure Layer - Vendor Adapters]
        ZA[ZKTeco Adapter]
        SA[Suprema Adapter]
        IA[IDEMIA Adapter]
        HA[Hikvision Adapter]
    end

    subgraph Sites[Farm Locations]
        CL[Clinic Gate]
        SC[School Gate]
        ST[Storeroom]
        GT[Main Gate]
        OF[Office Access]
    end

    CL --> ZA
    SC --> SA
    ST --> IA
    GT --> ZA
    OF --> HA

    SVC --> PORT
    PORT --> UC1 & UC2 & UC3 & UC4

    UC1 --> ZA & SA & IA & HA
    UC2 --> ZA & SA & IA & HA
    UC3 --> ZA & SA & IA & HA
    UC4 --> ZA & SA & IA & HA

    ZA --> CL & GT
    SA --> SC
    IA --> ST
    HA --> OF

    UC4 --> DB
```

---

## 3. Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE devices (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    vendor TEXT NOT NULL,
    model TEXT NOT NULL,
    ip_address INET,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE user_device_map (
    user_id UUID REFERENCES users(id),
    device_id UUID REFERENCES devices(id),
    vendor_user_id TEXT NOT NULL,
    enrolled_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY(user_id, device_id)
);

CREATE TABLE access_events (
    id BIGSERIAL PRIMARY KEY,
    device_id UUID REFERENCES devices(id),
    user_id UUID REFERENCES users(id),
    event_time TIMESTAMPTZ NOT NULL,
    result TEXT NOT NULL,
    reason TEXT,
    match_score NUMERIC(5,2),
    raw_event JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE user_photos (
    user_id UUID REFERENCES users(id) PRIMARY KEY,
    photo BYTEA NOT NULL,
    captured_at TIMESTAMPTZ DEFAULT now(),
    source_device_id UUID REFERENCES devices(id)
);

CREATE TABLE user_consent (
    user_id UUID REFERENCES users(id) PRIMARY KEY,
    consent_text TEXT NOT NULL,
    date_signed TIMESTAMPTZ NOT NULL,
    signature_hash TEXT NOT NULL,
    operator_id UUID,
    withdrawal_date TIMESTAMPTZ,
    withdrawal_reason TEXT
);
```

---

## 4. Entity–Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ USER_DEVICE_MAP : "enrolled_on"
    DEVICES ||--o{ USER_DEVICE_MAP : "has_enrollment"
    USERS ||--o{ ACCESS_EVENTS : "generates"
    DEVICES ||--o{ ACCESS_EVENTS : "records"
    USERS ||--o| USER_PHOTOS : "has_photo"
    DEVICES ||--o{ USER_PHOTOS : "captured_by"
    USERS ||--o| USER_CONSENT : "has_consent"
```

---

## 5. Full User Lifecycle (Enrollment → Event Logging → Activation/Deactivation)

```mermaid
sequenceDiagram
    autonumber
    participant Admin as Admin UI
    participant User as Person at Any Access Point
    participant Device as Biometric Device
    participant Adapter as Vendor Adapter
    participant Core as Core Domain Service
    participant DB_users as DB: users
    participant DB_map as DB: user_device_map
    participant DB_events as DB: access_events
    participant DB_photos as DB: user_photos
    participant OtherAdapters as Other Site Adapters
    participant OtherDevices as Other Site Devices

    %% ENROLLMENT
    User ->> Device: Enroll face
    Device ->> Adapter: Notify new enrollment
    Adapter ->> Device: Pull template + photo
    Adapter ->> Core: Send enrollment data
    Core ->> DB_users: INSERT user
    Core ->> DB_photos: INSERT photo
    Core ->> DB_map: INSERT mapping
    Core ->> OtherAdapters: Push enrollment
    OtherAdapters ->> OtherDevices: Enroll API

    %% ACCESS EVENT
    User ->> Device: Present face
    Device ->> Device: Local match
    alt Granted
        Device ->> Adapter: Event {granted}
    else Denied
        Device ->> Adapter: Event {denied, reason}
    end
    Adapter ->> Core: Normalise
    Core ->> DB_map: READ mapping
    Core ->> DB_users: READ status
    Core ->> DB_events: INSERT event

    %% STATE CHANGE
    Admin ->> Core: Activate/Deactivate
    Core ->> DB_users: UPDATE status
    Core ->> DB_map: READ mappings
    Core ->> Adapter: Send status change
    Adapter ->> Device: Apply status
    Device -->> Adapter: Confirm
    Adapter -->> Core: Result
```

---

## 6. Compliance & Consent – Zambia Context

- **Explicit, informed consent** captured before enrollment.
- Version consent text & store in `user_consent`.
- Withdrawal triggers full de‑provisioning:
  - Remove templates from all devices.
  - Remove `user_device_map` entries.
  - Update `users.status`.

---

## 7. Consent Form UI (Enrollment)

```mermaid
flowchart TD
    subgraph ConsentForm[Consent Form UI]
        Title[**Biometric Data Collection Consent**]
        P1[Purpose: Control access to farm facilities and maintain an audit trail]
        P2[Data Collected: Facial biometric template + photo + name + role]
        P3[Use: Authentication at registered access points only]
        P4[Retention: Until association ends or consent withdrawn]
        P5[Rights: Access, correct, delete data anytime]
        Sig[Signature / Checkbox Consent]
        SaveBtn[Submit Enrollment & Store Consent]
    end
```

**Consent Text Example:**
> I understand [Farm Name] will collect and store my facial biometric template, enrollment photo, and details for access control and audit logs. I have rights under the Zambia Data Protection Act, 2021, including access, correction, deletion, and consent withdrawal. I voluntarily consent until my association ends or I withdraw in writing.

---

## 8. Admin UI Dashboard (NEW Section)

**Key Panels:**
- **User Management** – Create/edit users, view enrollment status, activate/deactivate.
- **Device Management** – View device health, last sync, firmware, mappings.
- **Consent Tracking** – View consent status & history, trigger withdrawal workflows.
- **Event Log Viewer** – Filterable by site/device/date/result, export CSV/PDF.
- **Alerts & Sync Status** – Show offline devices, pending sync queues.

```mermaid
flowchart TD
    subgraph AdminUI[Admin Dashboard]
        UM[User Management Panel]
        DM[Device Management Panel]
        CT[Consent Tracking Panel]
        EL[Event Log Viewer]
        AS[Alerts & Sync Status]
    end

    UM --> CT
    UM --> DM
    DM --> EL
    CT --> EL
    AS --> DM
    AS --> EL
```

---

## 9. Quick Start Developer Checklist

**Phase 1:** Implement schema + domain interfaces  
**Phase 2:** Core use cases  
**Phase 3:** Event logging  
**Phase 4:** Multi‑site sync  
**Phase 5:** Consent capture + withdrawal  
**Phase 6:** Admin dashboard

---