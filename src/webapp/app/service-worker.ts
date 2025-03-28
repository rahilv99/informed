/// <reference lib="webworker" />

// This service worker can be customized!
// See https://developers.google.com/web/tools/workbox/modules
// for the list of available Workbox modules, or add any other
// code you'd like.

// Instead of redeclaring self, use type assertion
const sw = self as unknown as ServiceWorkerGlobalScope

// Skip waiting so the service worker activates immediately
sw.addEventListener("install", (event) => {
  sw.skipWaiting()
})

// Claim clients so the service worker takes control immediately
sw.addEventListener("activate", (event) => {
  event.waitUntil(sw.clients.claim())
})

// Listen for messages from clients
sw.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    sw.skipWaiting()
  }
})

// Export an empty object to satisfy TypeScript module requirements
export {}

