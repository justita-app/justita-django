let deferredPrompt; // Declare deferredPrompt variable globally

const cacheName = "V1";
const cacheAssets = [
  "/social",
  "/static/social/services/style.css",
  "/static/V3/homepage/images/main_banner.webp",
  "/static/fonts/vazri/Vazir-Medium.ttf",
  "/media/social/services/online_attorney_banner.webp",
  "/media/social/services/app_banner.webp",
  "/media/social/main/header-logo.png",
  "/media/social/services/free_councel_logo.webp",
  "/media/social/services/online_counceling_logo.webp",
  "/static/social/base/style.css",
  "/media/social/services/online_attorney_logo.webp",
  "/media/social/services/startups_lawyer.webp",
  "/media/social/services/fast_councel_logo.webp",
  "/media/social/services/issu_company.webp",
  "/media/social/services/complaint_logo.webp",
  "/media/social/services/live_counceling_logo.webp",
  "/media/social/main/question-icon.svg",
  "/media/social/services/contract_logo.webp",
  "/media/social/services/call_counceling_logo.webp",
  "/static/base/style.css",
];

// Call install
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(cacheName)
      .then((cache) => {
        return cache.addAll(cacheAssets);
      })
      .then(() => {
        self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker install failed:', error);
      })
  );
});

// Call activate
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== cacheName) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Call fetch
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        // Make a clone of the response
        const resClone = res.clone();
        // Open cache
        caches.open(cacheName)
          .then((cache) => {
            // Add the response to cache
            cache.put(e.request, resClone);
          });
        return res;
      })
      .catch(() => caches.match(e.request).then(res => res))
  );
});

