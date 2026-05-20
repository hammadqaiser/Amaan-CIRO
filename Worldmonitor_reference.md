# UI/UX Reference: CIRO Command Center (Inspired by WorldMonitor)

## Visual Design Vibe
- **Theme:** Ultra-dark mode, high-information density, "cyber-war room" aesthetic. Cyberpunk, Neon-punk. Also give option for light theme on top right corner toggle button.
- **Font:** Monospace and highly legible sans-serif (e.g., Inter, JetBrains Mono).
- **Colors:** Deep blacks/grays for background, vibrant neon accents for alerts (Red for critical, Orange for elevated, Blue/Green for stable).

## Core Tech Stack
- **Framework:** React + Vite + TypeScript.
- **Styling:** Tailwind CSS.
- **Map Engine:** `deck.gl` (via `@deck.gl/react`) + `react-map-gl` (MapLibre basemap)
- **AI/ML:** Ollama / Groq / OpenRouter, Transformers.js (browser-side)
- **State Management:** Zustand (for handling the massive JSON payloads from the CIRO backend).

## Layout Structure
1. **Top Nav Bar:** Global metrics, active crisis count, system status (DEFCON style), and a live clock.
2. **Center Canvas (The Map):** - A `deck.gl` map restricted to Pakistan's bounds (focused on Islamabad, Lahore, Karachi).
   - Layers: ScatterplotLayer for active crises, PathLayer for emergency vehicle routing, HeatmapLayer for severity clusters.
3. **Left Sidebar (Layers & Filters):** Checkboxes to toggle map layers (e.g., Weather anomalies, Infrastructure, Deployed Resources).
4. **Bottom Panel (Live Feeds):** A scrolling ticker or grid showing live GDELT news feeds and citizen reports (from CIRO's `SignalIngestionAgent`).
5. **Right Sidebar (AI Insights):** - A dedicated panel displaying the output from the CIRO `SimulationAgent` and `CrisisClassificationAgent`.
   - Sections for "Strategic Posture", "Cascading Risks", and "Recommended Allocations".

## Backend Connection
- The frontend must connect to the local FastAPI backend running at `http://localhost:8080`.


### Data Sources
- WorldMonitor aggregates 65+ external data sources across geopolitics, finance, energy, climate, aviation, cyber, military, infrastructure, and news intelligence. See the full data sources catalog for providers, feed tiers, and collection methods.
- link: https://www.worldmonitor.app/docs/data-sources