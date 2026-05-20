# 🎬 Amaan CIRO — Cinematic Demo Video Blueprint & Voiceover Script
### *The Autonomous Guardian of Pakistan's Urban Frontiers*

This document serves as your **Cinematic Storyboard, Browser Interaction Guide, Map Icon Catalog, and Word-for-Word Voiceover Script** for the Amaan (CIRO) demonstration video (Target: 2 to 5 minutes). 

You can use the live Vercel Web Dashboard at **[https://amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app)** to record your screen capture. The backend is running live on Google Cloud Run at **[https://amaan-ciro-485623882730.asia-south1.run.app](https://amaan-ciro-485623882730.asia-south1.run.app)**.

---

## 🗺️ Key Map UI Layers & Icon Blueprint

When recording your browser screen capture of the Map view, highlight these specific **WebGL-accelerated vector layers** and hover/click on the icons to show their live telemetry details to the judges:

| Map Layer | Visual Style & Color Profile | Map Icon & Marker | Interaction & Dynamic Behavior |
|:---|:---|:---|:---|
| **Crisis Zone Overlays** | `#EF4444` (Neon Red/Crimson) with dynamic radial gradient fill | Pulse marker with warning tag | Expands outwards to match the calculated impact radius (e.g. 4.2 km in G-10, 3.8 km in I-8). |
| **Traffic Congestion Line** | `#F59E0B` (Neon Amber / Yellow) styled line weights | Gridlock hazard sign | Highlights blocked arterial routes (e.g., Jinnah Avenue and G-10 Markaz loop). |
| **Ambulance Assets** | `#3B82F6` (Electric Blue) vector dots | `AMB-01` to `AMB-12` badges | Smooth vector tracking representing vehicle routes to staging points. |
| **Rescue Boat Assets** | `#10B981` (Emerald Green) vector circles | `BOAT-01` to `BOAT-06` badges | Located near local response centers, routing dynamically to flooded lanes. |
| **Shelter Staging Hubs** | `#8B5CF6` (Neon Indigo) house glyph | Staging Center tag | Highlights locations like the G-10 Markaz Community Center, pulsing when capacity increases. |
| **Core Heartbeat Wave** | `#10B981` (Emerald / Pulse Green) | Heartbeat ECG wave indicator | Animates in real-time next to the operational status badge in the sticky header: `STATUS: ONLINE • COMMAND BRIDGE`. |

---

## 📽️ Scene-by-Scene Script & Storyboard (3-5 Minute Video)

---

### ⏳ Scene 1: The Tactical Cockpit (0:00 – 0:40)
**Visual Actions on Screen:**
1. Open the browser to **[https://amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app)**.
2. Ensure you are on the **Overview** dashboard (which shows the system layout in a sleek, glassmorphic layout: Regional Operational Map, Tactical Fleet Inventory, Live Broadcast Feeds).
3. Hover your cursor over the pulsing green **Amaan logo / motto banner** and the live-streaming satellite feeds of **Geo News** and **ARY News** playing on the screen.
4. Zoom in and out of the **Regional Operational Map** smoothly to show the hardware-accelerated MapLibre GL rendering at a fluid 60 frames per second.

**🎤 Narration / Voiceover:**
> *"Welcome to the EOC Command Bridge of Amaan CIRO—Autonomous Multi-Agent Crisis Response Orchestrator. Deployed live on Vercel and Google Cloud Run, what you are seeing is not a passive statistical chart, but an active, stateful AI ecosystem designed to protect Pakistan’s urban centers in real-time. Rendered using a high-fidelity WebGL vector map, Amaan operates at a fluid 60 frames per second. The command bridge combines regional operational telemetry, fleet inventory tracking, and a live broadcast satellite news system directly inside one unified canvas. Let's trigger a crisis event."*

---

### ⏳ Scene 2: The Ingestion Spark & Staleness Check (0:40 – 1:20)
**Visual Actions on Screen:**
1. Locate the **Run System Scenarios** panel on your left side.
2. Click on the button labeled **"Run Scenario A (Monsoon Flash Flood in G-10)"**.
3. Immediately point the cursor to the scrolling **Telemetry Logs** panel as raw signal nodes animate onto the map.
4. Hover over the newly rendered signal markers in the G-10 sector:
   * **Open-Meteo Weather Signal (Emerald):** 82mm rainfall in 3 hours.
   * **GDELT Social Signal (Orange):** Flooding reported on Jinnah Avenue.
   * **Citizen Field Report (Faded Gray):** Stale, 4-hour-old report claiming a minor pipe burst. Point to the log showing `staleness_flag: true` and the credibility penalty!

**🎤 Narration / Voiceover:**
> *"At 20:40 Local Time, heavy monsoon rainfall hits Islamabad's G-10 sector. Instantly, Amaan’s SignalIngestionAgent fetches and normalizes data from four sources: Open-Meteo weather grids, GDELT global news, Google Maps traffic grids, and citizen field reports. The Ingestion Agent applies strict temporal filtering. Watch as a citizen report of a simple water main burst is flagged as 'stale'—it's over two hours old. The system automatically penalizes its credibility by 30%, filtering out noise before it reaches our decision engine. Our inputs are clean. The data flows."*

---

### ⏳ Scene 3: The LangGraph Collision & Self-Correction (1:20 – 2:05)
**Visual Actions on Screen:**
1. Scroll down slightly to show the **System Core Architecture Blueprint** panel.
2. Point your cursor to the **VerificationAgent** trace log.
3. Highlight the contradiction text on screen showing how the system detected a logical conflict: meteorological rain surge vs. localized pipe leak.
4. Click on the **Agent Traces** tab in your settings or sidebar to show the JSON trace payload indicating that the Verification Agent resolved the conflict in favor of the rain surge.

**🎤 Narration / Voiceover:**
> *"As these signals collide, the orchestrator triggers our stateful LangGraph workflow. The CrisisClassificationAgent flags a logical contradiction: how can a localized pipe leak occur simultaneously with a massive meteorological flood alert? Instead of passing conflicting data to rescue teams, the orchestrator routes the state directly to the VerificationAgent. Utilizing a self-correcting reflection loop, the VerificationAgent compares source credibility, resolves the conflict, and updates the state payload. Flash Flood confirmed in under 5 seconds with absolute mathematical transparency."*

---

### ⏳ Scene 4: Severity Prediction & Fair Resource Dispatch (2:05 – 3:00)
**Visual Actions on Screen:**
1. Zoom in on the **G-10 sector** on the map.
2. Show the crimson hazard circle expanding to show the 4.2 km² flood radius and the **35,000 affected population** calculation overlay.
3. Move your cursor to the **Tactical Fleet Inventory** panel. Show the dynamic resource allocation card that has just rendered:
   * Highlight **Rescue Boats (BOAT-01 to 04)** and **Rescue Teams (TEAM-01 to 03)** deploying to G-10.
   * Point to the **Trade-off Explanation** card showing a written summary explaining the resource prioritization.
   * Highlight the **Fairness Check** indicator confirming that low-income areas (like the simultaneous I-8 heat crisis) received an automatic `1.15x` priority multiplier.

**🎤 Narration / Voiceover:**
> *"With classification locked, our SeverityPredictionAgent models the physical scale. A 4.2 square-kilometer impact circle expands over G-10, predicting thirty-five thousand citizens at risk. Instantly, the ResourceAllocationAgent computes the optimal dispatch plan. Look closely at the screen: because we have a simultaneous heatwave crisis in the low-income sector of I-8, the allocation algorithm applies an automatic 1.15-times impact multiplier to guarantee social equity. Rescue boats and teams are sent to the G-10 floods, while ambulances are dispatched to I-8, complete with a natural English trade-off explanation."*

---

### ⏳ Scene 5: Impact Simulation & Stakeholder Comms (3:00 – 3:45)
**Visual Actions on Screen:**
1. Point your cursor to the **Simulation Results Card** displaying:
   * **Casualties Prevented:** 92%.
   * **Amaan Response Latency:** 3.5 minutes (vs. Legacy manual dispatch baseline of 23 minutes).
2. Point to the **Broadcast & Comms** section showing the live generated notifications:
   * *Public Warning (Bilingual Urdu/English SMS)*
   * *Hospital Staging Order (Standby at PIMS)*
   * *Rescue 1122 Tactical Coordinates*

**🎤 Narration / Voiceover:**
> *"Next, the SimulationAgent models our intervention. Compared to traditional manual dispatch rooms that suffer from a twenty-three minute average setup delay, Amaan’s stateful engine registers a 540% response speed acceleration, dropping setup to just three point five minutes. Simultaneously, the StakeholderCommsAgent works in the background, drafting and formatting customized alerts: a critical staging standby order for PIMS Hospital, precise routing vectors for Rescue 1122, and a bilingual Urdu and English SMS warning for the general public."*

---

### ⏳ Scene 6: Mobile Client & Conversational Chat (3:45 – 4:30)
**Visual Actions on Screen:**
1. If you have the APK running, switch your screen capture to show the mobile layout or click on the **Chat** tab on the top-right settings bridge.
2. In the Chat prompt, type: `Kya G-10 mein flooding hai abhi?` (Roman Urdu).
3. Press enter and highlight the ChatAgent's instant response:
   * The response appears in natural Roman Urdu, confirming the flood, warning the citizen to avoid Jinnah Avenue, and detailing the nearest shelter location: **G-10 Markaz Community Center** with the **1122 helpline**.

**🎤 Narration / Voiceover:**
> *"Now let's look at the citizen's lifeline. Wrapped cleanly inside Ionic Capacitor, our native Android client runs the identical high-performance WebGL map with a compact five megabyte footprint. Navigating to the dedicated Chat tab, a citizen queries in Roman Urdu: 'Kya G-10 mein flooding hai abhi?' The translation-aware ChatAgent queries Firestore live, identifies that the user is inside the G-10 hazard boundary, and replies immediately in Roman Urdu, providing safety advice, the nearest shelter location, and emergency helpline details."*

---

### ⏳ Scene 7: The Grand Finale (4:30 – 5:00)
**Visual Actions on Screen:**
1. Zoom out the map to show the entire Islamabad-Rawalpindi twin city grid.
2. Hover over the pulsing status header: `STATUS: SECURE BRIDGE`.
3. Fade out the browser window and display the final submission slide: **Amaan CIRO — Autonomous Multi-Agent Crisis Response Orchestrator**.

**🎤 Narration / Voiceover:**
> *"Amaan CIRO is more than a technical blueprint—it is an explainable, robust, and highly scalable guardian for Pakistan’s citizens. By combining stateful LangGraph cyclicity, MapLibre WebGL vector power, and rapid Capacitor mobile packaging, Amaan bridges the gap between chaotic events and coordinated rescue. Deployed live, proven under API failure, and ready for the front lines. Thank you."*

---

## 🎤 Alternative Bilingual Chat Agent Voiceover (Urdu Translation)

If you wish to do a localized Urdu voiceover during the **Scene 6 (Chat Agent Showcase)**, read this script:

> *Roman Urdu:*
> *"Jab shehri hamare chat agent se Roman Urdu mein poochta hai: 'Kya G-10 mein flooding hai abhi?'—to hamara intelligent ChatAgent foran Firestore database se live status check karta hai. Yeh user ko batata hai ke G-10 flood zone ke andar aata hai, aur unhe foran G-10 Markaz Community Center shelter mein muntaqil hone ki hidayat deta hai, Rescue 1122 helpline ke sath."*

> *Urdu Script (اردو):*
> ”جب شہری ہمارے چیٹ ایجنٹ سے اردو یا رومن اردو میں پوچھتا ہے: ’کیا جی-ٹیں میں فلڈنگ ہے ابھی؟‘—تو ہمارا ذہین چیٹ ایجنٹ فوراً فائر اسٹور ڈیٹا بیس سے لائیو صورتحال حاصل کرتا ہے۔ یہ شہری کو بتاتا ہے کہ وہ اس وقت خطرے کے زون میں ہیں، اور انہیں قریبی شیلٹر یعنی ’جی-ٹیں مرکز کمیونٹی سینٹر‘ منتقل ہونے کی ہدایت فراہم کرتا ہے۔“

---

## 🛠️ Step-by-Step Instructions to Record your Screen Demo

To record an absolute **10/10 hackathon demo**, follow these guidelines:
1. **Resolution:** Record your browser in 1080p Full HD (1920x1080) at 60fps.
2. **Setup Live API:** Before recording, click the **Settings** gear icon in the top-right corner. Ensure the API URL is set to the live Cloud Run backend `https://amaan-ciro-485623882730.asia-south1.run.app/api`.
3. **Pacing:** Give the map transitions 2-3 seconds to render. Smooth vector zoom-ins look incredibly satisfying in video.
4. **Telemetry Hovering:** When a scenario runs, hover your cursor over the active resource units (e.g. `AMB-01`, `BOAT-02`) so the tooltips showing unit status and travel times pop up dynamically.
5. **No Editing Hacks:** The entire flow from clicking "Run Scenario A" to receiving the LangGraph response takes less than 6 seconds. Do not cut or fast-forward this section—showcasing the real-time speed of the agent workflow is your strongest selling point!
