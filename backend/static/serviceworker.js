const CACHE_NAME = 'ehr-offline-v2';
const ASSETS_TO_CACHE = [
    // CSS
    '/static/css/theme.css',
    '/static/css/custom.css',
    // Webpack bundles (replaces individual /static/js/*.js files)
    '/static/dist/main.bundle.js',
    '/static/dist/vendors.bundle.js',
    '/static/dist/joint-diagram.chunk.js',
    // External CDN dependencies
    'https://unpkg.com/htmx.org@1.9.10',
    'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'
];

// Install event: Cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching all: app shell and content');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch event: Network First for HTML, Cache First for assets
self.addEventListener('fetch', (event) => {
    const requestUrl = new URL(event.request.url);

    // HTML pages: Network First
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(event.request);
            })
        );
        return;
    }

    // Static assets: Cache First
    // Check if the request is for one of our cached assets
    // We check if the pathname ends with one of our local assets or if the full URL matches (for external)
    const isCachedAsset = ASSETS_TO_CACHE.some(asset => {
        if (asset.startsWith('http')) {
            return requestUrl.href === asset;
        }
        return requestUrl.pathname === asset;
    });

    if (isCachedAsset) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
        return;
    }

    // Default: Network First (try network, fall back to cache if available)
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
