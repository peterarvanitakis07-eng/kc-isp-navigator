// KC ISP Navigator — Service Worker
// Caches app shell + FCC block data for offline use.
// Railway proxy calls, Census geocoding, and FCC API calls are never cached.

const CACHE = 'kc-isp-v1';

const APP_SHELL = [
  './',
  './index.html',
];

// ── Install: cache the app shell ─────────────────────────────────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(APP_SHELL))
  );
  self.skipWaiting(); // activate immediately
});

// ── Activate: delete old cache versions ──────────────────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch: smart caching strategy ────────────────────────────────────────────
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Never cache: proxy, Census geocoding, FCC API, QR code generator
  const passThrough = (
    url.hostname.includes('railway.app') ||
    url.hostname.includes('census.gov') ||
    url.hostname.includes('fcc.gov') ||
    url.hostname.includes('qrserver.com')
  );
  if (passThrough) return;

  // Block data JSON: stale-while-revalidate
  // Show cached data instantly, update cache in background
  if (url.pathname.includes('block_isp_lookup.json')) {
    e.respondWith(
      caches.open(CACHE).then(async cache => {
        const cached = await cache.match(e.request);
        // Always try to refresh in background
        const fresh = fetch(e.request).then(r => {
          if (r && r.status === 200) cache.put(e.request, r.clone());
          return r;
        }).catch(() => null);
        // Return cached immediately if available, otherwise wait for network
        return cached || fresh;
      })
    );
    return;
  }

  // App shell (HTML, CSS, JS): cache-first, fall back to network
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(r => {
        if (r && r.status === 200 && r.type !== 'opaque') {
          caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        }
        return r;
      }).catch(() => cached); // if network fails and no cache, fail gracefully
    })
  );
});
