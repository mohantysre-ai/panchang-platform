/* Network-first shell assets so drawer font / calendar icon updates are not stuck on old Hindi-font CSS */
const CACHE = "regional-panchang-v7";
const SHELL = [
  "/",
  "/manifest.webmanifest",
  "/fonts.css",
  "/i18n.js",
  "/regional-ui.css",
  "/regional-ui.js",
  "/state-options.js",
  "/app-shell.css",
  "/app-shell.js",
  "/launch-enhancements.js",
  "/share-card.js",
  "/live-activity.js",
  "/classic-extras.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || !e.request.url.startsWith(self.location.origin)) return;
  const url = new URL(e.request.url);
  const isShell =
    url.pathname === "/" ||
    url.pathname.endsWith(".js") ||
    url.pathname.endsWith(".css") ||
    url.pathname.endsWith(".html");

  if (isShell) {
    // Always prefer network for UI chrome so font/CSS fixes apply immediately
    e.respondWith(
      fetch(e.request)
        .then((r) => {
          const copy = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return r;
        })
        .catch(() => caches.match(e.request).then((hit) => hit || caches.match("/")))
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then(
      (hit) =>
        hit ||
        fetch(e.request).then((r) => {
          const copy = r.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return r;
        })
    )
  );
});
