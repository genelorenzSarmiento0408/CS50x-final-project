// Modified https://github.com/umluizlima/flask-pwa/tree/master
(function () {
  if ("serviceWorker" in navigator) {
    // On load
    window.addEventListener("load", () => {
      // register the service worker
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

window.addEventListener("beforeinstallprompt", (e) => {
  console.log("beforeinstallprompt event fired");
});

window.addEventListener("appinstalled", (evt) => {
  app.logEvent("app", "installed");
});
