# Amaan CIRO — Demo Walkthrough & Voiceover Script

This document serves as a **screen recording guide, map icon catalog, and voiceover script** for the Amaan CIRO demonstration video (target: 3–5 minutes).

Use the live deployments:
- **Web Dashboard:** [amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app)
- **Backend API:** [amaan-ciro-...run.app](https://amaan-ciro-485623882730.asia-south1.run.app)

---

## Map Layer & Icon Reference

When recording, hover over and click these map elements to show their telemetry details:

| Layer | Color | Markers | Behavior |
|:------|:------|:--------|:---------|
| Crisis Zone Overlays | Red (`#EF4444`) with radial gradient | Pulsing ⚠️ warning marker | Expands to match calculated impact radius (e.g. 4.2 km in G-10) |
| Weather Radar | Red/Amber/Green concentric bands | — | 3 intensity bands: heavy (1.2 km), moderate (2.5 km), light (4.5 km) |
| Ambulance Assets | Blue (`#3B82F6`) | `AMB-01` to `AMB-12` badges | Dispatch route lines from station to crisis |
| Rescue Boats | Emerald (`#10B981`) | `BOAT-01` to `BOAT-06` badges | Route lines to flooded zones |
| Shelter Hubs | Green with capacity bar | 🏠 house icon | Shows name, capacity, occupancy on hover |
| Vulnerability Sectors | Red/Amber/Green coded | Sector name + risk % badge | Click for drainage, density, historical data |
| Field Signals | Source-specific colors | 🌧️ 🚗 📰 👥 icons | Credibility score and staleness shown on hover |

---

## Scene-by-Scene Script

### Scene 1: The Command Dashboard (0:00 – 0:40)

**On screen:** Open the web dashboard. Show the overview layout — map, fleet inventory, satellite news feeds. Zoom in/out of the map smoothly to demonstrate WebGL rendering.

**Voiceover:**
> "Welcome to Amaan CIRO — an Autonomous Multi-Agent Crisis Response Orchestrator. Deployed live, what you are seeing is not a passive dashboard but an active AI ecosystem designed to protect Pakistan's urban centers in real-time. The command bridge combines a WebGL vector map, fleet tracking, stakeholder communications, and embedded satellite news — all in one unified canvas."

---

### Scene 2: Signal Ingestion & Staleness (0:40 – 1:20)

**On screen:** Click "Run Scenario A" (G-10 Flooding). Show signals appearing on the map. Hover over the stale citizen report to show `staleness_flag: true` and the credibility penalty.

**Voiceover:**
> "Heavy monsoon rainfall hits Islamabad's G-10 sector. The SignalIngestionAgent fetches data from Open-Meteo weather grids, GDELT news, Google Traffic, and citizen reports. A citizen field report claiming a water main burst is flagged as stale — it's over two hours old. The system penalizes its credibility by 30%, filtering out noise before it reaches the classification engine."

---

### Scene 3: Classification & Self-Correction (1:20 – 2:05)

**On screen:** Show the VerificationAgent trace resolving the contradiction between the rain signal and the pipe burst report.

**Voiceover:**
> "The CrisisClassificationAgent detects a logical contradiction: how can a localized pipe leak occur alongside a massive meteorological flood? The LangGraph orchestrator routes to the VerificationAgent, which compares credibility scores, resolves the conflict, and updates the state. Flash flood confirmed in under 5 seconds — with full reasoning transparency."

---

### Scene 4: Severity & Resource Allocation (2:05 – 3:00)

**On screen:** Zoom to G-10. Show the flood radius circle and affected population overlay. Point to the resource allocation panel showing dispatch assignments and the fairness check.

**Voiceover:**
> "The SeverityPredictionAgent models a 4.2 km² impact zone affecting 35,000 citizens. The ResourceAllocationAgent computes the optimal dispatch: rescue boats and teams to G-10, while ambulances go to a simultaneous I-8 heatwave. Because I-8 is a low-income sector, a 15% impact multiplier guarantees equitable resource distribution."

---

### Scene 5: Simulation & Stakeholder Alerts (3:00 – 3:45)

**On screen:** Show simulation results (before/after comparison). Point to the stakeholder communications panel showing bilingual alerts.

**Voiceover:**
> "The SimulationAgent models our intervention. Compared to traditional manual dispatch with a 23-minute average delay, Amaan responds in under 8 minutes. Simultaneously, the StakeholderCommsAgent generates bilingual alerts — a staging order for PIMS Hospital, routing for Rescue 1122, and an Urdu/English public warning."

---

### Scene 6: Multilingual Chat (3:45 – 4:30)

**On screen:** Open the Chat panel. Type: `Kya G-10 mein flooding hai abhi?` (Roman Urdu). Show the response with shelter info and safety instructions.

**Voiceover:**
> "A citizen queries in Roman Urdu: 'Is there flooding in G-10 right now?' The ChatAgent detects the language, checks live crisis data, and responds instantly in Roman Urdu — confirming the flood, warning them to avoid Jinnah Avenue, and providing the nearest shelter location with the 1122 helpline."

**Alternative Urdu voiceover:**
> جب شہری ہمارے چیٹ ایجنٹ سے اردو میں پوچھتا ہے: 'کیا جی-ٹیں میں فلڈنگ ہے ابھی؟' — تو ہمارا ذہین چیٹ ایجنٹ فوراً لائیو صورتحال حاصل کرتا ہے اور قریبی شیلٹر کی ہدایت فراہم کرتا ہے۔

---

### Scene 7: Closing (4:30 – 5:00)

**On screen:** Zoom out to show the full Islamabad-Rawalpindi grid. Fade to the title slide.

**Voiceover:**
> "Amaan CIRO is an explainable, robust, and scalable guardian for Pakistan's citizens. By combining a stateful LangGraph agent topology, WebGL vector mapping, and native mobile delivery, Amaan bridges the gap between chaotic events and coordinated rescue. Deployed live and ready for the front lines."

---

## Recording Tips

1. **Resolution:** Record at 1080p (1920×1080) at 60fps.
2. **API:** Ensure the settings point to the live Cloud Run backend.
3. **Pacing:** Give map transitions 2–3 seconds to render. Smooth zoom-ins look excellent on video.
4. **Hover tooltips:** When a scenario runs, hover over resource units (AMB-01, BOAT-02) to show travel time tooltips.
5. **Don't cut the pipeline:** The full agent pipeline takes ~6 seconds. Show it in real-time — the speed is a key selling point.
