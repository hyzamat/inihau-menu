/* Eastern Special Inihaw menu — renders from window.MENU (menu-data.js). Vanilla JS, no dependencies. */
(function () {
  "use strict";

  var M = window.MENU;
  var CUR = M.restaurant.currency || "SR";
  var IMG = "assets/img/menu/";
  var doc = document;
  var root = doc.documentElement;
  var $ = function (id) { return doc.getElementById(id); };

  var menuEl = $("menu"), chipsEl = $("chips"), barEl = $("bar"), q = $("q"), emptyEl = $("empty");
  var sheet = $("sheet"), sheetPanel = $("sheetPanel"), sheetBody = $("sheetBody");

  // id -> { item, cat } lookup (combos included)
  var byId = Object.create(null);

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9#& ]+/g, " ");
  }
  function img(slug, sizes, opts) {
    opts = opts || {};
    var b = IMG + slug;
    return '<img src="' + b + '-360.webp" srcset="' + b + "-360.webp 360w, " + b + "-540.webp 540w, " + b +
      '-720.webp 720w" sizes="' + sizes + '" width="' + (opts.w || 360) + '" height="' + (opts.h || 360) + '" alt="' + esc(opts.alt || "") + '"' +
      (opts.eager ? ' fetchpriority="' + (opts.high ? "high" : "auto") + '"' : ' loading="lazy"') + ' decoding="async">';
  }
  function priceHTML(it) {
    if (it.prices) {
      return it.prices.map(function (p) { return p.price; }).join(" / ") + " <small>" + CUR + "</small>";
    }
    return it.price + " <small>" + CUR + "</small>";
  }
  function calText(it) { return it.cal != null && it.cal !== "" ? it.cal + " kcal" : ""; }

  var PEOPLE = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M16 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-8 0a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm0 2c-2.7 0-8 1.3-8 4v3h16v-3c0-2.7-5.3-4-8-4zm8 0c-.3 0-.7 0-1.1.1 1.3.9 2.1 2.2 2.1 3.9v3h7v-3c0-2.7-5.3-4-8-4z"/></svg>';
  var CARD_SIZES ="(min-width: 1100px) 260px, (min-width: 900px) 23vw, (min-width: 640px) 31vw, 47vw";
  var LIST_SIZES = "104px";

  /* ---------- render ---------- */
  function render() {
    var html = [], chips = [];

    // Combos (each one has its own price, size and included items)
    var minPrice = Math.min.apply(null, M.combos.map(function (c) { return c.price; }));
    chips.push('<button class="chip" type="button" data-target="combos">Family Combos</button>');
    html.push(
      '<section class="sec sec--combo" id="combos" data-sec>' +
        '<div class="sec__head"><div><h2 class="sec__title">Family Combos</h2>' +
        '<p class="sec__en">Sharing feasts for family &amp; friends</p></div>' +
        '<span class="sec__count">from ' + minPrice + " " + CUR + "</span></div>" +
        '<div class="free"><span class="free__badge">INCLUDED</span><p>Every combo comes with <strong>rice, buko pandan, Pepsi, water, fruits, kropek &amp; free sabaw</strong></p></div>' +
        '<div class="combos">' +
        M.combos.map(function (c, i) {
          byId[c.id] = { item: c, combo: true };
          return '<a class="combo" href="#' + c.id + '" data-id="' + c.id + '" data-s="' +
            esc(norm(c.name + " combo family group " + c.serves + " " + c.dishes.map(function (d) { return d.n; }).join(" "))) + '">' +
            '<div class="ph">' + img(c.img, "(min-width: 900px) 340px, 84vw", { eager: i < 2, high: i === 0, w: 360, h: 270 }) +
            '<span class="combo__price">' + c.price + " " + CUR + "</span>" +
            '<span class="combo__serves">' + PEOPLE + esc(c.serves) + "</span></div>" +
            '<div class="combo__body"><h3 class="combo__name">' + esc(c.name) + "</h3>" +
            '<ul class="combo__dishes">' + c.dishes.map(function (d) {
              return "<li><span>" + esc(d.n) + "</span><em>" + esc(d.q) + "</em></li>";
            }).join("") + "</ul>" +
            '<p class="combo__more"><b>+ Included:</b> ' + esc(c.free.join(", ")) + " · " + c.cal + " kcal</p></div></a>";
        }).join("") +
        "</div><p class=\"swipe-hint\">Swipe for more combos →</p></section>"
    );

    // Categories
    M.categories.forEach(function (cat) {
      chips.push('<button class="chip" type="button" data-target="' + cat.id + '">' + esc(cat.name) + "</button>");
      html.push(
        '<section class="sec" id="' + cat.id + '" data-sec>' +
          '<div class="sec__head"><div><h2 class="sec__title">' + esc(cat.name) + "</h2>" +
          '<p class="sec__en">' + esc(cat.en) + "</p></div>" +
          '<span class="sec__count">' + cat.items.length + "</span></div>" +
          '<div class="items">' +
          cat.items.map(function (it) {
            byId[it.id] = { item: it, cat: cat };
            var cal = calText(it);
            return '<a class="card" href="#' + it.id + '" data-id="' + it.id + '" data-s="' +
              esc(norm(it.name + " " + it.desc + " " + cat.name + " " + cat.en)) + '">' +
              (it.tag ? '<span class="tag">★ ' + esc(it.tag) + "</span>" : "") +
              '<div class="ph">' + img(it.img, CARD_SIZES) + "</div>" +
              '<div class="card__body"><h3 class="card__name">' + esc(it.name) + "</h3>" +
              '<p class="card__desc">' + esc(it.desc) + "</p>" +
              '<div class="card__meta"><span class="price">' + priceHTML(it) + "</span>" +
              (cal ? '<span class="cal">' + cal + "</span>" : "") + "</div></div></a>";
          }).join("") +
          "</div></section>"
      );
    });

    menuEl.innerHTML = html.join("");
    chipsEl.innerHTML = chips.join("");

    // Highlights (featured on the printed cover)
    var hl = ["pineapple-juice", "iced-tea", "halo-halo", "bubble-tea"];
    $("highlights").innerHTML = hl.map(function (id, i) {
      var it = byId[id] && byId[id].item;
      if (!it) return "";
      var p = it.prices ? it.prices.map(function (x) { return x.label + " " + x.price; }).join(" · ") + " " + CUR : it.price + " " + CUR;
      return '<a class="hl" href="#' + id + '" data-id="' + id + '">' + img(it.img, "170px", { eager: true }) +
        '<span class="hl__t">' + esc(it.name) + '<span class="hl__p">' + esc(p) + "</span></span></a>";
    }).join("");
  }

  /* ---------- sticky bar height -> CSS var ---------- */
  function syncBar() { root.style.setProperty("--bar-h", barEl.offsetHeight + "px"); }

  /* ---------- category chips + scrollspy ---------- */
  var chipEls = [], activeId = null, spyLock = 0;
  function setActive(id, instant) {
    if (id === activeId) return;
    activeId = id;
    for (var i = 0; i < chipEls.length; i++) {
      var c = chipEls[i], on = c.getAttribute("data-target") === id;
      c.classList.toggle("is-active", on);
      if (on) {
        var left = Math.max(0, c.offsetLeft - (chipsEl.clientWidth - c.offsetWidth) / 2);
        // two smooth scrolls at once cancel each other in Chrome, so jump when the page is scrolling
        if (instant) chipsEl.scrollLeft = left;
        else chipsEl.scrollTo({ left: left, behavior: "smooth" });
      }
    }
  }
  function goTo(sec) {
    var y = sec.getBoundingClientRect().top + window.scrollY - barEl.offsetHeight + 1;
    window.scrollTo({ top: y, behavior: "smooth" });
  }
  function initSpy() {
    chipEls = [].slice.call(chipsEl.querySelectorAll(".chip"));
    chipsEl.addEventListener("click", function (e) {
      var c = e.target.closest(".chip");
      if (!c) return;
      var sec = $(c.getAttribute("data-target"));
      if (!sec) return;
      spyLock = Date.now() + 1200;
      setActive(sec.id, true);
      goTo(sec);
    });
    if (!("IntersectionObserver" in window)) return;
    var visible = Object.create(null);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
      if (Date.now() < spyLock) return;
      // the last section that has entered the band just under the sticky bar wins
      var secs = menuEl.querySelectorAll("[data-sec]:not([hidden])");
      for (var i = secs.length - 1; i >= 0; i--) {
        if (visible[secs[i].id]) { setActive(secs[i].id); return; }
      }
    }, { rootMargin: "-" + (barEl.offsetHeight + 8) + "px 0px -62% 0px" });
    menuEl.querySelectorAll("[data-sec]").forEach(function (s) { io.observe(s); });
  }

  /* ---------- search ---------- */
  function initSearch() {
    var cards = [].slice.call(menuEl.querySelectorAll("[data-s]"));
    var secs = [].slice.call(menuEl.querySelectorAll("[data-sec]"));
    function run() {
      var terms = norm(q.value).trim().split(/\s+/).filter(Boolean);
      var any = false;
      cards.forEach(function (c) {
        var s = c.getAttribute("data-s");
        var ok = terms.every(function (t) { return s.indexOf(t) !== -1; });
        c.hidden = !ok;
      });
      secs.forEach(function (sec) {
        var has = !!sec.querySelector("[data-s]:not([hidden])");
        sec.hidden = !has;
        any = any || has;
      });
      emptyEl.hidden = any;
      chipEls.forEach(function (c) {
        var sec = $(c.getAttribute("data-target"));
        c.hidden = !!(sec && sec.hidden);
      });
    }
    // pin the search bar to the top so results are visible above the keyboard
    function pin() {
      var y = menuEl.offsetTop - barEl.offsetHeight;
      if (Math.abs(window.scrollY - y) > 2) window.scrollTo(0, y);
    }
    q.addEventListener("focus", pin);
    q.addEventListener("input", function () {
      run();
      pin();
    });
    q.addEventListener("keydown", function (e) { if (e.key === "Enter") q.blur(); });
  }

  /* ---------- grid / list toggle ---------- */
  function initView() {
    var btn = $("viewToggle");
    var key = "ei-view";
    function apply(list) {
      root.classList.toggle("list-view", list);
      btn.setAttribute("aria-label", list ? "Switch to grid view" : "Switch to list view");
      var sizes = list ? LIST_SIZES : CARD_SIZES;
      menuEl.querySelectorAll(".card img").forEach(function (im) { im.sizes = sizes; });
    }
    var saved = null;
    try { saved = localStorage.getItem(key); } catch (e) {}
    if (saved === "list") apply(true);
    btn.addEventListener("click", function () {
      var list = !root.classList.contains("list-view");
      apply(list);
      try { localStorage.setItem(key, list ? "list" : "grid"); } catch (e) {}
    });
  }

  /* ---------- detail sheet ---------- */
  function sheetHTML(id) {
    var ref = byId[id];
    var it = ref.item;
    var call = '<a class="btn btn--call" href="tel:' + M.restaurant.phone + '">Call to order</a>';
    var share = (navigator.share ? '<button class="btn btn--ghost" type="button" data-share>Share</button>' : "");
    if (ref.combo) {
      return '<div class="sh__img wide">' + img(it.img, "(min-width: 600px) 560px, 100vw", { eager: true, alt: it.name, w: 360, h: 270 }) + "</div>" +
        '<div class="sh__body"><p class="sh__cat">Family Combo</p><h2 class="sh__name" id="sheetTitle">' + esc(it.name) + "</h2>" +
        '<div class="sh__row"><span class="sh__price">' + it.price + " <small>" + CUR + "</small></span>" +
        '<span class="sh__serves">' + PEOPLE + esc(it.serves) + "</span>" +
        '<span class="sh__cal">' + it.cal + " kcal</span></div>" +
        '<p class="sh__h">Main dishes</p><ul class="sh__list">' +
        it.dishes.map(function (d) { return "<li>" + esc(d.n) + '<span class="qty">' + esc(d.q) + "</span></li>"; }).join("") + "</ul>" +
        '<p class="sh__h">Also included</p><div class="freebies">' +
        it.free.map(function (f) { return "<span>" + esc(f) + "</span>"; }).join("") + "</div>" +
        '<div class="sh__actions">' + call + share + "</div></div>";
    }
    var cal = calText(it);
    var price = it.prices
      ? '<div class="sizes">' + it.prices.map(function (p) {
          return '<div class="size"><span>' + esc(p.label) + '</span><span class="price">' + p.price + " <small>" + CUR + "</small></span></div>";
        }).join("") + "</div>" + (cal ? '<div class="sh__row"><span class="sh__cal">' + cal + "</span></div>" : "")
      : '<div class="sh__row"><span class="sh__price">' + it.price + " <small>" + CUR + "</small></span>" +
        (cal ? '<span class="sh__cal">' + cal + "</span>" : "") + "</div>";
    return '<div class="sh__img">' + img(it.img, "(min-width: 600px) 560px, 100vw", { eager: true, alt: it.name }) + "</div>" +
      '<div class="sh__body"><p class="sh__cat">' + esc(ref.cat.name) + "</p>" +
      '<h2 class="sh__name" id="sheetTitle">' + esc(it.name) + "</h2>" +
      '<p class="sh__desc">' + esc(it.desc) + "</p>" + price +
      '<div class="sh__actions">' + call + share + "</div></div>";
  }

  var openId = null;
  function showSheet(id) {
    if (!byId[id]) return false;
    openId = id;
    sheetBody.innerHTML = sheetHTML(id);
    sheetPanel.scrollTop = 0;
    sheetPanel.style.transform = "";
    sheet.classList.remove("closing");
    if (!sheet.open) {
      if (sheet.showModal) sheet.showModal(); else sheet.setAttribute("open", "");
      root.classList.add("lock");
    }
    return true;
  }
  function hideSheetUI() {
    if (!sheet.open) return;
    openId = null;
    sheet.classList.add("closing");
    setTimeout(function () {
      sheet.classList.remove("closing");
      if (sheet.close) sheet.close(); else sheet.removeAttribute("open");
      root.classList.remove("lock");
      sheetPanel.style.transform = "";
    }, 200);
  }
  function openItem(id) {
    if (showSheet(id)) history.pushState({ sheet: id }, "", "#" + id);
  }
  function closeSheet() {
    if (history.state && history.state.sheet) history.back(); // popstate hides it
    else { hideSheetUI(); history.replaceState(null, "", location.pathname + location.search); }
  }

  function initSheet() {
    doc.addEventListener("click", function (e) {
      var a = e.target.closest("a[data-id]");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      openItem(a.getAttribute("data-id"));
    });
    $("sheetClose").addEventListener("click", closeSheet);
    sheet.addEventListener("click", function (e) { if (e.target === sheet) closeSheet(); });
    sheet.addEventListener("cancel", function (e) { e.preventDefault(); closeSheet(); });
    sheetBody.addEventListener("click", function (e) {
      if (!e.target.closest("[data-share]") || !openId) return;
      var it = byId[openId].item;
      navigator.share({ title: it.name + " — " + M.restaurant.name, url: location.origin + location.pathname + "#" + openId }).catch(function () {});
    });
    window.addEventListener("popstate", function (e) {
      var id = e.state && e.state.sheet;
      if (id) showSheet(id); else hideSheetUI();
    });

    // swipe down to close (when scrolled to top)
    var y0 = null, dy = 0;
    sheetPanel.addEventListener("touchstart", function (e) {
      if (sheetPanel.scrollTop > 0) { y0 = null; return; }
      y0 = e.touches[0].clientY; dy = 0;
      sheetPanel.style.transition = "none";
    }, { passive: true });
    sheetPanel.addEventListener("touchmove", function (e) {
      if (y0 === null) return;
      dy = e.touches[0].clientY - y0;
      if (dy > 0) sheetPanel.style.transform = "translateY(" + dy + "px)";
    }, { passive: true });
    sheetPanel.addEventListener("touchend", function () {
      if (y0 === null) return;
      y0 = null;
      sheetPanel.style.transition = "transform .2s ease";
      if (dy > 110) { sheetPanel.style.transform = "translateY(100%)"; closeSheet(); }
      else sheetPanel.style.transform = "";
    });

    // deep link: /#bulalo opens that dish (Back returns to the menu)
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && byId[h]) {
      history.replaceState(null, "", location.pathname + location.search);
      openItem(h);
    }
  }

  /* ---------- boot ---------- */
  render();
  syncBar();
  initSpy();
  initSearch();
  initView();
  initSheet();
  window.addEventListener("resize", syncBar, { passive: true });

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register("sw.js").catch(function () {}); });
  }
})();
