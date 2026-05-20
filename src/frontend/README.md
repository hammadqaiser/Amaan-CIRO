# 🇵🇰 Amaan CIRO - High-Performance Web & Mobile Client

[![Live Web Dashboard](https://img.shields.io/badge/Vercel-Web_Dashboard-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://amaan-ciro-web.vercel.app)
[![API Docs & Swagger](https://img.shields.io/badge/FastAPI-Cloud_Run_Swagger-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://amaan-ciro-485623882730.asia-south1.run.app/docs)

This directory houses the frontend application for the **Amaan (CIRO) - Crisis Intelligence & Response Orchestrator** system. It is built as a high-fidelity Single Page Application (SPA) designed to serve as both an interactive desktop command bridge for Emergency Operations Centers (EOC) and a responsive mobile dashboard for citizens and field coordinators.

### 🌐 Live Production URL
*   **Vercel Production Link:** [https://amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app)

---

## 🚀 Key Technologies

*   **Vite + React 19 + TypeScript**: Fast HMR dev server and compiled, fully typed production SPA.
*   **MapLibre GL JS**: Hardware-accelerated WebGL vector canvas that renders live crisis zones, dynamic traffic rerouting, and active emergency fleet GPS coordinates.
*   **Zustand**: High-efficiency, ultra-lightweight client state management keeping map coordinates, chat history, and news alerts synchronized.
*   **Tailwind CSS v4**: Futuristic dark-mode and neon UI design representing tactical command systems.
*   **Ionic Capacitor v8**: Native Android wrapper shell compiling the WebGL canvas into an Android Package (APK) with zero performance loss.

---

## 📂 Project Structure

```
src/frontend/
├── android/             # Android Studio native Java/Kotlin project (Ionic Capacitor)
├── public/              # Static assets, mock telemetry icons, live news banners
├── src/
│   ├── api/             # API client linking Vite client with deployed FastAPI agent orchestrator
│   ├── components/      # UI components (Satellite Broadcast, Resource Inventory, Command Bridge)
│   ├── config/          # Map styling and vector layer configs
│   ├── store/           # Zustand state variables (active crisis, selected coordinates, chats)
│   ├── utils/           # Spatial geocoding, distance matrices, and metric baselines
│   ├── App.tsx          # Main entry layout with tab toggling and MapLibre overlay bindings
│   └── main.tsx         # App bootstrapping
├── capacitor.config.ts  # Capacitor configurations (package identifier, native web root)
├── index.html           # Web template document
├── package.json         # Client build scripts and node packages
└── vite.config.ts       # Vite build configurations
```

---

## 🛠️ Development Setup

### Prerequisite Checklist
*   Node.js v20+ and npm
*   Android Studio (for compiling the APK locally)
*   Java Development Kit (JDK) 17 (required for Gradle compilation)

### 1. Installation
Restore project node modules:
```bash
npm install
```

### 2. Configure Deployed API Endpoint
Configure the deployed API backend server URL in `src/api/client.ts`. By default, the production URL routes to our live Google Cloud Run server:
```typescript
const PRODUCTION_URL = 'https://amaan-ciro-485623882730.asia-south1.run.app/api';
```
For local debugging against a local FastAPI port, you can change it to:
```typescript
const LOCAL_URL = 'http://localhost:8000/api';
```

### 3. Launch Development Server
Start the local Vite server:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📱 Compiling the Native Android APK

Amaan utilizes **Ionic Capacitor** to bridge WebGL hardware-accelerated mapping into a lightweight Android container. This allows us to reuse our highly polished interactive React UI directly on Android.

### Step 1: Compile Web Assets
Build the React production assets:
```bash
npm run build
```

### Step 2: Synchronize with Native Android Shell
Sync the compiled static folder (`dist/`) into the native Android Gradle project directory:
```bash
npx cap sync android
```

### Step 3: Compile Debug APK
Run Gradle to build the native Android executable:
```bash
cd android
./gradlew assembleDebug
```
*   **Output APK:** The final compiled APK file is saved at:
    `src/frontend/android/app/build/outputs/apk/debug/app-debug.apk` (Size: ~5.3 MB!)
*   **Android Studio Visual Guide:** If you prefer running or visual debugging on a simulator/device, run `npx cap open android` from the `src/frontend` directory to automatically open the workspace in Android Studio.
