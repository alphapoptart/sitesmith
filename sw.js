/* Offline is the whole point, so everything needed to generate a site is
 * precached on install — app shell, the Python modules and the ~13MB runtime.
 * After one successful install the app never needs the network again. */

var VERSION = "sitesmith-6e0eac45ad35";
var SHELL = [
  "./",
  "index.html",
  "app.css",
  "app.js",
  "manifest.webmanifest",
  "icons/icon.svg",
  "icons/icon-180.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "py/bridge.py",
  "py/content.py",
  "py/design.py",
  "py/css.py",
  "py/layouts.py",
  "py/cards.py",
  "py/qr.py",
  "py/sitesmith.py",
  "py/version.json",
  "vendor/pyodide/pyodide.js",
  "vendor/pyodide/pyodide.asm.js",
  "vendor/pyodide/pyodide.asm.wasm",
  "vendor/pyodide/python_stdlib.zip",
  "vendor/pyodide/pyodide-lock.json"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(VERSION).then(function (cache) {
      // `cache: "reload"` bypasses the browser's own HTTP cache. Without it an
      // update can precache the files it was trying to replace.
      // addAll fails the whole install if any single file 404s, which is what we
      // want — a half-cached app that dies offline is worse than no install.
      return cache.addAll(SHELL.map(function (url) {
        return new Request(url, { cache: "reload" });
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== VERSION; })
                             .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (event) {
  var req = event.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Cache first: the app must behave identically with and without a connection.
  // A background refresh keeps it current whenever there happens to be signal.
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then(function (hit) {
      var live = fetch(req).then(function (res) {
        if (res && res.status === 200 && res.type === "basic") {
          var copy = res.clone();
          caches.open(VERSION).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () { return hit; });
      return hit || live;
    })
  );
});
