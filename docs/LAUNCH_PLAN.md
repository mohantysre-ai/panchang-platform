# Regional Panchang launch plan

## Product goal
Build the most trustworthy, fastest and most region-aware Hindu Panchang/calendar experience for India and the diaspora. The product should win on **accuracy + regional authenticity + modern mobile UX**, not on feature count alone.

## Release gates

### Gate 1 — Astronomical correctness
- Swiss Ephemeris Lahiri sidereal calculations remain the deterministic source.
- Festival matching uses sunrise tithi and lunar-month rules instead of Gregorian date guesses.
- Solar festivals use sidereal solar ingress rules.
- Amanta and Purnimanta month systems are explicit in festival rules.
- Regional solar month names are derived from the actual sidereal Sun sign.
- Build a reference corpus for 2025–2030 and compare every major festival against trusted published Panchang references before production certification.

### Gate 2 — Regional authenticity
- All 28 states + 8 union territories are selectable.
- State config controls calendar system, regional month system, muhurat system, visual style, accent and priority fields.
- Gowri Panchangam is shown for South Indian configurations that use it; Choghadiya is shown for North/West/East configurations.
- Regional language fallback exists for every state; native translations should be expanded before each regional marketing launch.

### Gate 3 — Product UX
- Material-inspired mobile drawer, bottom navigation and edge-to-edge safe-area layout.
- Fast launch splash with Om mark and regional identity.
- Installable PWA with offline shell caching.
- Calendar cells show festival markers and accessible labels.
- Font-size control persists locally.
- Desktop keeps the dense calendar + detail split view.

### Gate 4 — Mobile distribution
- Capacitor Android/iOS shells generated from the same web application.
- Android adaptive icon, launch screen, status/navigation bar colors and deep links.
- iOS safe-area, launch screen and universal-link configuration.
- Play Store/App Store privacy, data safety and notification declarations.

## Competitive moat
1. **Accuracy ledger:** publish calculation engine/version, ayanamsa, location and rule system in an expandable "Why this date?" panel.
2. **Regional mode:** selecting a state changes month naming, festivals, muhurat, language and calendar layout together.
3. **Festival intelligence:** festival cards include date, tithi, sunrise/sunset, vrat status and regional variants.
4. **Fast calendar:** cache month data and prefetch adjacent months.
5. **Personalization:** location, preferred tradition, language, notification interests and home-screen widgets.
6. **Shareability:** generate clean festival/day cards for WhatsApp and social sharing.
7. **Trust:** never let an LLM decide astronomical dates; AI may explain terminology but cannot mutate deterministic calculations.

## Next engineering backlog
- Reference-date validation harness for 2025–2030.
- Full tithi transition times and sunrise/sunset-aware festival decision rules.
- Sankranti, Ekadashi, Pradosh, Purnima, Amavasya and regional vrata catalog.
- Regional calendar variants: Bengali, Odia, Tamil, Malayalam, Kannada, Telugu, Gujarati, Marathi, Punjabi, Assamese and Hindi/Purnimanta.
- Festival variant resolver for state-specific observance and local exceptions.
- Location picker with geocoding and saved cities.
- Notifications for festivals, Ekadashi, Pradosh and user-selected events.
- Android/iOS native QA and store release builds.
- Performance budgets: first meaningful paint < 2s on a mid-range Android over 4G; month navigation should feel instant from cache.

## Launch strategy
Start with India-first SEO pages for each state, major city and festival. Every indexed page must contain server-rendered/crawlable festival and Panchang metadata, canonical URLs, structured data where appropriate, and a clear install CTA. Use regional language landing pages rather than one generic English page.
