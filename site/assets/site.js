/* Mizan site behaviour. Copied verbatim to site/assets/site.js by build.py.
 *
 * Two halves:
 *   1. Preferences (theme, language, menu) - work on every page, no API.
 *   2. The account/billing client - only runs where build.py emitted the
 *      #mizan-data island, which carries the config and every translated
 *      string this file needs. No user-visible text is written here.
 *
 * The site never talks to Stripe and holds no Stripe key: POST /billing/checkout
 * returns a URL and we navigate to it. When build.py is given a Paddle client-side
 * token (CFG.paddle), checkout opens as a Paddle overlay instead; the site still
 * holds no API key and never decides entitlement.
 */
(function () {
  'use strict';
  var d = document.documentElement;
  var activeSection = '';   // element id of the home-page section the URL points at

  // ---------- preferences ----------
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('mizan-lang', a.getAttribute('data-lang')); } catch (e) {}
      // One page: switching language keeps the visitor on the section they are reading.
      var keep = activeSection ? '#' + activeSection : location.hash;
      if (keep) a.setAttribute('href', a.getAttribute('href').split('#')[0] + keep);
    });
  });

  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var dark = d.classList.toggle('dark');
      try { localStorage.setItem('mizan-theme', dark ? 'dark' : 'light'); } catch (e) {}
      var m = document.querySelector('meta[name="theme-color"]');
      if (m) m.setAttribute('content', dark ? '#0F172A' : '#F8FAFC');
    });
  });

  var menu = document.querySelector('[data-menu]');
  if (menu) {
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { menu.removeAttribute('open'); });
    });
  }

  // ---------- config + translations, shipped by build.py ----------
  var DATA = null;
  try {
    var island = document.getElementById('mizan-data');
    if (island) DATA = JSON.parse(island.textContent);
  } catch (e) {}
  if (!DATA) return;

  // ---------- section URLs (home page only) ----------
  // The home page is one page and its nav jumps to sections. Instead of /#pricing the
  // address bar shows /pricing/, which the host answers with the same home page (see
  // redirects() in build.py), so it survives a reload and can be shared. DATA.sections
  // maps the slug in the URL to the element id. Without JS the links stay plain #id
  // anchors and still scroll.
  var SECTIONS = DATA.sections || null;
  if (SECTIONS) {
    var has = function (o, k) { return Object.prototype.hasOwnProperty.call(o, k); };
    var slugOf = function (id) {
      for (var k in SECTIONS) if (has(SECTIONS, k) && SECTIONS[k] === id) return k;
      return '';
    };
    var showSection = function (slug, smooth) {
      var el = document.getElementById(SECTIONS[slug]);
      if (!el) return false;
      activeSection = SECTIONS[slug];
      try { el.scrollIntoView({ block: 'start', behavior: smooth ? 'smooth' : 'instant' }); }
      catch (e) { el.scrollIntoView(); }
      // replaceState, not pushState: Back leaves the page instead of stepping through sections.
      try { history.replaceState(null, '', '/' + slug + '/' + location.search); } catch (e) {}
      return true;
    };

    // Arriving on /pricing/ (the home page, answered by the host) or on /#pricing.
    var pm = /^\/([a-z-]+)\/?$/.exec(location.pathname);
    var first = pm && has(SECTIONS, pm[1]) ? pm[1] : slugOf(location.hash.slice(1));
    if (first) showSection(first, false);

    // Clicking a link to a section of this page.
    document.addEventListener('click', function (ev) {
      if (ev.defaultPrevented || ev.button || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
      var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
      var m = a && /^\/?#([a-z]+)$/.exec(a.getAttribute('href'));
      var slug = m && slugOf(m[1]);
      if (slug && showSection(slug, true)) ev.preventDefault();
    });
  }

  var CFG = DATA.cfg;
  var T = DATA.i18n || null;
  var EMAIL_KEY = CFG.tokenKey + '_email';

  function token() { try { return localStorage.getItem(CFG.tokenKey) || ''; } catch (e) { return ''; } }
  function setToken(v) { try { localStorage.setItem(CFG.tokenKey, v); } catch (e) {} }
  function knownEmail() { try { return localStorage.getItem(EMAIL_KEY) || ''; } catch (e) { return ''; } }
  function setEmail(v) {
    try { v ? localStorage.setItem(EMAIL_KEY, v) : localStorage.removeItem(EMAIL_KEY); } catch (e) {}
  }
  function clearToken() {
    try {
      localStorage.removeItem(CFG.tokenKey);
      localStorage.removeItem(CFG.tokenKey + '_pending');
    } catch (e) {}
    setEmail('');
  }

  // The deep link is only meaningful where the app can exist. Showing it on a
  // desktop would hand the buyer a button that cannot work.
  function isPhoneOS() {
    var ua = navigator.userAgent || '';
    if (/Android|iPhone|iPod/i.test(ua)) return true;
    // iPadOS 13+ reports itself as a Mac; touch points give it away.
    return /iPad/i.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  // The header renders "Sign in"; it becomes "Account" once a token exists.
  var hdr = document.querySelector('[data-auth-link]');
  if (hdr && token()) {
    hdr.setAttribute('href', hdr.getAttribute('data-account-href'));
    hdr.textContent = hdr.getAttribute('data-account-label');
  }

  // ---------- helpers ----------
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function show(el) { if (el) el.classList.remove('hidden'); }
  function hide(el) { if (el) el.classList.add('hidden'); }
  function clear(el) { while (el && el.firstChild) el.removeChild(el.firstChild); }
  function put(root, sel, value) {
    var el = root && root.querySelector(sel);
    if (el) el.textContent = value;
    return el;
  }

  function fmtDate(v) {
    var dt = new Date(v);
    if (isNaN(dt.getTime())) return String(v);
    try { return dt.toLocaleDateString(CFG.lang, { year: 'numeric', month: 'long', day: 'numeric' }); }
    catch (e) { return dt.toISOString().slice(0, 10); }
  }

  // Panels are assembled with textContent only, so nothing the API returns is
  // ever interpreted as HTML.
  function panel(tone, heading, body) {
    var box = document.createElement('div');
    box.className = 'rounded-xl border p-4 text-sm ' +
      (tone === 'bad' ? 'border-red-500/50 bg-red-500/10' : 'border-line bg-surface');
    if (heading) {
      var h = document.createElement('p');
      h.className = 'font-semibold';
      h.textContent = heading;
      box.appendChild(h);
    }
    if (body) {
      var p = document.createElement('p');
      p.className = heading ? 'mt-1 text-muted' : 'text-muted';
      p.textContent = body;
      box.appendChild(p);
    }
    return box;
  }

  function retryPanel(message, again) {
    var box = panel('bad', T.billing.error_h, message);
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'mt-3 rounded-lg border border-line bg-bg px-3.5 py-2 text-sm font-semibold hover:border-muted';
    b.textContent = T.auth.errors.retry;
    b.addEventListener('click', again);
    box.appendChild(b);
    return box;
  }

  // 501 BILLING_PROVIDER_NOT_CONFIGURED: Stripe is not wired up yet. Calm, never red.
  function soonPanel() {
    return panel('calm', T.billing.soon_h, T.billing.soon_p.replace('{email}', T.email));
  }

  // ---------- /app/billing/activated ----------
  // The page the OS hides when the app is installed. It has no language prefix,
  // so every language is in the markup and the right one is revealed here.
  // It never calls the API: it states the purchase is done and points at the app.
  var appRoot = document.querySelector('[data-app-handoff]');
  if (appRoot && DATA.app) {
    var appLangs = Object.keys(DATA.app);

    var chosenLang = (function () {
      var q = null;
      try { q = new URLSearchParams(location.search).get('lang'); } catch (e) {}
      if (appLangs.indexOf(q) >= 0) return q;
      try {
        var saved = localStorage.getItem('mizan-lang');
        if (appLangs.indexOf(saved) >= 0) return saved;
      } catch (e) {}
      var nav = (navigator.language || '').slice(0, 2).toLowerCase();
      return appLangs.indexOf(nav) >= 0 ? nav : appLangs[0];
    })();

    var applyAppLang = function (code) {
      var block = appRoot.querySelector('[data-applang="' + code + '"]');
      if (!block) return;
      appRoot.querySelectorAll('[data-applang]').forEach(function (el) {
        if (el.getAttribute('data-applang') === code) show(el); else hide(el);
      });
      appRoot.querySelectorAll('[data-applang-btn]').forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-applang-btn') === code ? 'true' : 'false');
      });
      d.setAttribute('lang', code);
      d.setAttribute('dir', block.getAttribute('dir') || 'ltr');
      var strings = DATA.app[code] || {};
      if (strings.title) document.title = strings.title;
      var who = knownEmail();
      if (who && strings.p) put(block, '[data-app-text]', strings.p.replace('{email}', who));
    };

    appRoot.querySelectorAll('[data-applang-btn]').forEach(function (b) {
      b.addEventListener('click', function () {
        var code = b.getAttribute('data-applang-btn');
        try { localStorage.setItem('mizan-lang', code); } catch (e) {}
        applyAppLang(code);
      });
    });
    applyAppLang(chosenLang);
  }

  if (!T) return; // everything below needs the full translation payload

  // ---------- API ----------
  function ApiError(status, code, message) {
    this.status = status;
    this.code = code;
    this.message = message || '';
  }

  function messageOf(body) {
    if (!body) return '';
    var m = body.message;
    if (m && typeof m.join === 'function') m = m.join(' '); // Nest validation arrays
    return m || body.error || '';
  }

  // Retries once on a network failure or 5xx, then hands the error to the
  // caller, which offers an explicit retry.
  function request(path, opts) {
    opts = opts || {};
    var init = { method: opts.method || 'GET', headers: {}, credentials: 'omit' };
    if (opts.body !== undefined) {
      init.headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(opts.body);
    }
    if (opts.auth) {
      var t = token();
      if (!t) return Promise.reject(new ApiError(401, 'NO_TOKEN', ''));
      init.headers['Authorization'] = 'Bearer ' + t;
    }
    function attempt(retried) {
      return fetch(CFG.api + path, init).then(function (res) {
        if (res.status >= 500 && !retried) {
          return wait(700).then(function () { return attempt(true); });
        }
        return res.text().then(function (raw) {
          var body = null;
          try { body = raw ? JSON.parse(raw) : null; } catch (e) {}
          if (res.ok) return body;
          throw new ApiError(res.status, body && body.code, messageOf(body));
        });
      }, function () {
        if (!retried) return wait(700).then(function () { return attempt(true); });
        throw new ApiError(0, 'NETWORK', '');
      });
    }
    return attempt(false);
  }

  // ---------- the plan the visitor is trying to buy ----------
  // Carried in the query string from pricing through signup/login to checkout.
  // Losing it here loses the sale, so every hop re-reads and re-writes it.
  function intent() {
    var q = null;
    try { q = new URLSearchParams(location.search); } catch (e) {}
    var plan = q ? q.get('plan') : null;
    var period = q ? q.get('period') : null;
    if (CFG.plans.indexOf(plan) < 0) plan = null;
    if (period !== 'yearly') period = 'monthly';
    return { plan: plan, period: period };
  }

  function intentQS(plan, period) {
    if (!plan) return '';
    return '?plan=' + encodeURIComponent(plan) + '&period=' + encodeURIComponent(period || 'monthly');
  }

  // Any 401: drop the token, go to login, keep the intent.
  function toLogin(plan, period) {
    clearToken();
    location.href = CFG.urls.login + intentQS(plan, period);
  }

  // ---------- checkout ----------
  // What the visitor is paying for, remembered across the trip to Stripe.
  // Two jobs:
  //   1. the success page needs it, because a trialing account already has a
  //      plan and "any plan" would declare victory with the OLD one showing;
  //   2. the account page needs it, so that someone who has just paid is never
  //      told they have no subscription while the webhook is still in flight.
  // localStorage, not sessionStorage: the buyer may come back in a new tab.
  var PENDING_KEY = CFG.tokenKey + '_pending';
  var PENDING_MAX_AGE = 30 * 60 * 1000;

  function setPending(plan) {
    try {
      if (plan) localStorage.setItem(PENDING_KEY, JSON.stringify({ plan: plan, ts: Date.now() }));
      else localStorage.removeItem(PENDING_KEY);
    } catch (e) {}
  }
  function readPending() {
    try {
      var raw = localStorage.getItem(PENDING_KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || !v.plan || !v.ts || Date.now() - v.ts > PENDING_MAX_AGE) {
        localStorage.removeItem(PENDING_KEY);
        return null;
      }
      return v;
    } catch (e) { return null; }
  }
  function clearPending() { setPending(''); }

  // ---------- Paddle checkout (web) ----------
  // Present only when build.py was given a client-side token (CFG.paddle). The
  // token and the price ids are public by design; no API key ever reaches this
  // file. Nothing here grants access: the plan is written by the server from
  // Paddle's signed webhook, and the success page reads it back from the API.
  var PADDLE = CFG.paddle || null;
  var paddleLoading = null;   // Promise<Paddle>, reset after a failed load
  var paddleReady = false;    // Paddle.Initialize may only run once per page
  var paddleBusy = false;     // one checkout at a time, from click until closed
  var paddleRun = null;       // { plan, period, host, timer } of the open checkout
  var PADDLE_OPEN_TIMEOUT = 20000;

  // The API token is "<base64url JSON>.<signature>". The JSON half is read here
  // only to tell whether anyone is signed in at all, so a signed-out click goes to
  // login instead of making a request that is certain to 401. Nothing read from it
  // reaches Paddle: the server decides who a checkout is for.
  function session() {
    var t = token();
    if (!t) return null;
    try {
      var b = t.split('.')[0].replace(/-/g, '+').replace(/_/g, '/');
      while (b.length % 4) b += '=';
      var bytes = atob(b);
      var json = decodeURIComponent(bytes.split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      var p = JSON.parse(json);
      if (!p || !p.userId) return null;
      if (typeof p.exp === 'number' && p.exp * 1000 <= Date.now()) return null;
      return { userId: String(p.userId), email: String(p.email || knownEmail() || '') };
    } catch (e) { return null; }
  }

  function loadPaddle() {
    if (paddleLoading) return paddleLoading;
    paddleLoading = new Promise(function (resolve, reject) {
      if (window.Paddle) { resolve(window.Paddle); return; }
      var s = document.createElement('script');
      s.src = PADDLE.js;
      s.async = true;
      s.onload = function () {
        if (window.Paddle) resolve(window.Paddle); else reject(new Error('paddle-missing'));
      };
      s.onerror = function () { reject(new Error('paddle-blocked')); };
      document.head.appendChild(s);
    });
    // Offline or a content blocker: the next click must be able to try again.
    paddleLoading.catch(function () { paddleLoading = null; });
    return paddleLoading;
  }

  function setSubscribeBusy(on) {
    document.querySelectorAll('[data-subscribe]').forEach(function (a) {
      if (on) { a.setAttribute('aria-disabled', 'true'); a.classList.add('opacity-70'); }
      else { a.removeAttribute('aria-disabled'); a.classList.remove('opacity-70'); }
    });
  }

  function paddleIdle() {
    if (paddleRun && paddleRun.timer) clearTimeout(paddleRun.timer);
    paddleBusy = false;
    paddleRun = null;
    setSubscribeBusy(false);
  }

  function paddleFailed(run) {
    paddleIdle();
    clear(run.host);
    run.host.appendChild(retryPanel(T.billing.checkout_unavailable, function () {
      paddleCheckout(run.plan, run.period, run.host);
    }));
    // On the pricing page the status sits under the cards, out of view after a click.
    try { run.host.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) {}
  }

  function onPaddleEvent(ev) {
    if (!ev) return;
    var run = paddleRun;

    if (ev.name === 'checkout.completed') {
      // Payment accepted by Paddle. That is not access: the success page waits for
      // the server, which only grants the plan from the verified webhook. Handled
      // with or without a run of ours, because a checkout opened from one of
      // Paddle's own links (see below) has none.
      //
      // The plan is read from custom data the SERVER put on the transaction. It
      // only decides which plan the success page waits to see; what the account
      // actually receives is decided by the webhook, from the price.
      var done = ev.data || {};
      var bought = (run && run.plan) || (done.custom_data && done.custom_data.mizan_plan);
      if (CFG.plans.indexOf(bought) >= 0) setPending(bought);
      var txn = done.transaction_id;
      paddleRun = null; // the close below must not repaint this page
      try { window.Paddle.Checkout.close(); } catch (e) {}
      location.href = CFG.urls.success + (txn ? '?txn=' + encodeURIComponent(txn) : '');
      return;
    }

    if (!run) return;
    if (ev.name === 'checkout.loaded') {
      // The overlay is up and covers the page; stop the watchdog but stay busy
      // until it closes, so nothing underneath can open a second checkout.
      if (run.timer) { clearTimeout(run.timer); run.timer = null; }
      clear(run.host);
    } else if (ev.name === 'checkout.closed') {
      clear(run.host);
      paddleIdle();
    } else if (ev.name === 'checkout.error') {
      try { window.Paddle.Checkout.close(); } catch (e) {}
      paddleFailed(run);
    }
  }

  // Initialised once per page. Sandbox must be declared before Initialize; live is
  // Paddle's default, so a production build never calls Environment.set at all.
  function ensurePaddle(P) {
    if (paddleReady) return;
    if (PADDLE.env === 'sandbox') P.Environment.set('sandbox');
    P.Initialize({ token: PADDLE.token, eventCallback: onPaddleEvent });
    paddleReady = true;
  }

  function paddleCheckout(plan, period, host) {
    if (paddleBusy) return;
    if (!session()) { toLogin(plan, period); return; } // no, expired or unreadable token

    paddleBusy = true;
    setSubscribeBusy(true);
    clear(host);
    host.appendChild(panel('calm', T.billing.starting, ''));
    var run = paddleRun = { plan: plan, period: period, host: host, timer: null };
    run.timer = setTimeout(function () {
      if (paddleRun !== run) return;
      try { if (window.Paddle) window.Paddle.Checkout.close(); } catch (e) {}
      paddleFailed(run);
    }, PADDLE_OPEN_TIMEOUT);

    // The SERVER creates the transaction. It fixes the customer, the price and the
    // plan, and the browser is only handed an id to open. This page's Paddle token
    // is public by design, so anything chosen here (a price, an account id typed
    // into custom data) could be chosen by anyone with a console. Fetched alongside
    // Paddle.js so the two waits overlap.
    Promise.all([
      request('/billing/paddle/transaction', { method: 'POST', auth: true, body: { plan: plan, period: period } }),
      loadPaddle()
    ]).then(function (res) {
      if (paddleRun !== run) return; // timed out while waiting
      var transactionId = res[0] && res[0].transactionId;
      if (!transactionId) throw new Error('no-transaction');
      var P = res[1];
      ensurePaddle(P);
      P.Checkout.open({
        transactionId: transactionId,
        settings: {
          displayMode: 'overlay',
          variant: 'one-page',
          locale: CFG.lang,
          theme: d.classList.contains('dark') ? 'dark' : 'light',
          // The customer is already fixed on the transaction; the buyer must not
          // be able to swap it for someone else's.
          allowLogout: false
        }
      });
    }).catch(function (e) {
      if (paddleRun !== run) return;
      if (e && e.status === 401) { paddleIdle(); clear(host); toLogin(plan, period); return; }
      if (e && e.status === 501) { paddleIdle(); clear(host); host.appendChild(soonPanel()); return; }
      paddleFailed(run);
    });
  }

  // Paddle's own links, the account's default payment link and the "update your
  // payment method" emails, land on one of our pages with ?_ptxn=<transaction>.
  // Paddle.js opens that checkout by itself, but only once it has been initialised
  // on the page, so do that here. Without it those links open a page that does
  // nothing.
  if (PADDLE && /[?&]_ptxn=/.test(location.search)) {
    loadPaddle().then(ensurePaddle).catch(function () {});
  }

  function checkout(plan, period, host) {
    if (PADDLE) { paddleCheckout(plan, period, host); return; }
    clear(host);
    host.appendChild(panel('calm', T.billing.starting, ''));
    request('/billing/checkout', { method: 'POST', auth: true, body: { plan: plan, period: period } })
      .then(function (r) {
        if (r && r.url) { setPending(plan); location.href = r.url; return; }
        clear(host);
        host.appendChild(panel('bad', T.billing.error_h, ''));
      })
      .catch(function (e) {
        clear(host);
        if (e.status === 401) { toLogin(plan, period); return; }
        if (e.status === 501 && e.code === 'BILLING_PROVIDER_NOT_CONFIGURED') {
          host.appendChild(soonPanel());
          return;
        }
        if (e.status === 400) {
          host.appendChild(panel('bad', T.billing.error_h, e.message));
          return;
        }
        host.appendChild(retryPanel(e.message || T.auth.errors.network, function () {
          checkout(plan, period, host);
        }));
      });
  }

  // ---------- pricing ----------
  var grid = document.querySelector('[data-billing]');
  if (grid) {
    var billHost = document.querySelector('[data-billing-status]');
    var periodBtns = document.querySelectorAll('[data-billing-btn]');
    var subs = document.querySelectorAll('[data-subscribe]');

    var applyPeriod = function (v) {
      grid.setAttribute('data-billing', v);
      periodBtns.forEach(function (x) {
        x.setAttribute('aria-pressed', x.getAttribute('data-billing-btn') === v ? 'true' : 'false');
      });
      subs.forEach(function (a) {
        a.setAttribute('data-period', v);
        // Keep the signed-out path carrying the plan and the period too.
        a.setAttribute('href', a.getAttribute('data-signup-base') + intentQS(a.getAttribute('data-plan'), v));
      });
    };

    periodBtns.forEach(function (b) {
      b.addEventListener('click', function () { applyPeriod(b.getAttribute('data-billing-btn')); });
    });
    applyPeriod('monthly');

    // Signed in: fetch Paddle.js now so the first click opens without a wait.
    if (PADDLE && token()) loadPaddle().catch(function () {});

    subs.forEach(function (a) {
      a.addEventListener('click', function (ev) {
        if (paddleBusy) { ev.preventDefault(); return; } // one checkout at a time
        if (!token()) return; // follow the href to signup, plan preserved
        ev.preventDefault();
        checkout(a.getAttribute('data-plan'), a.getAttribute('data-period') || 'monthly', billHost);
      });
    });
  }

  // ---------- login / signup ----------
  var form = document.querySelector('[data-auth-form]');
  if (form) {
    var mode = form.getAttribute('data-auth-form');
    var want = intent();
    var errBox = form.querySelector('[data-form-error]');
    var submitBtn = form.querySelector('[data-submit]');
    var authHost = document.querySelector('[data-auth-status]');

    if (want.plan && PADDLE) loadPaddle().catch(function () {});

    if (want.plan) {
      var note = document.querySelector('[data-intent-note]');
      if (note) {
        note.textContent = T.auth.continue_plan
          .replace('{plan}', T.planNames[want.plan] || want.plan)
          .replace('{period}', T.periods[want.period] || want.period);
        show(note);
      }
    }

    // Moving between login and signup must not drop the plan.
    document.querySelectorAll('[data-carry-intent]').forEach(function (a) {
      a.setAttribute('href', a.getAttribute('href').split('?')[0] + intentQS(want.plan, want.period));
    });

    var idle = function () {
      submitBtn.disabled = false;
      submitBtn.textContent = submitBtn.getAttribute('data-label');
    };
    var fail = function (msg) {
      errBox.textContent = msg;
      show(errBox);
      idle();
    };

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      hide(errBox);
      clear(authHost);

      var emailEl = form.querySelector('#email');
      var passEl = form.querySelector('#password');
      var nameEl = form.querySelector('#name');
      var email = (emailEl.value || '').trim();
      var password = passEl.value || '';

      if (!email) { fail(T.auth.errors.email); emailEl.focus(); return; }
      if (mode === 'signup' ? password.length < 6 : !password) {
        fail(T.auth.errors.password);
        passEl.focus();
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = submitBtn.getAttribute('data-working');

      var payload = { email: email, password: password };
      if (nameEl && nameEl.value.trim()) payload.name = nameEl.value.trim();

      request('/auth/' + mode, { method: 'POST', body: payload })
        .then(function (r) {
          if (!r || !r.token) { fail(T.auth.errors.network); return; }
          setToken(r.token);
          setEmail((r.user && r.user.email) || email);
          // Straight to checkout: no second click, nothing lost in between.
          if (want.plan) { checkout(want.plan, want.period, authHost); return; }
          location.href = CFG.urls.account;
        })
        .catch(function (e) {
          // A 401 here means wrong credentials, not an expired session, so it is
          // shown in place and never bounced back to this same page.
          fail(e.status === 0 ? T.auth.errors.network : (e.message || T.auth.errors.network));
        });
    });
  }

  // ---------- billing success ----------
  var successRoot = document.querySelector('[data-billing-success]');
  if (successRoot) {
    var waitPane = successRoot.querySelector('[data-state="wait"]');
    var okPane = successRoot.querySelector('[data-state="ok"]');
    var pendPane = successRoot.querySelector('[data-state="pending"]');

    var sessionId = null;
    try {
      var sq = new URLSearchParams(location.search);
      sessionId = sq.get('session_id') || sq.get('txn'); // Stripe session or Paddle transaction
    } catch (e) {}
    if (sessionId) {
      put(successRoot, '[data-ref-value]', sessionId);
      show(successRoot.querySelector('[data-ref]'));
    }

    // The entitlement is written by a webhook that can land a second or two
    // after this redirect. Read the plan 5 times across ~10s before concluding
    // anything: an empty first read is normal and must never look like failure.
    var pending = readPending();
    var expected = pending && pending.plan;
    var settled = function (p) {
      if (!p || !p.plan) return false;
      // Wait for the plan actually bought. Without that, an account upgrading
      // from the free trial would "succeed" while still showing Trial.
      if (expected) return p.plan === expected;
      return p.status !== 'trialing';
    };

    var STEPS = [0, 2000, 2500, 2500, 3000];
    var readPlan = function (i) {
      return wait(STEPS[i])
        .then(function () { return request('/auth/me/plan', { auth: true }); })
        .then(function (p) {
          if (settled(p)) return p;
          return i + 1 < STEPS.length ? readPlan(i + 1) : null;
        })
        .catch(function (e) {
          if (e.status === 401) return null; // still not a failed payment
          return i + 1 < STEPS.length ? readPlan(i + 1) : null;
        });
    };

    readPlan(0).then(function (p) {
      hide(waitPane);
      // Not confirmed yet: keep the pending marker so /account/ also says
      // "activating" rather than "no subscription".
      if (!p) { show(pendPane); return; } // "being activated", never "failed"
      clearPending();

      put(okPane, '[data-plan-name]', T.planNames[p.plan] || p.plan);
      var when = p.currentPeriodEnd || p.trialEndsAt;
      if (when) {
        put(okPane, '[data-renew-label]', p.currentPeriodEnd ? T.account.renews_l : T.account.trial_ends_l);
        put(okPane, '[data-renew-value]', fmtDate(when));
        show(okPane.querySelector('[data-renew]'));
      }
      show(okPane);

      // The handoff, only once the purchase is confirmed above it.
      if (isPhoneOS()) {
        show(okPane.querySelector('[data-handoff-mobile]'));
      } else {
        var who = knownEmail();
        if (who) {
          put(okPane, '[data-desktop-text]', T.billing.success.desktop_p.replace('{email}', who));
        }
        show(okPane.querySelector('[data-handoff-desktop]'));
      }
    });
  }

  // ---------- account ----------
  // Backend provider values: "paddle" or "stripe" (bought here) | "play_store" |
  // "app_store" | "promotional". Only a web subscription can use POST /billing/portal;
  // the store ones 400, and the server picks Paddle's portal or Stripe's by itself.
  function fromStore(p) {
    return !!p && (p.provider === 'play_store' || p.provider === 'app_store');
  }
  function storeName(p) {
    return (p && T.account.providers && T.account.providers[p.provider]) || '';
  }
  function storeText(p) {
    return T.account.store_p.split('{store}').join(storeName(p));
  }

  var accRoot = document.querySelector('[data-account]');
  if (accRoot) {
    if (!token()) {
      location.replace(CFG.urls.login);
    } else {
      var loadingEl = accRoot.querySelector('[data-account-loading]');
      var bodyEl = accRoot.querySelector('[data-account-body]');
      var accHost = accRoot.querySelector('[data-account-status]');
      var current = null;

      accRoot.querySelector('[data-signout]').addEventListener('click', function () {
        clearToken();
        location.href = CFG.urls.home;
      });

      var portalBtn = accRoot.querySelector('[data-portal]');
      var portalHost = accRoot.querySelector('[data-portal-status]');
      portalBtn.addEventListener('click', function () {
        clear(portalHost);
        portalBtn.disabled = true;
        request('/billing/portal', { method: 'POST', auth: true })
          .then(function (r) {
            if (r && r.url) { location.href = r.url; return; }
            portalBtn.disabled = false;
            portalHost.appendChild(panel('bad', T.billing.error_h, ''));
          })
          .catch(function (e) {
            portalBtn.disabled = false;
            if (e.status === 401) { toLogin(null, null); return; }
            if (e.status === 501 && e.code === 'BILLING_PROVIDER_NOT_CONFIGURED') {
              portalHost.appendChild(soonPanel());
              return;
            }
            if (e.status === 400) {
              // Usually: the subscription is billed by an app store, so the
              // portal cannot manage it. Say where it actually is managed.
              portalHost.appendChild(fromStore(current)
                ? panel('calm', T.account.store_h, e.message || storeText(current))
                : panel('bad', T.billing.error_h, e.message));
              return;
            }
            portalHost.appendChild(retryPanel(e.message || T.auth.errors.network, function () {
              portalBtn.click();
            }));
          });
      });

      var renderUsage = function (p) {
        var dl = accRoot.querySelector('[data-usage]');
        var usage = p.usage || {};
        var limits = p.limits || {};
        var keys = Object.keys(usage);
        if (!keys.length) return;
        clear(dl);
        keys.forEach(function (k) {
          var row = document.createElement('div');
          row.className = 'flex justify-between gap-4';
          var dt = document.createElement('dt');
          dt.className = 'text-muted';
          dt.textContent = (T.account.usage_labels && T.account.usage_labels[k]) || k.replace(/_/g, ' ');
          var dd = document.createElement('dd');
          dd.className = 'font-medium';
          var lim = limits[k];
          var unlimited = lim === null || lim === undefined || lim < 0;
          dd.textContent = String(usage[k]) + ' ' + T.account.usage_of + ' ' +
            (unlimited ? T.account.unlimited : String(lim));
          row.appendChild(dt);
          row.appendChild(dd);
          dl.appendChild(row);
        });
        show(accRoot.querySelector('[data-usage-card]'));
      };

      var render = function (p) {
        current = p;
        var who = knownEmail();
        if (who) {
          put(accRoot, '[data-email]', who);
          show(accRoot.querySelector('[data-identity]'));
        }
        // A purchase counts as landed only when the plan on the server is the one
        // that was bought. Anything else still means "activating": an account
        // upgrading from the free trial has a plan already, and treating that as
        // success would leave a paying customer staring at "Trial".
        var pend = readPending();
        var hasPlan = !!(p && p.plan);
        if (pend && hasPlan && p.plan === pend.plan) { clearPending(); pend = null; }
        if (pend) show(accRoot.querySelector('[data-activating-card]'));

        if (!hasPlan) {
          // Never tell someone who has just paid that they have no subscription.
          if (!pend) show(accRoot.querySelector('[data-no-plan-card]'));
          return;
        }
        var card = accRoot.querySelector('[data-plan-card]');
        put(card, '[data-plan-name]', T.planNames[p.plan] || p.plan);
        put(card, '[data-status]', (T.account.statuses && T.account.statuses[p.status]) || p.status || '');

        var note = T.account.status_notes && T.account.status_notes[p.status];
        if (note) {
          put(card, '[data-status-note]', note);
          show(card.querySelector('[data-status-note]'));
        }
        var when = p.currentPeriodEnd || p.trialEndsAt;
        if (when) {
          put(card, '[data-renew-label]', p.currentPeriodEnd ? T.account.renews_l : T.account.trial_ends_l);
          put(card, '[data-renew-value]', fmtDate(when));
          show(card.querySelector('[data-renew]'));
        }
        var prov = T.account.providers && T.account.providers[p.provider];
        if (prov) {
          put(card, '[data-provider]', prov);
          show(card.querySelector('[data-provider-row]'));
        }
        show(card);

        if (fromStore(p)) {
          // No portal button at all: POST /billing/portal would 400.
          put(accRoot, '[data-store-card] [data-store-text]', storeText(p));
          show(accRoot.querySelector('[data-store-card]'));
        } else {
          show(accRoot.querySelector('[data-manage-card]'));
        }
        renderUsage(p);
      };

      // Re-checking must start from a clean slate, or a stale card stays up.
      var RESET = ['[data-plan-card]', '[data-activating-card]', '[data-no-plan-card]',
        '[data-manage-card]', '[data-store-card]', '[data-usage-card]',
        '[data-plan-card] [data-status-note]', '[data-plan-card] [data-renew]',
        '[data-plan-card] [data-provider-row]'];

      var load = function () {
        clear(accHost);
        RESET.forEach(function (sel) { hide(accRoot.querySelector(sel)); });
        show(loadingEl);
        request('/auth/me/plan', { auth: true })
          .then(function (p) {
            hide(loadingEl);
            show(bodyEl);
            render(p);
          })
          .catch(function (e) {
            hide(loadingEl);
            if (e.status === 401) { toLogin(null, null); return; }
            accHost.appendChild(retryPanel(e.message || T.auth.errors.network, load));
          });
      };

      var againBtn = accRoot.querySelector('[data-activating-retry]');
      if (againBtn) againBtn.addEventListener('click', load);

      load();
    }
  }

  // ---------- delete account ----------
  var delRoot = document.querySelector('[data-delete-web]');
  if (delRoot) {
    var signedIn = !!token();
    show(delRoot.querySelector(signedIn ? '[data-del-signedin]' : '[data-del-signedout]'));
    if (signedIn) {
      var startBtn = delRoot.querySelector('[data-del-start]');
      var confirmBox = delRoot.querySelector('[data-del-confirm]');
      var keepBtn = delRoot.querySelector('[data-del-keep]');
      var check = delRoot.querySelector('[data-del-check]');
      var goBtn = delRoot.querySelector('[data-del-go]');
      var delHost = delRoot.querySelector('[data-del-status]');

      startBtn.addEventListener('click', function () {
        hide(startBtn);
        show(confirmBox);
        check.focus();
      });
      keepBtn.addEventListener('click', function () {
        hide(confirmBox);
        show(startBtn);
        check.checked = false;
        clear(delHost);
      });
      goBtn.addEventListener('click', function () {
        clear(delHost);
        if (!check.checked) {
          delHost.appendChild(panel('bad', '', T.delete.check_required));
          return;
        }
        goBtn.disabled = true;
        goBtn.textContent = goBtn.getAttribute('data-working');
        request('/auth/me', { method: 'DELETE', auth: true })
          .then(function () {
            clearToken();
            hide(delRoot.querySelector('[data-del-signedin]'));
            show(delRoot.querySelector('[data-del-done]'));
          })
          .catch(function (e) {
            goBtn.disabled = false;
            goBtn.textContent = goBtn.getAttribute('data-label');
            if (e.status === 401) { toLogin(null, null); return; }
            delHost.appendChild(panel('bad', T.billing.error_h, e.message || T.auth.errors.network));
          });
      });
    }
  }
})();
