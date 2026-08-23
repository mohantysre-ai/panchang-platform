# Play Data Safety & Apple App Privacy — Answer Key

Based on a full code review on 2026-08-23 (commit `0bfd653` and the location-coarsening
fix that shipped with it). Re-check this if you add any new SDK, endpoint, or data flow —
these answers describe what the app *actually does today*, not a general template.

---

## Google Play Console → App content → Data safety

**Does your app collect or share any of the required user data types?** → Yes

### Data type: Location → Approximate location
- Collected: **Yes**
- Shared: **Yes** — with OpenStreetMap / Nominatim, for app functionality only
- Purpose: **App functionality**
- Is this data collection required or optional: **Optional** — a manual state picker is
  always available; the "detect my region" flow is never forced
- Is data processed ephemerally: **No** — results are cached to disk keyed off the
  (rounded) coordinate, so it doesn't qualify for Google's ephemeral-processing exemption
- Do **not** check "Precise location." As of the coarsening fix, every endpoint rounds to
  2 decimal places (~1.1 km) before the value is used for anything, so this is
  Approximate location only.

### Every other category (Personal info, Financial info, Health & fitness, Messages,
Photos/videos, Audio files, Files & docs, Calendar, Contacts, App activity, Web browsing,
App info & performance, Device or other IDs):
- **Not collected.**

### Security practices
- Data is encrypted in transit: **Yes** (HTTPS throughout)
- Independent security review: **No** — leave unchecked unless you actually commission one
- User-initiated data deletion path: see note below before answering

> **On the deletion question:** nothing in this app is linked to an account or device ID,
> so there's no way to find and delete "one specific person's" cached entry — cache keys
> are shared across anyone who happens to query the same rounded coordinate and date.
> Google's own guidance is that the deletion question is about data linked to an
> identifiable user, which this isn't. If you want the strongest possible answer here
> (and a generally good practice), add a scheduled job that purges cache files older than
> ~90 days — say the word and I'll write it.

---

## Apple App Store Connect → App Privacy

### Data type: Location → **Coarse Location**
- Collected: **Yes**
- Linked to the user's identity: **No** (no accounts anywhere in the app)
- Used for tracking (Apple's definition): **No**
- Purpose: **App Functionality**

### Every other data type Apple lists (Contact Info, Health & Fitness, Financial Info,
Browsing/Search History, Identifiers, Purchases, User Content, Diagnostics, Contacts,
etc.):
- **Not Collected.**

### App Tracking Transparency (ATT)
**Not required.** ATT only applies when you link data to identity or share it with a
data broker / ad network for cross-app tracking — this app does neither. No ATT prompt
needed, and you can skip the whole ATT integration.

### Privacy manifest (`PrivacyInfo.xcprivacy`)
Capacitor 8 ships its own manifest covering its core APIs. Since there's no other native
SDK in this app (no ads, no analytics, no crash reporter), you shouldn't need to add
anything yourself — just build against a current Capacitor release.

---

## Before you submit, in order

1. Host `frontend/privacy.html` (now served at `/privacy` and `/privacy.html` by the
   backend) and put that URL in both consoles' privacy policy field.
2. Run `npx cap add android` / `npx cap add ios`, then add the location purpose strings
   Capacitor's docs specify for `Geolocation` (or, if you keep using raw
   `navigator.geolocation`, the plain `NSLocationWhenInUseUsageDescription` /
   `ACCESS_COARSE_LOCATION` entries) before your first native build.
3. Fill in the two forms above exactly as written.
4. Re-read this file any time you add a new third-party SDK, endpoint, or permission —
   these answers stop being accurate the moment the app's data flows change.
