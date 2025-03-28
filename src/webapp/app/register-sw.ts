export function registerServiceWorker() {
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker
          .register("/service-worker.js")
          .then((registration) => {
            console.log("Service Worker registered: ", registration)
          })
          .catch((registrationError) => {
            console.log("Service Worker registration failed: ", registrationError)
          })
      })
    }
  }
  
  