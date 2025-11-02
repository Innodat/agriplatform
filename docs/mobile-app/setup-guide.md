# Mobile App Setup Guide

## Prerequisites

- Node.js 20+
- npm or yarn
- For iOS: Xcode 14+ and CocoaPods
- For Android: Android Studio and Android SDK

## Installation Steps

### 1. Install Dependencies

```bash
cd packages/mobile
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in `packages/mobile/`:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. iOS Setup (macOS only)

```bash
cd ios
pod install
cd ..
```

### 4. Run the App

#### iOS
```bash
npm run ios
```

#### Android
```bash
npm run android
```

## Project Structure

```
packages/mobile/
├── src/
│   ├── contexts/
│   │   └── AuthContext.tsx          # Authentication state management
│   ├── lib/
│   │   └── supabase.ts              # Supabase client configuration
│   ├── navigation/
│   │   └── RootNavigator.tsx        # Navigation setup
│   ├── screens/
│   │   ├── LoginScreen.tsx          # Login screen
│   │   ├── ForgotPasswordScreen.tsx # Password reset
│   │   └── ReceiptListScreen.tsx    # Receipt list (placeholder)
│   └── components/                   # Reusable components (empty)
├── App.tsx                           # Root component
├── .env                              # Environment variables (create this)
├── .env.example                      # Environment template
└── package.json                      # Dependencies
```

## Testing Authentication

### Test Users

Use the test users from `docs/auth/test-users-setup.md`:

**Admin User:**
- Email: `admin@liselifoundation.org`
- Password: `Admin@123`

**Employee User:**
- Email: `employee@liselifoundation.org`
- Password: `Employee@123`

### Test Flow

1. Launch the app
2. You should see the Login screen
3. Enter test credentials
4. Tap "Sign in"
5. You should be navigated to the Receipt List screen (placeholder)
6. Tap the profile icon to sign out

## Troubleshooting

### TypeScript Errors

TypeScript errors are expected until dependencies are installed. Run `npm install` to resolve them.

### Metro Bundler Issues

If you encounter Metro bundler issues:

```bash
# Clear Metro cache
npm start -- --reset-cache
```

### iOS Build Issues

```bash
cd ios
pod deintegrate
pod install
cd ..
```

### Android Build Issues

```bash
cd android
./gradlew clean
cd ..
```

## Next Steps

Once Phase 2 is complete and tested, proceed to Phase 3 to implement the full Receipt List screen with:
- Data fetching from Supabase
- Today's receipts highlighting
- Edit functionality
- Pull-to-refresh
- Pagination

See `docs/mobile-app/tech-spec.md` for detailed specifications.
