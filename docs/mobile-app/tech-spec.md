# Mobile App Technical Specification — AgriPlatform

**Version:** 1.0  
**Last Updated:** 2025-11-02  
**Platform:** React Native  
**Status:** In Development

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Shared Code Strategy](#4-shared-code-strategy)
5. [Screen Specifications](#5-screen-specifications)
6. [Navigation Structure](#6-navigation-structure)
7. [Data Management](#7-data-management)
8. [Camera & Document Scanning](#8-camera--document-scanning)
9. [Offline Support](#9-offline-support)
10. [Platform-Specific Considerations](#10-platform-specific-considerations)

---

## 1. Overview

### 1.1 Purpose

The AgriPlatform Mobile App is a React Native application designed for receipt capture and expense management on iOS and Android devices. It enables employees to capture receipts using their device camera, categorize expenses, and submit them for approval.

### 1.2 Key Features

- **Receipt Capture**: Camera scanning and gallery selection
- **Multi-Item Receipts**: Support for multiple purchase items per receipt
- **Supplier Tracking**: Required supplier field for all receipts
- **Today's Receipts**: Highlighted and editable only on capture day
- **Offline Support**: Queue operations when offline, sync when online
- **Supabase Integration**: Direct backend access with RLS security

### 1.3 Target Platforms

- **iOS**: 13.0+
- **Android**: 8.0+ (API Level 26+)

---

## 2. Architecture

### 2.1 Monorepo Structure

```
agriplatform/
├── packages/
│   ├── web/                    # React + Vite web app
│   ├── mobile/                 # React Native mobile app
│   │   ├── src/
│   │   │   ├── screens/       # Screen components
│   │   │   ├── components/    # Reusable components
│   │   │   ├── navigation/    # Navigation configuration
│   │   │   ├── lib/           # Utilities
│   │   │   └── App.tsx        # Root component
│   │   ├── android/           # Android native code
│   │   ├── ios/               # iOS native code
│   │   └── package.json
│   └── shared/                # Shared code
│       ├── schemas/           # Zod schemas
│       ├── services/          # Supabase services
│       ├── lib/               # Utilities
│       └── index.ts
```

### 2.2 Component Architecture

```
Mobile App Architecture:
┌─────────────────────────────────────────────────────────┐
│ App.tsx (Root)                                          │
│  ├─ NavigationContainer                                │
│  │   └─ Stack Navigator                                │
│  │       ├─ Auth Stack (if not authenticated)          │
│  │       │   ├─ LoginScreen                            │
│  │       │   ├─ ForgotPasswordScreen                   │
│  │       │   └─ ResetPasswordScreen                    │
│  │       └─ Main Stack (if authenticated)              │
│  │           ├─ ReceiptListScreen                      │
│  │           ├─ AddReceiptScreen                       │
│  │           └─ EditReceiptScreen                      │
│  └─ Providers (Supabase, Theme, etc.)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | 19.1.1 | UI framework |
| `react-native` | 0.82.1 | Mobile platform |
| `@react-navigation/native` | ^6.1.0 | Navigation |
| `@react-navigation/native-stack` | ^6.9.0 | Stack navigation |
| `react-native-screens` | ^4.4.0 | Native screen optimization |

### 3.2 Camera & Media

| Package | Version | Purpose |
|---------|---------|---------|
| `react-native-vision-camera` | ^3.9.0 | Camera access |
| `react-native-document-scanner-plugin` | ^1.0.0 | Document scanning |
| `react-native-image-picker` | ^7.1.0 | Gallery selection |

### 3.3 Forms & Validation

| Package | Version | Purpose |
|---------|---------|---------|
| `react-hook-form` | ^7.62.0 | Form management |
| `zod` | ^3.24.1 | Schema validation |
| `@hookform/resolvers` | ^3.9.1 | Zod integration |

### 3.4 Backend & Storage

| Package | Version | Purpose |
|---------|---------|---------|
| `@supabase/supabase-js` | ^2.55.0 | Backend client |
| `react-native-url-polyfill` | ^2.0.0 | URL polyfill for Supabase |
| `@react-native-async-storage/async-storage` | ^1.21.0 | Local storage |

### 3.5 UI Components

| Package | Version | Purpose |
|---------|---------|---------|
| `react-native-paper` | ^5.12.0 | Material Design components |
| `date-fns` | ^4.1.0 | Date utilities |

### 3.6 Shared Code

| Package | Version | Purpose |
|---------|---------|---------|
| `@agriplatform/shared` | workspace:* | Shared schemas, services, types |

---

## 4. Shared Code Strategy

### 4.1 What is Shared

✅ **Schemas** (`packages/shared/schemas/zod/`)
- Receipt, Purchase, ExpenseType, Currency schemas
- Type inference from Zod
- Validation logic

✅ **Services** (`packages/shared/services/`)
- Supabase query functions
- Accept `SupabaseClient` as parameter
- Platform-independent

✅ **Utilities** (`packages/shared/lib/`)
- Supabase client factory
- Date formatting helpers
- Common utilities

### 4.2 What is NOT Shared

❌ **UI Components**
- Web uses React DOM components
- Mobile uses React Native components
- Different styling approaches (Tailwind vs StyleSheet)

❌ **Navigation**
- Web uses React Router
- Mobile uses React Navigation

❌ **Platform-Specific Code**
- Camera access
- File system
- Native modules

### 4.3 Import Pattern

```typescript
// Mobile app imports from shared
import {
  receiptInsertSchema,
  type ReceiptInsert,
  getReceipts,
  createReceipt,
} from '@agriplatform/shared';

// Use with mobile's Supabase client
const { data, error } = await getReceipts(supabase, filters);
```

---

## 5. Screen Specifications

### 5.1 Login Screen

**Purpose**: Authenticate users via Supabase Auth

**Features**:
- Email/password input
- "Continue with Microsoft" button (SSO)
- "Forgot Password" link
- Liseli Foundation branding

**Navigation**:
- Success → ReceiptListScreen
- Forgot Password → ForgotPasswordScreen

### 5.2 Receipt List Screen

**Purpose**: Display all receipts with filtering and pagination

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "Receipts" + User Profile Icon                  │
├─────────────────────────────────────────────────────────┤
│ [ADD] Button (full width, teal)                         │
├─────────────────────────────────────────────────────────┤
│ Receipt List (FlatList)                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Supplier | Amount | Date | Edit (if today)        │  │
│  │ [Today's receipts highlighted in green]           │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Pagination: < Previous | 1 | Next >                     │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Display: Supplier | Amount | Date
- Today's receipts: Green background
- Edit button: Enabled only for today's receipts
- Pull-to-refresh
- Pagination controls

**Data Source**:
```typescript
const { data: receipts } = await getReceipts(supabase, {
  isActive: true,
});
```

### 5.3 Add/Edit Receipt Screen

**Purpose**: Capture new receipt or edit today's receipt

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "← Add Receipt" or "← Edit Receipt"             │
├─────────────────────────────────────────────────────────┤
│ Receipt Image Section                                   │
│  [Scan with Camera] [Choose from Photos]                │
│  (or show captured image with re-scan option)           │
├─────────────────────────────────────────────────────────┤
│ Date: [Date Picker]  Currency: [Dropdown]               │
├─────────────────────────────────────────────────────────┤
│ Supplier: [Text Input] ← REQUIRED                       │
├─────────────────────────────────────────────────────────┤
│ ☑ Own money (reimbursable)                              │
├─────────────────────────────────────────────────────────┤
│ Purchase Items                    [+ Add Item]          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Item 1                          [Delete]          │  │
│  │ Spending Type: [Dropdown]                         │  │
│  │ Amount: [Number Input]                            │  │
│  │ Description: [Text] (if "Other" selected)         │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Total Amount: ₹0.00                                     │
├─────────────────────────────────────────────────────────┤
│ [Save Receipt] Button                                   │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- **Camera Scanning**: `react-native-vision-camera`
- **Document Scanning**: `react-native-document-scanner-plugin`
- **Gallery Selection**: `react-native-image-picker` ("Choose from Photos")
- **Supplier Field**: Required text input
- **Date Picker**: Native date picker
- **Currency Dropdown**: Symbol display only (₹/$€/£)
- **Own Money Checkbox**: Applies to all items
- **Dynamic Items**: Add/remove purchase items
- **Expense Type Dropdown**: Grouped by category
- **Description Field**: Shown when "Other" selected
- **Total Calculation**: Sum of all item amounts

**Validation**:
```typescript
const receiptSchema = z.object({
  supplier: z.string().min(1, 'Supplier is required'),
  captured_date: z.string(),
  currency_id: z.number(),
  purchase_items: z.array(z.object({
    expense_type_id: z.number(),
    amount: z.number().positive(),
    other_category: z.string().optional(),
    reimbursable: z.boolean(),
  })).min(1, 'At least one item required'),
});
```

---

## 6. Navigation Structure

### 6.1 Navigation Stack

```typescript
// src/navigation/RootNavigator.tsx
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  // Auth Stack
  Login: undefined;
  ForgotPassword: undefined;
  ResetPassword: { token: string };
  
  // Main Stack
  ReceiptList: undefined;
  AddReceipt: undefined;
  EditReceipt: { receiptId: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  const { user } = useAuth();
  
  return (
    <Stack.Navigator>
      {!user ? (
        // Auth Stack
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          <Stack.Screen name="ResetPassword" component={ResetPasswordScreen} />
        </>
      ) : (
        // Main Stack
        <>
          <Stack.Screen name="ReceiptList" component={ReceiptListScreen} />
          <Stack.Screen name="AddReceipt" component={AddReceiptScreen} />
          <Stack.Screen name="EditReceipt" component={EditReceiptScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}
```

### 6.2 Navigation Flow

```
Login → ReceiptList → AddReceipt → ReceiptList
                   → EditReceipt → ReceiptList
```

---

## 7. Data Management

### 7.1 Supabase Client Setup

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import 'react-native-url-polyfill/auto';

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey,
