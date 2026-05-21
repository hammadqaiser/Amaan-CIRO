# Amaan CIRO — Project Vision & Scope

## One-Line Description

Pakistan's first autonomous multi-agent crisis response system — detects, classifies, and coordinates emergency response in real time using a LangGraph-based stateful agent orchestration graph, deployed as a high-performance web dashboard and native Android app.

## Problem Statement

Pakistan loses billions of rupees annually to preventable crisis mismanagement. The 2022 Karachi floods killed 36 people and caused PKR 14 billion in damage — not because the crisis was unforeseeable, but because response was reactive, fragmented, and slow. Emergency services received information from multiple disconnected channels with no unified intelligence to determine where to go first, which signals to trust, and how to split limited resources between simultaneous emergencies.

Amaan solves this by making every response decision in seconds, with full transparency on why each decision was made.

## Target Users

1. **Emergency Operations Center (EOC) operators** — Primary users. Command center view via React web dashboard and Android app.
2. **NDMA / PDMA field coordinators** — Resource allocation tracking and incident management.
3. **Citizens** — Reporting incidents, receiving location-based alerts, querying the multilingual chat system.
4. **Emergency services (Rescue 1122, Police, Ambulance)** — Dispatch coordination and tactical routing.

## Success Metrics

| Metric | Target |
|--------|--------|
| Signal fusion latency | < 5 seconds from receipt to classification |
| Resource allocation decision | < 10 seconds for single crisis |
| False positive rate | < 15% (demonstrated via contradiction detection) |
| Simultaneous crises supported | Minimum 2 (demo shows 3) |
| Agent trace completeness | 100% of decisions logged with reasoning |
| APK size | Under 5 MB |

## Scope Boundaries

What Amaan **does**:
- Multi-source signal fusion with credibility scoring
- Autonomous crisis classification and severity prediction
- Constrained resource allocation with fairness guarantees
- Before/after impact simulation
- Bilingual stakeholder communications (5 audience types)
- Multilingual citizen chat (English, Urdu, Roman Urdu)
- False alarm detection and recovery

What Amaan **does not do**:
- Real 911/Rescue 1122 dispatch integration (simulation only)
- Payment processing
- Social media platform features
- Long-term disaster prediction or climate modeling

## Competitive Differentiator

Most crisis systems are dashboards that show what happened. Amaan is an intelligence system that decides what to do next, explains every decision through structured reasoning traces, and self-corrects when it detects false alarms or contradictions.

## Production Deployments

| Platform | URL |
|----------|-----|
| Web Command Dashboard (Vercel) | [amaan-ciro-web.vercel.app](https://amaan-ciro-web.vercel.app) |
| Backend API & Swagger (Cloud Run) | [amaan-ciro-...run.app/docs](https://amaan-ciro-485623882730.asia-south1.run.app/docs) |
| Android APK | `src/mobile/android/app/build/outputs/apk/debug/app-debug.apk` |