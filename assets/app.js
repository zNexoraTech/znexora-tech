// Theme toggle (remembers your choice) and instant search.
(function () {
  var root = document.documentElement;
  function apply(theme) {
    if (theme === 'dark' || theme === 'light') root.setAttribute('data-theme', theme);
  }
  try { apply(localStorage.getItem('theme')); } catch (e) {}

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', function () {
      var current = root.getAttribute('data-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      var next = current === 'dark' ? 'light' : 'dark';
      apply(next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });

    document.querySelectorAll('.prose pre').forEach(function (pre) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'copy-btn'; b.textContent = 'Copy';
      b.addEventListener('click', function () {
        var code = pre.querySelector('code');
        navigator.clipboard.writeText((code || pre).innerText).then(function () {
          b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1500);
        });
      });
      pre.appendChild(b);
    });

    var input = document.getElementById('search-input');
    var out = document.getElementById('search-results');
    if (!input || !out) return;
    var index = null;
    function load() {
      if (index) return Promise.resolve(index);
      return fetch(input.dataset.index).then(function (r) { return r.json(); })
        .then(function (data) { index = data; return data; })
        .catch(function () { index = []; return index; });
    }
    input.addEventListener('focus', load, { once: true });
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      if (q.length < 2) { out.hidden = true; out.innerHTML = ''; return; }
      load().then(function (idx) {
        var words = q.split(/\s+/);
        var hits = idx.filter(function (p) {
          var hay = (p.t + ' ' + p.s + ' ' + p.c + ' ' + p.v).toLowerCase();
          return words.every(function (w) { return hay.indexOf(w) !== -1; });
        }).slice(0, 8);
        out.innerHTML = hits.length
          ? hits.map(function (h) { return '<li><a href="' + esc(h.u) + '">' + esc(h.t) + '</a></li>'; }).join('')
          : '<li class="empty">No briefings match. Try a CVE ID or vendor name.</li>';
        out.hidden = false;
      });
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') out.hidden = true; });
    document.addEventListener('click', function (e) { if (!e.target.closest('.search')) out.hidden = true; });
  });
})();
