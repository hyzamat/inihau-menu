/* Eastern Special Inihaw service worker — makes repeat visits instant and works on weak signal.
   Pages/scripts: network first (fresh prices), cached copy if offline.
   Images: cache first. Bump VERSION whenever you replace an image with the same name. */
var VERSION = "ei-v8";
var CORE = ["./", "index.html", "assets/css/style.css", "assets/js/menu-data.js", "assets/js/app.js", "assets/img/icon-192.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.destination === "image") {
    e.respondWith(
      caches.open(VERSION).then(function (c) {
        return c.match(req).then(function (hit) {
          return hit || fetch(req).then(function (res) {
            if (res.ok) c.put(req, res.clone());
            return res;
          });
        });
      })
    );
    return;
  }

  e.respondWith(
    fetch(req).then(function (res) {
      if (res.ok) {
        var copy = res.clone();
        caches.open(VERSION).then(function (c) { c.put(req, copy); });
      }
      return res;
    }).catch(function () {
      return caches.match(req, { ignoreSearch: true }).then(function (hit) {
        return hit || (req.mode === "navigate" ? caches.match("index.html") : undefined);
      });
    })
  );
});
