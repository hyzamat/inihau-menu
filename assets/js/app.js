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
  var wa = $("wa"), waPanel = $("waPanel"), waBody = $("waBody");
  var WA_ICON = '<svg aria-hidden="true" viewBox="0 0 24 24"><use href="#i-wa"/></svg>';

  // id -> { item, cat } lookup (combos included)
  var byId = Object.create(null);
  // add-ons offered in the order popup: [{ id, s: size index or -1 }] (menu-data.js -> extras)
  var EXTRAS = [];

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

  // "+" on the corner of every photo: one tap adds the dish, then it becomes  − 2 +
  function quickAdd(it) {
    return '<div class="card__ov"><div class="qa' + (it.prices ? " qa--sized" : "") + '" data-qa="' + it.id + '">' +
      '<button class="qa__b qa__minus" type="button" data-qd="-1" aria-label="One less ' + esc(it.name) + '">&minus;</button>' +
      '<span class="qa__n" aria-hidden="true"></span>' +
      '<button class="qa__b qa__plus" type="button" data-qd="1" aria-label="Add ' + esc(it.name) + ' to your order">+</button>' +
      "</div></div>";
  }

  var PEOPLE = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M16 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-8 0a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm0 2c-2.7 0-8 1.3-8 4v3h16v-3c0-2.7-5.3-4-8-4zm8 0c-.3 0-.7 0-1.1.1 1.3.9 2.1 2.2 2.1 3.9v3h7v-3c0-2.7-5.3-4-8-4z"/></svg>';
  var CARD_SIZES = "(min-width: 1100px) 260px, (min-width: 900px) 23vw, (min-width: 640px) 31vw, 47vw";
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
          return '<article class="combo" data-s="' +
            esc(norm(c.name + " combo family group " + c.serves + " " + c.dishes.map(function (d) { return d.n; }).join(" "))) + '">' +
            '<a class="combo__link" href="#' + c.id + '" data-id="' + c.id + '">' +
            '<div class="ph">' + img(c.img, "(min-width: 900px) 340px, 84vw", { eager: i < 2, high: i === 0, w: 360, h: 270 }) +
            '<span class="combo__price">' + c.price + " " + CUR + "</span>" +
            '<span class="combo__serves">' + PEOPLE + esc(c.serves) + "</span></div>" +
            '<div class="combo__body"><h3 class="combo__name">' + esc(c.name) + "</h3>" +
            '<ul class="combo__dishes">' + c.dishes.map(function (d) {
              return "<li><span>" + esc(d.n) + "</span><em>" + esc(d.q) + "</em></li>";
            }).join("") + "</ul>" +
            '<p class="combo__more"><b>+ Included:</b> ' + esc(c.free.join(", ")) + " · " + c.cal + " kcal</p></div></a>" +
            quickAdd(c) + "</article>";
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
            return '<article class="card" data-s="' + esc(norm(it.name + " " + it.desc + " " + cat.name + " " + cat.en)) + '">' +
              '<a class="card__link" href="#' + it.id + '" data-id="' + it.id + '">' +
              (it.tag ? '<span class="tag">★ ' + esc(it.tag) + "</span>" : "") +
              '<div class="ph">' + img(it.img, CARD_SIZES) + "</div>" +
              '<div class="card__body"><h3 class="card__name">' + esc(it.name) + "</h3>" +
              '<p class="card__desc">' + esc(it.desc) + "</p>" +
              '<div class="card__meta"><span class="price">' + priceHTML(it) + "</span>" +
              (cal ? '<span class="cal">' + cal + "</span>" : "") + "</div></div></a>" +
              quickAdd(it) + "</article>";
          }).join("") +
          "</div></section>"
      );
    });

    menuEl.innerHTML = html.join("");
    chipsEl.innerHTML = chips.join("");

    // Extras: either a dish already on the menu (ref) or a priced add-on of its own. No price yet -> hidden.
    (M.extras || []).forEach(function (x) {
      if (x.ref) {
        var r = byId[x.ref];
        if (!r || r.combo) return;
        if (r.item.prices) r.item.prices.forEach(function (p, i) { EXTRAS.push({ id: x.ref, s: i }); });
        else EXTRAS.push({ id: x.ref, s: -1 });
      } else if (x.id && x.name && typeof x.price === "number" && !byId[x.id]) {
        byId[x.id] = { item: x, extra: true };
        EXTRAS.push({ id: x.id, s: -1 });
      }
    });

    // Highlights (featured on the printed cover)
    var hl = ["pineapple-juice", "iced-tea", "halo-halo", "bubble-tea"];
    $("highlights").innerHTML = hl.map(function (id) {
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
  var shQty = 1, shSize = 0;
  function orderRow(price) {
    return '<div class="order"><div class="qty qty--lg">' +
      '<button type="button" data-sq="-1" aria-label="One less">&minus;</button><span id="shQty">1</span>' +
      '<button type="button" data-sq="1" aria-label="One more">+</button></div>' +
      '<button class="btn btn--add" type="button" data-add>Add to order &middot; <span id="shSum">' + price + " " + CUR + "</span></button></div>";
  }
  function sheetHTML(id) {
    var ref = byId[id];
    var it = ref.item;
    var call = '<a class="btn btn--ghost" href="tel:' + M.restaurant.phone + '">Call us</a>';
    var share = (navigator.share ? '<button class="btn btn--ghost" type="button" data-share>Share</button>' : "");
    call = orderRow(it.prices ? it.prices[0].price : it.price) + '<div class="sh__actions">' + call;
    if (ref.combo) {
      return '<div class="sh__img wide">' + img(it.img, "(min-width: 600px) 560px, 100vw", { eager: true, alt: it.name, w: 360, h: 270 }) + "</div>" +
        '<div class="sh__body"><p class="sh__cat">Family Combo</p><h2 class="sh__name" id="sheetTitle">' + esc(it.name) + "</h2>" +
        '<div class="sh__row"><span class="sh__price">' + it.price + " <small>" + CUR + "</small></span>" +
        '<span class="sh__serves">' + PEOPLE + esc(it.serves) + "</span>" +
        '<span class="sh__cal">' + it.cal + " kcal</span></div>" +
        '<p class="sh__h">Main dishes</p><ul class="sh__list">' +
        it.dishes.map(function (d) { return "<li>" + esc(d.n) + '<span class="qtyl">' + esc(d.q) + "</span></li>"; }).join("") + "</ul>" +
        '<p class="sh__h">Also included</p><div class="freebies">' +
        it.free.map(function (f) { return "<span>" + esc(f) + "</span>"; }).join("") + "</div>" +
        call + share + "</div></div>";
    }
    var cal = calText(it);
    var price = it.prices
      ? '<div class="sizes" role="radiogroup" aria-label="Choose size">' + it.prices.map(function (p, i) {
          return '<button class="size" type="button" role="radio" data-size="' + i + '" aria-checked="' + (i === 0) + '">' +
            '<span class="size__l">' + esc(p.label) + '</span><span class="price">' + p.price + " <small>" + CUR + "</small></span></button>";
        }).join("") + "</div>" + (cal ? '<div class="sh__row"><span class="sh__cal">' + cal + "</span></div>" : "")
      : '<div class="sh__row"><span class="sh__price">' + it.price + " <small>" + CUR + "</small></span>" +
        (cal ? '<span class="sh__cal">' + cal + "</span>" : "") + "</div>";
    return '<div class="sh__img">' + img(it.img, "(min-width: 600px) 560px, 100vw", { eager: true, alt: it.name }) + "</div>" +
      '<div class="sh__body"><p class="sh__cat">' + esc(ref.cat.name) + "</p>" +
      '<h2 class="sh__name" id="sheetTitle">' + esc(it.name) + "</h2>" +
      '<p class="sh__desc">' + esc(it.desc) + "</p>" + price +
      call + share + "</div></div>";
  }

  /* dialogs (item sheet + WhatsApp order) share the slide-up animation */
  function dlgShow(d, panel) {
    clearTimeout(d._t);
    d.classList.remove("closing");
    panel.style.transform = "";
    if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute("open", ""); }
    root.classList.add("lock");
  }
  function dlgHide(d, panel) {
    if (!d.open || d.classList.contains("closing")) return;
    d.classList.add("closing");
    d._t = setTimeout(function () {
      d.classList.remove("closing");
      if (d.close) d.close(); else d.removeAttribute("open");
      panel.style.transform = "";
      if (!sheet.open && !wa.open) root.classList.remove("lock");
    }, 200);
  }

  var openId = null;
  function showSheet(id) {
    if (!byId[id] || byId[id].extra) return false;   // extras have no detail page
    openId = id;
    shQty = 1; shSize = 0;
    sheetBody.innerHTML = sheetHTML(id);
    sheetPanel.scrollTop = 0;
    dlgShow(sheet, sheetPanel);
    return true;
  }
  function hideSheetUI() {
    if (!sheet.open) return;
    openId = null;
    dlgHide(sheet, sheetPanel);
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
      if (!openId) return;
      var id = openId, it = byId[id].item, b;
      if (e.target.closest("[data-share]")) {
        navigator.share({ title: it.name + " — " + M.restaurant.name, url: location.origin + location.pathname + "#" + id }).catch(function () {});
      } else if ((b = e.target.closest("[data-size]"))) {
        shSize = +b.getAttribute("data-size");
        sheetBody.querySelectorAll("[data-size]").forEach(function (x) { x.setAttribute("aria-checked", x === b); });
        sheetSum(it);
      } else if ((b = e.target.closest("[data-sq]"))) {
        shQty = Math.max(1, Math.min(99, shQty + +b.getAttribute("data-sq")));
        $("shQty").textContent = shQty;
        sheetSum(it);
      } else if ((b = e.target.closest("[data-add]")) && !b.disabled) {
        addToCart(id, it.prices ? shSize : -1, shQty);
        b.disabled = true;
        b.classList.add("is-done");
        b.innerHTML = "&#10003; Added to your order";
        setTimeout(function () {
          if (sheet.open && openId === id) closeSheet();
          addedTip();
        }, 600);
      }
    });
    window.addEventListener("popstate", function (e) {
      var st = e.state || {};
      if (st.sheet) showSheet(st.sheet); else hideSheetUI();
      if (st.wa) showWa(); else dlgHide(wa, waPanel);
    });

    swipeToClose(sheetPanel, closeSheet);

    // deep links: /#bulalo opens that dish, /#order opens the WhatsApp order (Back returns to the menu)
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && (byId[h] || h === "order")) {
      history.replaceState(null, "", location.pathname + location.search);
      if (h === "order") openWa(); else openItem(h);
    }
  }
  function sheetSum(it) {
    var p = it.prices ? it.prices[shSize].price : it.price;
    $("shSum").textContent = p * shQty + " " + CUR;
  }

  // swipe down to close (when scrolled to the top)
  function swipeToClose(panel, close) {
    var y0 = null, dy = 0;
    panel.addEventListener("touchstart", function (e) {
      if (panel.scrollTop > 0 || e.target.closest("input, textarea, .xts")) { y0 = null; return; }
      y0 = e.touches[0].clientY; dy = 0;
      panel.style.transition = "none";
    }, { passive: true });
    panel.addEventListener("touchmove", function (e) {
      if (y0 === null) return;
      dy = e.touches[0].clientY - y0;
      if (dy > 0) panel.style.transform = "translateY(" + dy + "px)";
    }, { passive: true });
    panel.addEventListener("touchend", function () {
      if (y0 === null) return;
      y0 = null;
      panel.style.transition = "transform .2s ease";
      if (dy > 110) { panel.style.transform = "translateY(100%)"; close(); }
      else panel.style.transform = "";
    });
  }

  /* ---------- order basket + WhatsApp order ---------- */
  var R = M.restaurant;
  var WA_NUM = String(R.whatsapp || "").replace(/\D/g, "");
  var TYPES = R.orderTypes || ["Dine-in", "Pickup", "Delivery"];
  var fab = $("waFab"), fabTxt = $("waFabTxt"), tip = $("waTip"), tipTimer = 0;
  var cart = [];                                   // [{ id, s: size index or -1, n: quantity }]
  // people = party size for Dine-in; table only comes from a table QR (?table=5); loc = map link from "Share my location"
  var info = { type: "", name: "", table: "", people: 2, addr: "", note: "", loc: "" };
  var isDine = function (t) { return /dine/i.test(t); };
  var isDelivery = function (t) { return /deliver/i.test(t); };
  var DLV = R.delivery || {};
  var FEE = typeof DLV.fee === "number" && DLV.fee >= 0 ? DLV.fee : null;      // null -> confirmed on WhatsApp
  var MIN = +DLV.minOrder || 0;
  var locMsg = "";
  function fee() { return isDelivery(info.type) && FEE ? FEE : 0; }
  function belowMin() { return isDelivery(info.type) && MIN > 0 && totals().sum < MIN; }
  function countOf(id, s) {
    for (var i = 0; i < cart.length; i++) if (cart[i].id === id && cart[i].s === s) return cart[i].n;
    return 0;
  }
  function thumb(it, sizes) {
    return it.img ? img(it.img, sizes) : '<span class="wl__ico" aria-hidden="true">' + esc(it.icon || "+") + "</span>";
  }

  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function restore(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }

  function unit(l) {
    var it = byId[l.id].item, p = it.prices && it.prices[l.s];
    return { name: it.name, size: p ? p.label : "", price: p ? p.price : it.price };
  }
  function totals() {
    var n = 0, sum = 0;
    cart.forEach(function (l) { n += l.n; sum += l.n * unit(l).price; });
    return { n: n, sum: sum };
  }
  function saveCart() { store("ei-cart", cart); updateFab(); syncCards(); }
  function updateFab() {
    var t = totals();
    var txt = t.n ? t.n + (t.n > 1 ? " items · " : " item · ") + t.sum + " " + CUR : "";
    fab.classList.toggle("has", t.n > 0);
    fabTxt.innerHTML = t.n ? "<b>View order</b>" + txt : "";
    fab.setAttribute("aria-label", t.n ? "View your order, " + txt + ". Send on WhatsApp" : "Order on WhatsApp");
  }
  // the "+" / "− 2 +" control on every card shows how many of that dish are in the basket
  var qaEls = null;
  function syncCards() {
    if (!qaEls) qaEls = [].slice.call(menuEl.querySelectorAll("[data-qa]"));
    var counts = Object.create(null);
    cart.forEach(function (l) { counts[l.id] = (counts[l.id] || 0) + l.n; });
    qaEls.forEach(function (el) {
      var n = counts[el.getAttribute("data-qa")] || 0;
      if (el._n === n) return;
      el._n = n;
      el.classList.toggle("has", n > 0);
      el.children[1].textContent = n || "";
    });
  }
  function takeOne(id, s) {
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].id === id && cart[i].s === s) {
        if (--cart[i].n <= 0) cart.splice(i, 1);
        saveCart();
        return;
      }
    }
  }
  function addToCart(id, s, n) {
    var l = null;
    for (var i = 0; i < cart.length; i++) if (cart[i].id === id && cart[i].s === s) l = cart[i];
    if (l) l.n = Math.min(99, l.n + n); else cart.push({ id: id, s: s, n: n });
    saveCart();
    fab.classList.remove("bump");
    void fab.offsetWidth;                          // restart the animation
    fab.classList.add("bump");
  }

  function waLink(text) { return "https://wa.me/" + WA_NUM + (text ? "?text=" + encodeURIComponent(text) : ""); }
  function orderText() {
    var out = ["Hi " + R.name + "! 👋 I'd like to order:", ""];
    cart.forEach(function (l) {
      var u = unit(l);
      out.push(l.n + " × " + u.name + (u.size ? " (" + u.size + ")" : "") + " — " + l.n * u.price + " " + CUR);
    });
    var sum = totals().sum, del = isDelivery(info.type);
    out.push("");
    if (del) {
      out.push("Subtotal: " + sum + " " + CUR,
        "Delivery: " + (FEE === null ? "please confirm" : FEE ? FEE + " " + CUR : "FREE"));
    }
    out.push("*Total: " + (sum + fee()) + " " + CUR + (del && FEE === null ? " + delivery" : "") + "*", "", "*Order type:* " + info.type);
    if (isDine(info.type)) {
      out.push("*People:* " + info.people);
      if (info.table.trim()) out.push("*Table:* " + info.table.trim());
    }
    if (del && info.addr.trim()) out.push("*Address:* " + info.addr.trim());
    if (del && info.loc) out.push("*Location:* " + info.loc);
    if (info.name.trim()) out.push("*Name:* " + info.name.trim());
    if (info.note.trim()) out.push("*Note:* " + info.note.trim());
    return out.join("\n");
  }

  function linesHTML() {
    return cart.map(function (l, i) {
      var u = unit(l), it = byId[l.id].item;
      return '<li><div class="wl__img">' + thumb(it, "48px") + "</div>" +
        '<div class="wl__n"><b>' + esc(u.name) + "</b>" + (u.size ? "<span>" + esc(u.size) + "</span>" : "") + "</div>" +
        '<div class="qty"><button type="button" data-i="' + i + '" data-d="-1" aria-label="One less ' + esc(u.name) + '">&minus;</button>' +
        "<span>" + l.n + '</span><button type="button" data-i="' + i + '" data-d="1" aria-label="One more ' + esc(u.name) + '">+</button></div>' +
        '<b class="wl__p">' + l.n * u.price + " <small>" + CUR + "</small></b></li>";
    }).join("");
  }
  // "Add to your order": one tap adds one; the count shows on the tile and the line appears in the list above
  function extrasHTML() {
    return EXTRAS.map(function (x, i) {
      var u = unit(x), n = countOf(x.id, x.s);
      return '<button class="xt' + (n ? " on" : "") + '" type="button" data-x="' + i + '" aria-label="Add ' +
        esc(u.name + (u.size ? " " + u.size : "") + ", " + u.price + " " + CUR) + '">' +
        '<span class="xt__img">' + thumb(byId[x.id].item, "92px") +
        '<i class="' + (n ? "xt__n" : "xt__plus") + '">' + (n || "+") + "</i></span>" +
        "<b>" + esc(u.name) + "</b>" + (u.size ? '<span class="xt__s">' + esc(u.size) + "</span>" : "") +
        '<span class="xt__p">' + u.price + " " + CUR + "</span></button>";
    }).join("");
  }
  function syncExtras() {
    var box = $("waExtras");
    if (!box) return;
    [].forEach.call(box.children, function (b) {
      var x = EXTRAS[+b.getAttribute("data-x")], n = countOf(x.id, x.s), badge = b.querySelector("i");
      b.classList.toggle("on", n > 0);
      badge.className = n ? "xt__n" : "xt__plus";
      badge.textContent = n || "+";
    });
  }
  function sumsHTML() {
    var sum = totals().sum, del = isDelivery(info.type), rows = "";
    if (del) {
      rows = '<div class="wa__row"><span>Subtotal</span><span>' + sum + " " + CUR + "</span></div>" +
        '<div class="wa__row"><span>Delivery</span><span>' +
        (FEE === null ? "confirmed on WhatsApp" : FEE ? FEE + " " + CUR : "FREE") + "</span></div>";
    }
    return rows + '<div class="wa__total"><span>Total</span><b>' + (sum + fee()) + " <small>" + CUR + "</small></b></div>" +
      (belowMin() ? '<p class="wa__min" id="waMin">Minimum order for delivery is ' + MIN + " " + CUR +
        ". Add " + (MIN - sum) + " " + CUR + " more.</p>" : "");
  }
  function locHTML() {
    if (info.loc) {
      return '<span class="loc__ok">&#10003; Location pin added</span>' +
        '<button class="loc__rm" type="button" data-loc-rm>Remove</button>';
    }
    return '<button class="btn btn--ghost loc__btn" type="button" data-loc>&#128205; Share my location</button>' +
      (locMsg ? '<p class="loc__msg">' + esc(locMsg) + "</p>" : "");
  }
  function getLoc(btn) {
    function done(msg) { locMsg = msg; var box = $("waLoc"); if (box) box.innerHTML = locHTML(); }
    if (!navigator.geolocation) { done("Location is not available on this phone. Please type your address."); return; }
    btn.disabled = true;
    btn.textContent = "Getting your location…";
    navigator.geolocation.getCurrentPosition(function (p) {
      info.loc = "https://maps.google.com/?q=" + p.coords.latitude.toFixed(6) + "," + p.coords.longitude.toFixed(6);
      var a = waBody.querySelector('[data-f="addr"]');
      if (a) a.classList.remove("err");
      done("");
    }, function () {
      done("Couldn't get your location. Type your address, or send your location in WhatsApp after the order.");
    }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 });
  }
  function refresh() {                             // after the basket changes while the popup is open
    $("waLines").innerHTML = linesHTML();
    $("waSums").innerHTML = sumsHTML();
    syncExtras();
  }
  function field(k, label, attrs, show) {
    var v = esc(info[k] || "");
    var tag = /rows=/.test(attrs) ? '<textarea data-f="' + k + '" ' + attrs + ">" + v + "</textarea>"
      : '<input type="text" data-f="' + k + '" value="' + v + '" ' + attrs + ">";
    return '<label class="fld"' + (show ? ' data-show="' + show + '"' : "") + "><span>" + label + "</span>" + tag + "</label>";
  }
  function renderWa() {
    var t = totals();
    if (!t.n) {
      var types = TYPES.length > 1 ? TYPES.slice(0, -1).join(", ") + " or " + TYPES[TYPES.length - 1] : TYPES[0];
      waBody.innerHTML =
        '<div class="bubble">Mabuhay! 👋 Welcome to <b>' + esc(R.name) + "</b>. Ordering takes 3 easy steps:</div>" +
        '<ol class="how">' +
        '<li><b>Tap <i class="how__plus">+</i> on the dishes you want</b><span>Tap again for more. Tap a photo to see the details.</span></li>' +
        "<li><b>Tap the green button</b><span>It shows your dishes and the total price.</span></li>" +
        "<li><b>Send it on WhatsApp</b><span>Choose " + esc(types) + ". We confirm your order in the chat.</span></li></ol>" +
        '<button class="btn btn--add btn--start" type="button" data-wa-start>Start ordering</button>' +
        '<a class="wa__chat" href="' + esc(waLink("Hi " + R.name + "! 👋 I'd like to place an order.")) +
        '" target="_blank" rel="noopener">' + WA_ICON + " Or just chat with us on WhatsApp</a>";
      return;
    }
    waBody.innerHTML =
      '<div class="wa__card"><p class="wa__h">Your order</p><ul class="wl" id="waLines">' + linesHTML() + "</ul>" +
      '<div id="waSums">' + sumsHTML() + "</div></div>" +
      (EXTRAS.length ? '<div class="wa__card"><p class="wa__h">Add to your order</p>' +
        '<div class="xts" id="waExtras">' + extrasHTML() + "</div></div>" : "") +
      '<div class="wa__card"><p class="wa__h">Order type</p><div class="seg" id="waType" role="radiogroup" aria-label="Order type">' +
      TYPES.map(function (ty) {
        return '<button type="button" role="radio" data-type="' + esc(ty) + '" aria-checked="' + (ty === info.type) + '">' + esc(ty) + "</button>";
      }).join("") + "</div>" +
      '<div class="fld ppl" data-show="dine"><span id="waPplL">Number of people</span>' +
      '<div class="qty qty--lg" role="group" aria-labelledby="waPplL">' +
      '<button type="button" data-pp="-1" aria-label="One person less">&minus;</button>' +
      '<span id="waPpl" aria-live="polite">' + info.people + "</span>" +
      '<button type="button" data-pp="1" aria-label="One person more">+</button></div></div>' +
      (DLV.note ? '<p class="dlv__note">' + esc(DLV.note) + "</p>" : "") +
      field("addr", "Delivery address", 'rows="2" autocomplete="street-address" placeholder="Building / villa, street, area"', "delivery") +
      '<div class="loc" id="waLoc">' + locHTML() + "</div>" +
      field("name", "Your name", 'autocomplete="name" placeholder="Optional"') +
      field("note", "Note for the kitchen", 'rows="2" placeholder="Optional, e.g. less spicy"') + "</div>" +
      '<a class="btn btn--wa btn--send" id="waSend" href="' + waLink() + '" target="_blank" rel="noopener">' + WA_ICON + " Send order on WhatsApp</a>" +
      '<p class="wa__fine">WhatsApp opens with your order typed out. Just tap <b>Send</b>.</p>' +
      '<button class="wa__clear" type="button" data-wa-clear>Clear order</button>';
    syncType();
  }
  function syncType() {
    waBody.classList.toggle("t-dine", isDine(info.type));
    waBody.classList.toggle("t-delivery", isDelivery(info.type));
    waBody.querySelectorAll("[data-type]").forEach(function (b) { b.setAttribute("aria-checked", b.getAttribute("data-type") === info.type); });
    var sums = $("waSums");
    if (sums) sums.innerHTML = sumsHTML();         // delivery fee / minimum order depend on the type
  }
  function saveInfo() { store("ei-info", { name: info.name, type: info.type, addr: info.addr }); }

  function showWa() { renderWa(); waPanel.scrollTop = 0; hideTip(); dlgShow(wa, waPanel); }
  function openWa() {
    if (wa.open) return;
    showWa();
    history.pushState({ wa: 1 }, "", "#order");
  }
  function closeWa() {
    if (history.state && history.state.wa) history.back();
    else { dlgHide(wa, waPanel); history.replaceState(null, "", location.pathname + location.search); }
  }

  function showTip(html, ms) {
    $("waTipTxt").innerHTML = html;
    tip.hidden = false;
    clearTimeout(tipTimer);
    tipTimer = setTimeout(hideTip, ms);
  }
  function hideTip() { tip.hidden = true; clearTimeout(tipTimer); }
  function once(key) {
    try { if (sessionStorage.getItem(key)) return false; sessionStorage.setItem(key, "1"); } catch (e) {}
    return true;
  }
  function addedTip() {
    if (!once("ei-tip-added")) return false;
    showTip("<b>Added to your order &#10003;</b>Add more dishes, then tap the green button to send your order.", 6000);
    return true;
  }
  // "Start ordering": go to the dishes and point at the + buttons, so it never feels like just going back
  function startOrdering() {
    closeWa();
    setTimeout(function () {
      var first = menuEl.querySelector("[data-sec]:not([hidden])");
      var move = 0;                                  // how far the page is about to scroll down
      if (first && window.scrollY < menuEl.offsetTop - barEl.offsetHeight - 2) {
        move = first.getBoundingClientRect().top - barEl.offsetHeight;
        goTo(first);
      }
      showTip("<b>Tap + on a dish to add it</b>When you are done, tap the green button to send your order.", 12000);
      // pulse the + buttons that are (or are about to be) on screen
      var seen = 0;
      (qaEls || []).forEach(function (el) {
        if (seen >= 8 || el._n) return;
        var r = el.getBoundingClientRect(), y = r.top - move;
        if (r.width && y > 0 && y < window.innerHeight) { seen++; el.classList.add("pulse"); }
      });
      setTimeout(function () { (qaEls || []).forEach(function (el) { el.classList.remove("pulse"); }); }, 4200);
    }, 280);
  }

  function initOrder() {
    if (!WA_NUM) { root.classList.add("no-wa"); return; }
    (restore("ei-cart") || []).forEach(function (l) {
      var ref = l && byId[l.id];
      if (!ref) return;
      var ok = ref.item.prices ? !!ref.item.prices[l.s] : l.s === -1;
      if (ok && l.n > 0) cart.push({ id: l.id, s: l.s, n: Math.min(99, l.n | 0) });
    });
    var saved = restore("ei-info") || {};
    info.name = saved.name || "";
    info.addr = saved.addr || "";
    // every visit starts on the default order type (Delivery); a link with ?order=pickup can override it
    info.type = TYPES.indexOf(R.defaultOrderType) !== -1 ? R.defaultOrderType : "";
    var tm = /[?&]table=([^&#]+)/.exec(location.search);  // table QR codes: ?table=5
    if (tm) {
      info.table = decodeURIComponent(tm[1]);
      info.type = TYPES.filter(isDine)[0] || info.type;
    }
    var om = /[?&]order=([^&#]+)/.exec(location.search);  // links for home orders: ?order=delivery (or pickup)
    if (om) {
      var want = decodeURIComponent(om[1]).toLowerCase();
      info.type = TYPES.filter(function (ty) { return ty.toLowerCase().indexOf(want) === 0; })[0] || info.type;
    }
    updateFab();
    syncCards();

    doc.addEventListener("click", function (e) {
      var a = e.target.closest("[data-wa-open]");
      if (!a) return;
      e.preventDefault();
      openWa();
    });
    // quick add / remove straight from the menu cards
    menuEl.addEventListener("click", function (e) {
      var b = e.target.closest("[data-qd]");
      if (!b) return;
      var id = b.parentNode.getAttribute("data-qa"), ref = byId[id];
      if (!ref) return;
      if (ref.item.prices) { openItem(id); return; }   // has sizes: pick one in the dish popup
      if (+b.getAttribute("data-qd") > 0) {
        if (countOf(id, -1) < 99) addToCart(id, -1, 1);
        if (!addedTip()) hideTip();                     // the first add explains the green button
      } else takeOne(id, -1);
    });
    $("waClose").addEventListener("click", closeWa);
    wa.addEventListener("click", function (e) { if (e.target === wa) closeWa(); });
    wa.addEventListener("cancel", function (e) { e.preventDefault(); closeWa(); });
    swipeToClose(waPanel, closeWa);

    waBody.addEventListener("click", function (e) {
      var b = e.target.closest("button, a");
      if (!b) return;
      if (b.hasAttribute("data-d")) {
        var l = cart[+b.getAttribute("data-i")];
        if (!l) return;
        l.n = Math.min(99, l.n + +b.getAttribute("data-d"));
        if (l.n <= 0) cart.splice(cart.indexOf(l), 1);
        saveCart();
        if (!cart.length) renderWa();
        else refresh();
      } else if (b.hasAttribute("data-x")) {
        var x = EXTRAS[+b.getAttribute("data-x")];
        if (!x) return;
        addToCart(x.id, x.s, 1);
        refresh();
      } else if (b.hasAttribute("data-pp")) {
        info.people = Math.max(1, Math.min(50, info.people + +b.getAttribute("data-pp")));
        $("waPpl").textContent = info.people;
      } else if (b.hasAttribute("data-loc")) {
        getLoc(b);
      } else if (b.hasAttribute("data-loc-rm")) {
        info.loc = "";
        $("waLoc").innerHTML = locHTML();
      } else if (b.hasAttribute("data-type")) {
        info.type = b.getAttribute("data-type");
        $("waType").classList.remove("err");
        syncType();
        saveInfo();
      } else if (b.hasAttribute("data-wa-clear")) {
        cart = [];
        saveCart();
        renderWa();
      } else if (b.hasAttribute("data-wa-start")) {
        startOrdering();
      } else if (b.hasAttribute("data-wa-close")) {
        closeWa();
      } else if (b.id === "waSend") {
        var bad = null;
        if (!info.type) { bad = $("waType"); bad.classList.add("err"); }
        else if (belowMin()) { bad = $("waMin"); }
        // delivery needs a typed address or a location pin
        else if (isDelivery(info.type) && !info.addr.trim() && !info.loc) { bad = waBody.querySelector('[data-f="addr"]'); bad.classList.add("err"); bad.focus(); }
        if (bad) { e.preventDefault(); bad.scrollIntoView({ block: "center", behavior: "smooth" }); return; }
        b.href = waLink(orderText());              // the link then opens WhatsApp with the order typed out
      }
    });
    waBody.addEventListener("input", function (e) {
      var k = e.target.getAttribute("data-f");
      if (!k) return;
      info[k] = e.target.value;
      e.target.classList.remove("err");
      if (k !== "note" && k !== "table") saveInfo();
    });

    $("waTipX").addEventListener("click", function (e) { e.stopPropagation(); hideTip(); });
    tip.addEventListener("click", function () { hideTip(); if (cart.length) openWa(); });
    // a gentle hint, once per visit
    setTimeout(function () {
      if (!cart.length && !sheet.open && !wa.open && tip.hidden && once("ei-tip")) {
        showTip("<b>Order here on WhatsApp</b>Tap + on a dish to add it, then tap the green button to send your order.", 9000);
      }
    }, 5000);
  }

  /* ---------- boot ---------- */
  render();
  syncBar();
  initSpy();
  initSearch();
  initView();
  initOrder();
  initSheet();
  // keep the floating WhatsApp button out of the way while typing a search
  q.addEventListener("focus", function () { root.classList.add("typing"); });
  q.addEventListener("blur", function () { root.classList.remove("typing"); });
  window.addEventListener("resize", syncBar, { passive: true });

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register("sw.js").catch(function () {}); });
  }
})();
