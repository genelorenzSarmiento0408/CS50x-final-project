// https://github.com/umluizlima/flask-pwa/tree/master
(function () {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then(function (registration) {
          console.log("Service Worker Registered");
          return registration;
        })
        .catch(function (err) {
          console.error("Unable to register service worker.", err);
        });
      navigator.serviceWorker.ready.then(function (registration) {
        console.log("Service Worker Ready");
      });
    });
  }
})();

let deferredPrompt;

window.addEventListener("beforeinstallprompt", (e) => {
  console.log("beforeinstallprompt event fired");
  e.preventDefault();
  deferredPrompt = e;
});

window.addEventListener("appinstalled", (evt) => {
  app.logEvent("app", "installed");
});
