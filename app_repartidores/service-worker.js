/**
 * FARMACIAS MADRID - Service Worker para PWA Repartidores
 * Maneja cache offline y notificaciones.
 */

const CACHE_NAME = 'fm-repartidores-v3';
const URLS_TO_CACHE = [
    'index.html',
    'manifest.json'
];

// Install - cache archivos esenciales
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('[SW] Cacheando archivos');
            return cache.addAll(URLS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activate - limpiar caches anteriores
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(names => {
            return Promise.all(
                names.filter(name => name !== CACHE_NAME)
                     .map(name => caches.delete(name))
            );
        })
    );
    self.clients.claim();
});

// Fetch - Network first, fallback to cache
self.addEventListener('fetch', event => {
    // Solo cachear requests GET
    if (event.request.method !== 'GET') return;

    // Para API calls: network only (no cache)
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response(JSON.stringify({
                    ok: false,
                    error: 'Sin conexion',
                    offline: true
                }), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // Para archivos estaticos: network first, cache fallback
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Guardar en cache
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(() => {
                return caches.match(event.request);
            })
    );
});
