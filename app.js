/* sitesmith — phone app.
 *
 * There is no JavaScript port of the generator. Pyodide runs the same Python that
 * the desktop skill runs, so anything this produces is identical to the Mac output.
 * This file only handles the interface, storage and packaging.
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var KEY = "sitesmith.library.v1";   // every site, keyed by id
  var LEGACY = "sitesmith.brief.v1";  // single-brief format from the first build
  var GH_KEY = "sitesmith.github.v1"; // token + last repo, this device only
  var py = null;              // pyodide instance
  var bridge = null;          // py/bridge.py module proxy
  var CAT = null;             // catalogue: layouts, themes, presets
  var brief = {};             // current answers
  var picked = { layout: "classic", theme: "slate" };
  var built = null;           // last build result
  var filter = { layout: "all", theme: "all" };
  var library = [];           // [{id, name, brief, picked, updated, live}]
  var currentId = null;

  /* ---------------- boot ---------------- */

  function status(text, pct) {
    $("boot-status").textContent = text;
    if (pct != null) $("boot-bar").style.width = pct + "%";
  }

  async function boot() {
    try {
      status("Loading the Python runtime…", 10);
      py = await loadPyodide({ indexURL: "vendor/pyodide/" });

      status("Loading the generator…", 55);
      var names = ["content.py", "design.py", "css.py", "layouts.py",
                   "cards.py", "qr.py", "sitesmith.py", "bridge.py"];
      var sources = await Promise.all(names.map(function (n) {
        return fetch("py/" + n).then(function (r) {
          if (!r.ok) throw new Error("could not load py/" + n);
          return r.text();
        });
      }));
      py.FS.mkdirTree("/app");
      names.forEach(function (n, i) { py.FS.writeFile("/app/" + n, sources[i]); });
      py.runPython("import sys\nif '/app' not in sys.path: sys.path.insert(0, '/app')");

      status("Warming up…", 80);
      bridge = py.pyimport("bridge");
      CAT = JSON.parse(bridge.catalogue());

      status("Ready", 100);
      start();
    } catch (err) {
      console.error(err);
      status("Could not start: " + err.message);
      $("boot-note").textContent =
        "The first run needs a connection to fetch the runtime. Once it has loaded " +
        "successfully one time, it works with no signal.";
      $("boot-retry").hidden = false;
    }
  }

  $("boot-retry").addEventListener("click", function () {
    $("boot-retry").hidden = true;
    boot();
  });

  function start() {
    buildPresetOptions();
    buildChips();
    loadLibrary();
    $("boot").hidden = true;
    $("app").hidden = false;
    $("topbar").hidden = false;
    renderSites();
    show(library.length ? "step-sites" : "step-brief");
    if (!library.length) newSite(true);
  }

  /* ---------------- library ---------------- */

  function loadLibrary() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) { library = JSON.parse(raw) || []; return; }
    } catch (e) { library = []; }

    // Carry over anything saved by the single-brief version of the app.
    try {
      var old = JSON.parse(localStorage.getItem(LEGACY) || "null");
      if (old && old.brief && old.brief.name) {
        library = [{
          id: newId(), name: old.brief.name, brief: old.brief,
          picked: old.picked || { layout: "classic", theme: "slate" },
          updated: Date.now(), live: null
        }];
        persist();
      }
    } catch (e) { /* nothing to carry over */ }
  }

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(library)); }
    catch (e) { toast("Storage is full or blocked — this site will not be kept"); }
  }

  function newId() {
    return "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function currentEntry() {
    return library.filter(function (s) { return s.id === currentId; })[0] || null;
  }

  function save() {
    brief = readForm();
    var entry = currentEntry();
    if (!entry) {
      entry = { id: currentId || newId(), live: null };
      currentId = entry.id;
      library.unshift(entry);
    }
    entry.name = brief.name || "Untitled";
    entry.brief = brief;
    entry.picked = picked;
    entry.updated = Date.now();
    persist();
  }

  function newSite(silent) {
    currentId = newId();
    brief = {};
    picked = { layout: "classic", theme: "slate" };
    built = null;
    $("brief-form").reset();
    $("preset-select").value = "general";
    $("services-raw").value = "";
    $("show-prices").checked = false;
    $("tiles").dataset.forName = "";
    syncPriceRows();
    if (!silent) show("step-brief");
  }

  function openSite(id) {
    var entry = library.filter(function (s) { return s.id === id; })[0];
    if (!entry) return;
    currentId = entry.id;
    brief = entry.brief || {};
    picked = entry.picked || { layout: "classic", theme: "slate" };
    built = null;
    $("brief-form").reset();
    fillForm(brief);
    syncPriceRows();
    (brief.services || []).forEach(function (s) {
      if (!s || !s.title) return;
      var row = $("price-rows").querySelector('[data-name="' + cssEscape(s.title) + '"]');
      if (row) row.querySelector("input").value = s.price || "";
    });
    $("tiles").dataset.forName = "";
    doBuild();
  }

  function renderSites() {
    var host = $("sites-list");
    host.innerHTML = "";
    $("sites-empty").hidden = library.length > 0;
    $("sites-sub").textContent = library.length
      ? library.length + (library.length === 1 ? " site" : " sites") +
        ", kept on this phone. Tap one to open it."
      : "Everything you build is kept on this phone.";

    library.slice().sort(function (a, b) { return (b.updated || 0) - (a.updated || 0); })
      .forEach(function (entry) {
        var li = document.createElement("li");
        li.className = "site";
        var design = labelFor(CAT.layouts, (entry.picked || {}).layout) + " / " +
                     labelFor(CAT.themes, (entry.picked || {}).theme);
        li.innerHTML =
          '<button class="site__open">' +
            '<span class="site__name">' + esc(entry.name || "Untitled") + '</span>' +
            '<span class="site__meta">' + esc(design) + " · " + when(entry.updated) + '</span>' +
            (entry.live ? '<span class="site__live">Live</span>' : '') +
          '</button>' +
          '<button class="site__more" aria-label="More">⋯</button>';
        li.querySelector(".site__open").addEventListener("click", function () { openSite(entry.id); });
        li.querySelector(".site__more").addEventListener("click", function () { siteMenu(entry); });
        host.appendChild(li);
      });
  }

  function when(ts) {
    if (!ts) return "just now";
    var mins = Math.round((Date.now() - ts) / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return mins + "m ago";
    var hrs = Math.round(mins / 60);
    if (hrs < 24) return hrs + "h ago";
    return new Date(ts).toLocaleDateString();
  }

  function siteMenu(entry) {
    var choice = prompt(
      entry.name + "\n\n1 — Open\n2 — Duplicate\n3 — Export the brief\n4 — Delete" +
      (entry.live ? "\n5 — Open the live site" : "") + "\n\nType a number:");
    if (choice === "1") { openSite(entry.id); }
    else if (choice === "2") {
      var copy = JSON.parse(JSON.stringify(entry));
      copy.id = newId();
      copy.name = entry.name + " (copy)";
      copy.brief = Object.assign({}, entry.brief, { name: copy.name });
      copy.live = null;
      copy.updated = Date.now();
      library.unshift(copy); persist(); renderSites();
      toast("Duplicated");
    } else if (choice === "3") {
      saveBlob(new Blob([JSON.stringify(entry.brief, null, 2)], { type: "application/json" }),
               slugify(entry.name) + "-brief.json");
    } else if (choice === "4") {
      if (confirm("Delete " + entry.name + "? This cannot be undone.")) {
        library = library.filter(function (s) { return s.id !== entry.id; });
        if (currentId === entry.id) { currentId = null; built = null; }
        persist(); renderSites();
        toast("Deleted");
      }
    } else if (choice === "5" && entry.live) {
      window.open(entry.live, "_blank");
    }
  }

  function slugify(s) {
    return String(s || "site").toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "site";
  }

  $("new-site").addEventListener("click", function () { newSite(); });

  /* ---------------- form ---------------- */

  function buildPresetOptions() {
    var sel = $("preset-select");
    sel.innerHTML = "";
    CAT.presets.forEach(function (p) {
      var o = document.createElement("option");
      o.value = p.key; o.textContent = p.label;
      sel.appendChild(o);
    });
    sel.value = "general";
  }

  function currentPreset() {
    var key = $("preset-select").value;
    return CAT.presets.filter(function (p) { return p.key === key; })[0] || CAT.presets[0];
  }

  function serviceNames() {
    return $("services-raw").value.split("\n")
      .map(function (s) { return s.trim(); })
      .filter(Boolean);
  }

  function syncPriceRows() {
    var on = $("show-prices").checked;
    $("price-block").hidden = !on;
    if (!on) { $("price-rows").innerHTML = ""; return; }

    var names = serviceNames();
    if (!names.length) names = currentPreset().services;
    var existing = {};
    Array.prototype.forEach.call($("price-rows").children, function (row) {
      existing[row.dataset.name] = row.querySelector("input").value;
    });
    var prior = (brief.services || []).reduce(function (acc, s) {
      if (s && s.title) acc[s.title] = s.price || "";
      return acc;
    }, {});

    $("price-rows").innerHTML = "";
    names.forEach(function (name) {
      var row = document.createElement("div");
      row.className = "price-row";
      row.dataset.name = name;
      var label = document.createElement("span");
      label.textContent = name;
      var input = document.createElement("input");
      input.placeholder = "18";
      input.value = existing[name] != null ? existing[name] : (prior[name] || "");
      input.setAttribute("aria-label", "Price for " + name);
      row.appendChild(label); row.appendChild(input);
      $("price-rows").appendChild(row);
    });
  }

  function readForm() {
    var form = $("brief-form");
    var out = {};
    ["name", "tagline", "preset", "city", "phone", "email", "address", "hours",
     "owner", "owner_title", "years", "domain", "cta", "currency", "about"].forEach(function (k) {
      var el = form.elements[k];
      out[k] = el ? el.value.trim() : "";
    });
    out.currency_after = $("currency-after").value === "1";
    if (!$("show-prices").checked) { out.currency = ""; }

    var prices = {};
    Array.prototype.forEach.call($("price-rows").children, function (row) {
      prices[row.dataset.name] = row.querySelector("input").value.trim();
    });
    var names = serviceNames();
    if (!names.length) names = $("show-prices").checked ? currentPreset().services : [];
    out.services = names.map(function (n) { return { title: n, price: prices[n] || "" }; });
    out.logo = logoState.uri;
    out.logo_has_name = $("logo-has-name").checked;
    out.logo_needs_light = $("logo-needs-light").checked;
    out.layout = picked.layout;
    out.theme = picked.theme;
    return out;
  }

  function fillForm(b) {
    var form = $("brief-form");
    Object.keys(b).forEach(function (k) {
      var el = form.elements[k];
      if (el && typeof b[k] === "string") el.value = b[k];
    });
    if (b.preset) $("preset-select").value = b.preset;
    if (b.services && b.services.length) {
      $("services-raw").value = b.services.map(function (s) {
        return typeof s === "string" ? s : s.title;
      }).join("\n");
      var priced = b.services.some(function (s) { return s && s.price; });
      $("show-prices").checked = priced || !!b.currency;
    }
    if (b.currency) $("currency").value = b.currency;
    $("currency-after").value = b.currency_after ? "1" : "0";
    $("logo-has-name").checked = !!b.logo_has_name;
    $("logo-needs-light").checked = b.logo_needs_light !== false;
    setLogo(b.logo || "", true);
  }

  // --- logo -----------------------------------------------------------------
  var logoState = { uri: "" };
  var LOGO_MAX = 512 * 1024;
  var LOGO_TYPES = ["image/png", "image/jpeg", "image/gif", "image/webp",
                    "image/svg+xml"];

  function logoError(msg) {
    var el = $("logo-error");
    el.textContent = msg || "";
    el.hidden = !msg;
  }

  function setLogo(uri, quiet) {
    logoState.uri = uri || "";
    $("logo-empty").hidden = !!uri;
    $("logo-set").hidden = !uri;
    if (!quiet) logoError("");
    if (!uri) { $("logo-thumb").removeAttribute("src"); $("logo-meta").textContent = ""; return; }
    $("logo-thumb").src = uri;
    var img = new Image();
    img.onload = function () {
      var kb = Math.round(uri.length * 0.75 / 1024);
      var square = img.width / img.height >= 0.8 && img.width / img.height <= 1.25;
      $("logo-meta").textContent = img.width + " x " + img.height + " · ~" + kb + " KB · "
        + (square ? "square, so it doubles as the favicon"
                  : "wide, so the monogram stays as the favicon");
    };
    img.src = uri;
  }

  function pickLogo(file) {
    logoError("");
    if (!file) return;
    if (LOGO_TYPES.indexOf(file.type) < 0) {
      logoError("That is a " + (file.type || "unknown file") + ". Use PNG, JPEG, GIF, WebP or SVG.");
      return;
    }
    if (file.size > LOGO_MAX) {
      logoError(Math.round(file.size / 1024) + " KB is too big — keep it under 512 KB.");
      return;
    }
    var reader = new FileReader();
    reader.onerror = function () { logoError("Could not read that file."); };
    reader.onload = function () {
      setLogo(String(reader.result));
      save();
    };
    reader.readAsDataURL(file);
  }

  $("logo-pick").addEventListener("click", function () { $("logo-file").click(); });
  $("logo-replace").addEventListener("click", function () { $("logo-file").click(); });
  $("logo-remove").addEventListener("click", function () { setLogo(""); save(); });
  $("logo-file").addEventListener("change", function (e) {
    pickLogo(e.target.files && e.target.files[0]);
    e.target.value = "";
  });

  $("preset-select").addEventListener("change", function () {
    if (!serviceNames().length) $("services-raw").value = currentPreset().services.join("\n");
    var cta = $("brief-form").elements.cta;
    if (!cta.value) cta.placeholder = currentPreset().cta;
    syncPriceRows();
  });
  $("use-defaults").addEventListener("click", function () {
    $("services-raw").value = currentPreset().services.join("\n");
    syncPriceRows();
  });
  $("services-raw").addEventListener("change", syncPriceRows);
  $("show-prices").addEventListener("change", syncPriceRows);

  $("load-demo").addEventListener("click", function () {
    var demo = JSON.parse(bridge.demo_brief());
    brief = demo;
    fillForm(demo);
    picked = { layout: demo.layout || "bold", theme: demo.theme || "ocean" };
    syncPriceRows();
    (demo.services || []).forEach(function (s) {
      var row = $("price-rows").querySelector('[data-name="' + cssEscape(s.title) + '"]');
      if (row) row.querySelector("input").value = s.price || "";
    });
    save();
    toast("Demo business loaded");
  });

  function cssEscape(s) { return String(s).replace(/["\\]/g, "\\$&"); }

  /* ---------------- navigation ---------------- */

  var STEPS = ["step-sites", "step-brief", "step-gallery", "step-build"];
  var BACK = { "step-brief": "step-sites", "step-gallery": "step-brief",
               "step-build": "step-gallery" };

  function show(id) {
    STEPS.forEach(function (s) { $(s).hidden = s !== id; });
    $("back-btn").hidden = id === "step-sites";
    $("topbar-title").textContent =
      id === "step-sites" ? "sitesmith" : (brief.name || "Your business");
    window.scrollTo(0, 0);
  }

  $("back-btn").addEventListener("click", function () {
    var current = STEPS.filter(function (s) { return !$(s).hidden; })[0];
    if (current === "step-brief") { save(); renderSites(); }
    show(BACK[current] || "step-sites");
  });

  $("to-gallery").addEventListener("click", function () {
    var name = $("brief-form").elements.name;
    if (!name.value.trim()) { name.focus(); toast("The business needs a name"); return; }
    save();
    show("step-gallery");   // must be visible before renderGallery measures the tiles
    renderGallery();
  });

  $("change-design").addEventListener("click", function () { show("step-gallery"); });

  /* ---------------- gallery ---------------- */

  function buildChips() {
    chipRow($("layout-chips"), "layout", CAT.layouts);
    chipRow($("theme-chips"), "theme", CAT.themes);
  }

  function chipRow(host, group, items) {
    host.innerHTML = "";
    host.appendChild(chip(group, "all", "All", true));
    items.forEach(function (it) { host.appendChild(chip(group, it.key, it.label, false)); });
  }

  function chip(group, value, label, on) {
    var b = document.createElement("button");
    b.className = "chip"; b.textContent = label;
    b.dataset.group = group; b.dataset.value = value;
    b.setAttribute("aria-pressed", on ? "true" : "false");
    b.addEventListener("click", function () {
      filter[group] = value;
      Array.prototype.forEach.call(
        document.querySelectorAll('.chip[data-group="' + group + '"]'),
        function (c) { c.setAttribute("aria-pressed", String(c === b)); });
      applyFilter();
    });
    return b;
  }

  function applyFilter() {
    var shown = 0;
    Array.prototype.forEach.call(document.querySelectorAll(".tile"), function (tile) {
      var ok = (filter.layout === "all" || tile.dataset.layout === filter.layout) &&
               (filter.theme === "all" || tile.dataset.theme === filter.theme);
      tile.hidden = !ok;
      if (ok) shown++;
    });
    $("gallery-empty").hidden = shown > 0;
    $("gallery-count").textContent = shown + " of " +
      (CAT.layouts.length * CAT.themes.length) + " shown. Every one uses your own words.";
    fitShots();
    lazyRender();
  }

  function renderGallery() {
    var host = $("tiles");
    if (host.dataset.forName === (brief.name || "") + "|" + JSON.stringify(brief.services || [])) {
      applyFilter();
      return;
    }
    host.dataset.forName = (brief.name || "") + "|" + JSON.stringify(brief.services || []);
    host.innerHTML = "";
    CAT.layouts.forEach(function (l) {
      CAT.themes.forEach(function (t) {
        host.appendChild(tileFor(l, t));
      });
    });
    applyFilter();
  }

  function tileFor(l, t) {
    var tile = document.createElement("div");
    tile.className = "tile";
    tile.dataset.layout = l.key;
    tile.dataset.theme = t.key;
    tile.innerHTML =
      '<div class="tile__shot"><div class="spin">…</div></div>' +
      '<div class="tile__body">' +
        '<div class="tile__name">' + esc(l.label) + ' <span>/ ' + esc(t.label) + '</span></div>' +
        '<p class="tile__blurb">' + esc(t.blurb) + '</p>' +
        '<button class="btn btn--sm">Use this design</button>' +
      '</div>';
    tile.querySelector("button").addEventListener("click", function () {
      picked = { layout: l.key, theme: t.key };
      save();
      doBuild();
    });
    return tile;
  }

  /* Rendering 160 previews at once would lock the phone up, so they are drawn
     only as they scroll into view, one animation frame at a time. */
  var queue = [];
  var pumping = false;

  function lazyRender() {
    queue = Array.prototype.filter.call(document.querySelectorAll(".tile"), function (tile) {
      if (tile.hidden || tile.dataset.done) return false;
      var box = tile.getBoundingClientRect();
      // A hidden ancestor collapses every rect to zero, which would look like
      // "everything is on screen" and render all 160 at once.
      if (!box.height) return false;
      return box.top < window.innerHeight * 2 && box.bottom > -window.innerHeight;
    });
    pump();
  }

  function pump() {
    if (pumping || !queue.length) return;
    pumping = true;
    var tile = queue.shift();
    requestAnimationFrame(function () {
      try { drawTile(tile); } catch (e) { console.error(e); }
      pumping = false;
      if (queue.length) setTimeout(pump, 0);
    });
  }

  function drawTile(tile) {
    if (tile.dataset.done) return;
    tile.dataset.done = "1";
    var html = bridge.preview(JSON.stringify(brief), tile.dataset.layout, tile.dataset.theme);
    var shot = tile.querySelector(".tile__shot");
    var frame = document.createElement("iframe");
    frame.setAttribute("scrolling", "no");
    frame.setAttribute("tabindex", "-1");
    frame.setAttribute("aria-hidden", "true");
    frame.srcdoc = html;
    shot.innerHTML = "";
    shot.appendChild(frame);
    fitOne(shot);
  }

  function fitOne(shot) {
    var frame = shot.querySelector("iframe");
    if (!frame) return;
    var k = shot.clientWidth / 1180;
    frame.style.transform = "scale(" + k + ")";
  }

  function fitShots() {
    Array.prototype.forEach.call(document.querySelectorAll(".tile__shot"), fitOne);
  }

  window.addEventListener("resize", function () { fitShots(); lazyRender(); });
  window.addEventListener("scroll", function () { lazyRender(); }, { passive: true });

  /* ---------------- build ---------------- */

  function doBuild() {
    toast("Building…");
    setTimeout(function () {
      try {
        built = JSON.parse(bridge.build(JSON.stringify(brief), picked.layout, picked.theme));
      } catch (e) {
        console.error(e);
        toast("Build failed — see the console");
        return;
      }
      var layoutLabel = labelFor(CAT.layouts, picked.layout);
      var themeLabel = labelFor(CAT.themes, picked.theme);
      $("build-title").textContent = built.name;
      $("build-sub").textContent = layoutLabel + " / " + themeLabel + " · " +
        (Object.keys(built.files).length
         + Object.keys(built.binary || {}).length) + " files";
      showSitePreview();
      showCards();
      showTodo();
      save();
      renderSites();
      preparePublish();
      show("step-build");
    }, 30);
  }

  function labelFor(list, key) {
    var hit = list.filter(function (x) { return x.key === key; })[0];
    return hit ? hit.label : key;
  }

  function inlineSite(page) {
    var html = built.files[page] || "";
    var sheet = built.files["assets/site.css"] || "";
    var js = built.files["assets/site.js"] || "";
    html = html
      .replace('<link rel="stylesheet" href="assets/site.css">', "<style>" + sheet + "</style>")
      .replace('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">', "")
      .replace('<script src="assets/site.js" defer></script>', "<script>" + js + "<\/script>");
    // A srcdoc frame has no assets folder, so point the logo at its data URI
    // rather than leaving a broken image in the preview.
    if (brief && brief.logo) {
      var uri = brief.logo;
      html = html
        .replace(/src="assets\/logo\.[a-z]+"/g, function () { return 'src="' + uri + '"'; })
        .replace(/<link rel="icon" href="assets\/logo\.[a-z]+"[^>]*>/g, "");
    }
    return html;
  }

  function showSitePreview() {
    $("site-frame").srcdoc = inlineSite("index.html");
  }

  function showCards() {
    var host = $("card-preview");
    host.innerHTML = "";
    var frame = document.createElement("iframe");
    frame.title = "Business card proof";
    frame.srcdoc = built.cards_proof;
    host.appendChild(frame);
  }

  function showTodo() {
    var list = $("todo-list");
    list.innerHTML = "";
    var content = built.files["CONTENT.md"] || "";
    var items = content.split("\n").filter(function (l) { return l.indexOf("- **") === 0; });
    if (!items.length) { list.innerHTML = "<li><span>Nothing outstanding.</span></li>"; }
    items.forEach(function (line) {
      var m = line.match(/^- \*\*(.+?)\*\*\s*[—-]?\s*(.*)$/);
      var li = document.createElement("li");
      li.innerHTML = "<b>" + esc(m ? m[1] : "To do") + "</b><span>" +
                     esc(m ? m[2] : line.slice(2)) + "</span>";
      list.appendChild(li);
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (tab) {
    tab.addEventListener("click", function () {
      Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (t) {
        t.classList.toggle("is-on", t === tab);
      });
      ["pane-site", "pane-cards", "pane-publish", "pane-todo"].forEach(function (p) {
        $(p).hidden = p !== tab.dataset.pane;
      });
      if (tab.dataset.pane === "pane-publish") preparePublish();
    });
  });

  /* ---------------- output ---------------- */

  $("open-site").addEventListener("click", function () {
    openHtml(inlineSite("index.html"));
  });

  $("print-cards").addEventListener("click", function () {
    var w = openHtml(built.cards_print);
    if (w) setTimeout(function () { try { w.print(); } catch (e) {} }, 700);
  });

  function openHtml(html) {
    var blob = new Blob([html], { type: "text/html" });
    var url = URL.createObjectURL(blob);
    var w = window.open(url, "_blank");
    if (!w) toast("Allow pop-ups to open it in a new tab");
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
    return w;
  }

  $("download-zip").addEventListener("click", function () {
    var files = {};
    Object.keys(built.files).forEach(function (k) { files[built.slug + "/" + k] = built.files[k]; });
    Object.keys(built.binary || {}).forEach(function (k) {
      files[built.slug + "/" + k] = b64ToBytes(built.binary[k]);
    });
    downloadZip(built.slug + "-site.zip", files);
  });

  $("download-cards").addEventListener("click", function () {
    var files = {};
    Object.keys(built.files).forEach(function (k) {
      if (k.indexOf("cards/") === 0) files[k.slice(6)] = built.files[k];
    });
    downloadZip(built.slug + "-cards.zip", files);
  });

  function downloadZip(filename, files) {
    saveBlob(zipBlob(files), filename);
  }

  /* Minimal store-only ZIP writer. No compression, no dependency — the payload is
     text and a few hundred KB at most. */
  function zipBlob(files) {
    var enc = new TextEncoder();
    var names = Object.keys(files).sort();
    var chunks = [], central = [], offset = 0;

    names.forEach(function (name) {
      var nameBytes = enc.encode(name);
      var value = files[name];
      var data = (value instanceof Uint8Array) ? value : enc.encode(value);
      var crc = crc32(data);
      var local = new Uint8Array(30 + nameBytes.length);
      var dv = new DataView(local.buffer);
      dv.setUint32(0, 0x04034b50, true);
      dv.setUint16(4, 20, true);
      dv.setUint16(6, 0x0800, true);      // UTF-8 names
      dv.setUint16(8, 0, true);           // stored
      dv.setUint32(14, crc, true);
      dv.setUint32(18, data.length, true);
      dv.setUint32(22, data.length, true);
      dv.setUint16(26, nameBytes.length, true);
      local.set(nameBytes, 30);
      chunks.push(local, data);

      var cen = new Uint8Array(46 + nameBytes.length);
      var cv = new DataView(cen.buffer);
      cv.setUint32(0, 0x02014b50, true);
      cv.setUint16(4, 20, true);
      cv.setUint16(6, 20, true);
      cv.setUint16(8, 0x0800, true);
      cv.setUint16(10, 0, true);
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, nameBytes.length, true);
      cv.setUint32(42, offset, true);
      cen.set(nameBytes, 46);
      central.push(cen);
      offset += local.length + data.length;
    });

    var centralSize = central.reduce(function (n, c) { return n + c.length; }, 0);
    var end = new Uint8Array(22);
    var ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(8, names.length, true);
    ev.setUint16(10, names.length, true);
    ev.setUint32(12, centralSize, true);
    ev.setUint32(16, offset, true);

    return new Blob(chunks.concat(central, [end]), { type: "application/zip" });
  }

  var CRC_TABLE = (function () {
    var t = new Uint32Array(256);
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(bytes) {
    var c = 0xFFFFFFFF;
    for (var i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }

  function saveBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
    toast("Saved " + filename);
  }

  /* ---------------- publishing ---------------- */

  function ghCreds() {
    try { return JSON.parse(localStorage.getItem(GH_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function ghSave(patch) {
    var cur = ghCreds();
    Object.keys(patch).forEach(function (k) { cur[k] = patch[k]; });
    try { localStorage.setItem(GH_KEY, JSON.stringify(cur)); } catch (e) {}
  }

  function preparePublish() {
    var creds = ghCreds();
    if (creds.token) {
      $("gh-token").value = creds.token;
      $("gh-forget").hidden = false;
    }
    $("gh-repo").value = ($("gh-repo").value || (built ? built.slug : "")) || "";
    var entry = currentEntry();
    if (entry && entry.live) {
      $("live-box").hidden = false;
      $("live-url").textContent = entry.live;
      $("live-url").href = entry.live;
    } else {
      $("live-box").hidden = true;
    }
  }

  $("gh-forget").addEventListener("click", function () {
    localStorage.removeItem(GH_KEY);
    $("gh-token").value = "";
    $("gh-forget").hidden = true;
    toast("Token removed from this phone");
  });

  function logLine(text, state) {
    var log = $("gh-log");
    log.hidden = false;
    var li = document.createElement("li");
    li.textContent = text;
    if (state) li.className = "log--" + state;
    log.appendChild(li);
    li.scrollIntoView({ block: "nearest" });
    return li;
  }

  async function gh(token, method, path, body) {
    var res = await fetch("https://api.github.com" + path, {
      method: method,
      headers: {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
      },
      body: body ? JSON.stringify(body) : undefined
    });
    var text = await res.text();
    var data = text ? JSON.parse(text) : null;
    if (!res.ok) {
      var err = new Error((data && data.message) || (res.status + " " + res.statusText));
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  $("gh-publish").addEventListener("click", async function () {
    var token = $("gh-token").value.trim();
    var repo = slugify($("gh-repo").value.trim() || (built && built.slug) || "site");
    var isPrivate = $("gh-private").checked;
    if (!token) { toast("Paste a token first"); $("gh-token").focus(); return; }
    if (!built) { toast("Build the site first"); return; }

    $("gh-log").innerHTML = "";
    $("gh-publish").disabled = true;
    try {
      logLine("Checking the token…");
      var me = await gh(token, "GET", "/user");
      var owner = me.login;
      logLine("Signed in as " + owner, "ok");
      ghSave({ token: token, owner: owner });
      $("gh-forget").hidden = false;

      var exists = true;
      try { await gh(token, "GET", "/repos/" + owner + "/" + repo); }
      catch (e) { if (e.status === 404) exists = false; else throw e; }

      if (!exists) {
        logLine("Creating " + owner + "/" + repo + "…");
        await gh(token, "POST", "/user/repos", {
          name: repo, private: isPrivate, auto_init: false,
          description: (built.name || "Website") + " — built with sitesmith"
        });
        logLine("Repository created", "ok");
      } else {
        logLine("Using the existing " + owner + "/" + repo, "ok");
      }

      // Git Data API: one commit containing every file, so a republish is atomic
      // and never leaves half the site updated.
      logLine("Uploading " + Object.keys(built.files).length + " files…");
      var tree = [];
      for (var path in built.files) {
        var blob = await gh(token, "POST", "/repos/" + owner + "/" + repo + "/git/blobs",
                            { content: built.files[path], encoding: "utf-8" });
        tree.push({ path: path, mode: "100644", type: "blob", sha: blob.sha });
      }
      for (var bpath in (built.binary || {})) {
        var bblob = await gh(token, "POST", "/repos/" + owner + "/" + repo + "/git/blobs",
                             { content: built.binary[bpath], encoding: "base64" });
        tree.push({ path: bpath, mode: "100644", type: "blob", sha: bblob.sha });
      }

      var parents = [];
      var baseTree;
      try {
        var ref = await gh(token, "GET", "/repos/" + owner + "/" + repo + "/git/ref/heads/main");
        parents = [ref.object.sha];
        var head = await gh(token, "GET", "/repos/" + owner + "/" + repo + "/git/commits/" + ref.object.sha);
        baseTree = head.tree.sha;
      } catch (e) { if (e.status !== 404 && e.status !== 409) throw e; }

      var newTree = await gh(token, "POST", "/repos/" + owner + "/" + repo + "/git/trees",
                             baseTree ? { base_tree: baseTree, tree: tree } : { tree: tree });
      var commit = await gh(token, "POST", "/repos/" + owner + "/" + repo + "/git/commits", {
        message: (parents.length ? "Update " : "Publish ") + (built.name || repo) +
                 " — sitesmith", tree: newTree.sha, parents: parents
      });

      if (parents.length) {
        await gh(token, "PATCH", "/repos/" + owner + "/" + repo + "/git/refs/heads/main",
                 { sha: commit.sha, force: true });
      } else {
        await gh(token, "POST", "/repos/" + owner + "/" + repo + "/git/refs",
                 { ref: "refs/heads/main", sha: commit.sha });
      }
      logLine("Committed", "ok");

      logLine("Turning on Pages…");
      var pagesUrl = null;
      try {
        var pages = await gh(token, "POST", "/repos/" + owner + "/" + repo + "/pages",
                             { source: { branch: "main", path: "/" } });
        pagesUrl = pages.html_url;
      } catch (e) {
        if (e.status === 409) {
          var existing = await gh(token, "GET", "/repos/" + owner + "/" + repo + "/pages");
          pagesUrl = existing.html_url;
          logLine("Pages was already on", "ok");
        } else if (e.status === 403 && isPrivate) {
          logLine("Pages refused: a private repo needs a paid plan. The code is " +
                  "pushed — make the repo public, or publish another way.", "warn");
        } else { throw e; }
      }

      if (pagesUrl) {
        logLine("Live at " + pagesUrl, "ok");
        logLine("First build takes a minute or two before the link works.", "warn");
        var entry = currentEntry();
        if (entry) { entry.live = pagesUrl; entry.repo = owner + "/" + repo; persist(); renderSites(); }
        $("live-box").hidden = false;
        $("live-url").textContent = pagesUrl;
        $("live-url").href = pagesUrl;
      }
      ghSave({ repo: repo });
      toast("Published");
    } catch (err) {
      console.error(err);
      var msg = err.message || String(err);
      if (err.status === 401) msg = "That token was rejected. Check it has the repo scope and has not expired.";
      if (err.status === 403 && /rate limit/i.test(msg)) msg = "GitHub rate limit hit — wait a minute and try again.";
      logLine("Failed: " + msg, "err");
      toast("Publish failed");
    } finally {
      $("gh-publish").disabled = false;
    }
  });

  $("find-published").addEventListener("click", async function () {
    var creds = ghCreds();
    if (!creds.token) { toast("Publish to GitHub once first, then this can list them"); return; }
    try {
      toast("Looking…");
      var repos = await gh(creds.token, "GET", "/user/repos?per_page=100&sort=updated");
      var found = 0;
      for (var i = 0; i < repos.length; i++) {
        var r = repos[i];
        if (!r.has_pages) continue;
        var already = library.filter(function (s) { return s.repo === r.full_name; })[0];
        var url = "https://" + r.owner.login + ".github.io/" + r.name + "/";
        if (already) { already.live = url; found++; continue; }
        if (!/sitesmith/i.test(r.description || "")) continue;
        library.push({ id: newId(), name: r.name, brief: { name: r.name },
                       picked: { layout: "classic", theme: "slate" },
                       updated: new Date(r.updated_at).getTime(), live: url,
                       repo: r.full_name, remoteOnly: true });
        found++;
      }
      persist(); renderSites();
      toast(found ? "Matched " + found + " published site" + (found === 1 ? "" : "s")
                  : "No published sites found");
    } catch (e) {
      toast("Could not reach GitHub");
    }
  });

  function siteZipFiles() {
    var files = {};
    Object.keys(built.files).forEach(function (k) { files[k] = built.files[k]; });
    Object.keys(built.binary || {}).forEach(function (k) {
      files[k] = b64ToBytes(built.binary[k]);
    });
    return files;
  }

  function b64ToBytes(b64) {
    var bin = atob(b64);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function siteZipBlob() {
    return zipBlob(siteZipFiles());
  }

  ["netlify-zip", "cf-zip", "plain-zip"].forEach(function (id) {
    $(id).addEventListener("click", function () {
      saveBlob(siteZipBlob(), built.slug + "-site.zip");
    });
  });

  $("share-zip").addEventListener("click", async function () {
    var blob = siteZipBlob();
    var file = new File([blob], built.slug + "-site.zip", { type: "application/zip" });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try { await navigator.share({ files: [file], title: built.name }); return; }
      catch (e) { if (e.name === "AbortError") return; }
    }
    saveBlob(blob, built.slug + "-site.zip");
  });

  $("copy-live").addEventListener("click", function () {
    navigator.clipboard.writeText($("live-url").textContent).then(function () {
      toast("Link copied");
    });
  });

  $("share-live").addEventListener("click", async function () {
    var url = $("live-url").textContent;
    if (navigator.share) {
      try { await navigator.share({ title: built ? built.name : "My site", url: url }); return; }
      catch (e) { if (e.name === "AbortError") return; }
    }
    navigator.clipboard.writeText(url).then(function () { toast("Link copied"); });
  });

  /* ---------------- menu ---------------- */

  $("menu-btn").addEventListener("click", function () {
    $("menu-meta").textContent = "Generator " + (window.SITESMITH_VERSION || "—") +
      " · " + CAT.layouts.length + " layouts, " + CAT.themes.length + " themes";
    $("menu-sheet").hidden = false;
  });
  $("menu-close").addEventListener("click", closeMenu);
  $("menu-sheet").addEventListener("click", function (e) {
    if (e.target === $("menu-sheet")) closeMenu();
  });
  function closeMenu() { $("menu-sheet").hidden = true; }

  $("menu-sites").addEventListener("click", function () {
    closeMenu();
    if (!$("step-brief").hidden) save();
    renderSites();
    show("step-sites");
  });
  $("menu-edit").addEventListener("click", function () { closeMenu(); show("step-brief"); });
  $("menu-gallery").addEventListener("click", function () {
    closeMenu(); save(); show("step-gallery"); renderGallery();
  });
  $("menu-export").addEventListener("click", function () {
    closeMenu(); save();
    var name = (brief.name || "brief").toLowerCase().replace(/[^a-z0-9]+/g, "-");
    saveBlob(new Blob([JSON.stringify(brief, null, 2)], { type: "application/json" }),
             name + "-brief.json");
  });
  $("menu-import").addEventListener("click", function () { closeMenu(); $("import-file").click(); });
  $("import-file").addEventListener("change", function (e) {
    var file = e.target.files[0];
    if (!file) return;
    file.text().then(function (text) {
      try {
        brief = JSON.parse(text);
        fillForm(brief);
        syncPriceRows();
        (brief.services || []).forEach(function (s) {
          if (!s || !s.title) return;
          var row = $("price-rows").querySelector('[data-name="' + cssEscape(s.title) + '"]');
          if (row) row.querySelector("input").value = s.price || "";
        });
        save();
        show("step-brief");
        toast("Brief loaded");
      } catch (err) { toast("That file is not a sitesmith brief"); }
    });
    e.target.value = "";
  });
  $("menu-reset").addEventListener("click", function () {
    closeMenu();
    var entry = currentEntry();
    if (!entry) { newSite(); return; }
    if (!confirm("Delete " + (entry.name || "this site") + "? This cannot be undone.")) return;
    library = library.filter(function (s) { return s.id !== entry.id; });
    currentId = null; built = null;
    persist(); renderSites();
    show("step-sites");
    toast("Deleted");
  });

  /* ---------------- odds and ends ---------------- */

  var toastTimer = null;
  function toast(text) {
    var el = $("toast");
    el.textContent = text;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.hidden = true; }, 2200);
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  $("brief-form").addEventListener("input", function () {
    clearTimeout($("brief-form").dataset.t);
    $("brief-form").dataset.t = setTimeout(save, 400);
  });
  $("brief-form").addEventListener("submit", function (e) { e.preventDefault(); });

  fetch("py/version.json").then(function (r) { return r.json(); })
    .then(function (v) { window.SITESMITH_VERSION = v.generator; })
    .catch(function () {});

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      // updateViaCache:"none" stops the browser serving a stale sw.js, which would
      // pin the phone to an old generator forever.
      navigator.serviceWorker.register("sw.js", { updateViaCache: "none" })
        .then(function (reg) { reg.update(); })
        .catch(function (e) { console.warn(e); });

      // A new worker taking over mid-session means the page is running one version
      // and the cache holds another. Reload once so they agree.
      var refreshing = false;
      navigator.serviceWorker.addEventListener("controllerchange", function () {
        if (refreshing) return;
        refreshing = true;
        location.reload();
      });
    });
  }

  boot();
})();
