# Android and iOS release guide

## Architecture

Capacitor 8 packages the web UI locally under application ID `ai.panchang.regional` and display name Regional Panchang. The full classic calendar is the mobile launch screen; the React dashboard is available from its drawer. Both are bundled; classic calendar navigation stays inside the app. API calls use `https://calendar.sigq.in`, while normal web builds keep same-origin requests. Set `VITE_API_BASE_URL` to another HTTPS origin before `npm run mobile:sync` to change the mobile backend. Never put server secrets in Vite variables.

This is a hybrid app, retaining the existing frontend rather than a separate Swift/Kotlin rewrite. Astronomy and horoscope generation still require the hosted backend and connectivity. Lock-screen Live Activities currently only log messages; they are not implemented native features. The current React dashboard uses its existing default coordinates; use the classic calendar for location selection and regional language functionality.

## Prepare

Use Node 22 or newer, Android Studio with SDK 36 and Java 21 for Android. For iOS, use macOS and a compatible Xcode installation with iOS SDK support for Capacitor 8. Keep the existing bundle ID if this is an update; verify ownership before first publication.

```bash
cd frontend
npm ci
npm run mobile:sync
```

The Mobile Builds GitHub workflow produces an installable debug APK and unsigned AAB, and compiles an unsigned iOS simulator app. These are validation artifacts, not signed store submissions. Native builds must pass before release.

## Android: Play Store AAB

Open `npm run cap:open:android`. In Android Studio choose **Build > Generate Signed App Bundle / APK > Android App Bundle**. Create or select your upload key, retain it securely, and choose Release.

Alternatively supply `ANDROID_KEYSTORE_PATH` (absolute path), `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, and a monotonically increasing `ANDROID_VERSION_CODE` as environment variables, then:

```bash
cd android
./gradlew bundleRelease
```

Output: `app/build/outputs/bundle/release/app-release.aab`. Without signing environment variables the AAB is unsigned and cannot be uploaded. Never commit signing files or passwords. The current version name is 3.1.0; increment it and the version code for updates.

Upload the signed AAB to Play Console internal testing, test on actual phones, then complete the listing, content rating, Data safety, privacy URL and required testing before production submission.

## iOS: App Store and TestFlight

On macOS, run `npm run cap:open:ios`. In Xcode select the App target, set your Apple Developer team under Signing & Capabilities, confirm `ai.panchang.regional`, and set the marketing version/build number. Choose a generic iOS device, **Product > Archive**, then **Distribute App > App Store Connect**. Validate and upload; test through TestFlight before submitting for review. A simulator `.app` cannot be uploaded as an IPA.

## Release acceptance

Test dashboard and classic calendar, all supported languages, state/date switching, denied location permission and manual selection, slow/offline network error behavior, dark/light themes, notches/system bars, rotation, Android Back, native/browser share behavior and the local privacy link on physical devices. Browser image sharing/download fallback needs device verification; there is no dedicated native share plugin yet. This implementation does not claim offline astronomy calculations.

Review the existing privacy policy against actual data collection and confirm the support email is monitored. Publish the policy at a working public HTTPS URL (the backend already serves `/privacy`). Review location disclosures and any AI horoscope data processing. Replace template icons/splash artwork with approved branding before release. Complete store screenshots, description, support URL, privacy disclosures and Apple export-compliance answers. Recheck current store and SDK requirements on submission day.

The README's festival accuracy corpus remains a release gate. Store approval and authoritative date accuracy are not implied by a successful app build.
