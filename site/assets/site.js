(function () {
  'use strict';
  var d = document.documentElement;
  // Language choice: persist on click of any switcher link
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('mizan-lang', a.getAttribute('data-lang')); } catch (e) {}
    });
  });
  // Theme toggle
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var dark = d.classList.toggle('dark');
      try { localStorage.setItem('mizan-theme', dark ? 'dark' : 'light'); } catch (e) {}
      var m = document.querySelector('meta[name="theme-color"]');
      if (m) m.setAttribute('content', dark ? '#0F172A' : '#F8FAFC');
    });
  });
  // Pricing billing toggle
  var grid = document.querySelector('[data-billing]');
  if (grid) {
    var btns = document.querySelectorAll('[data-billing-btn]');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-billing-btn');
        grid.setAttribute('data-billing', v);
        btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        document.querySelectorAll('[data-subscribe]').forEach(function (a) { a.setAttribute('data-billing', v); });
      });
    });
    document.querySelectorAll('[data-subscribe]').forEach(function (a) { a.setAttribute('data-billing', 'monthly'); });
  }
  // Close mobile menu when a link inside it is clicked
  var menu = document.querySelector('[data-menu]');
  if (menu) menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.removeAttribute('open'); }); });
})();
