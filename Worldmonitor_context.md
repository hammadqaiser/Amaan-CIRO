# WorldMonitor — Architectural Reference

Source: https://github.com/koala73/worldmonitor
Purpose: Reference architecture for signal fusion, dashboard panels, live newsfeeds, and crisis visualization

---

## WHAT WE BORROW (architecture patterns only, not code)

### 1. Cross-Stream Correlation Pattern
WorldMonitor correlates military, economic, disaster, and escalation signals.
For CIRO, adapt this pattern:
- Instead of global signals: Islamabad/Pakistan crisis signals
- Instead of geopolitical correlation: crisis-type correlation
- Keep: credibility scoring, temporal weighting, contradiction detection

### 2. 45-Layer Data Visualization Approach
WorldMonitor uses deck.gl + globe.gl for 45 simultaneous data layers.
For CIRO mobile app, adapt:
- Google Maps with custom overlay layers
- Layer 1: Flood risk zones (NDMA data, GeoJSON)
- Layer 2: Active incidents (real-time markers)
- Layer 3: Resource positions (ambulances, rescue teams)
- Layer 4: Road status (open/blocked/rerouted)
- Layer 5: Population density (census data)
These 5 layers are our equivalent, mobile-optimized.

### 3. Country Intelligence Index → Pakistan District Risk Index
WorldMonitor scores countries across 12 signal categories.
For CIRO, adapt to Pakistan districts/sectors:
- ICT sectors (G-10, I-8, etc.) each get a risk score
- Score = flood_vulnerability × rainfall_intensity × population_density
- Updated every 30 minutes from PMD data
- Displayed as heatmap overlay on mobile map

### 4. Multi-Source AI Synthesis Pattern
WorldMonitor synthesizes 500+ feeds into AI briefs.
For CIRO, adapt:
- 5 signal sources synthesized into single CrisisObject
- Gemini generates the synthesis reasoning
- Output is structured (CrisisObject) not narrative text

### 5. Degraded Mode / Fallback Architecture
WorldMonitor uses 3-tier caching (Redis + CDN + service worker).
For CIRO, adapt:
- Tier 1: Live APIs (PMD, Google Maps, Twitter)
- Tier 2: Firestore cached data (15-minute freshness)
- Tier 3: Static mock data (pre-loaded for demo reliability)
Always fall through gracefully: live → cached → mock

---

## WHAT WE DO NOT USE FROM WORLDMONITOR
- Protocol Buffers (overkill for hackathon)
- Tauri desktop app (not needed)
- Finance/commodity features (not relevant)
- 65+ data sources (we use 5 focused sources)
