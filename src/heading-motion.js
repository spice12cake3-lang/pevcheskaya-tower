(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!root || reducedMotion.matches || !('IntersectionObserver' in window)) return;
  var headings = Array.from(root.querySelectorAll('h1, h2, h3')).filter(function (heading) {
    return !heading.closest('dialog') && !heading.classList.contains('pb__sr-only');
  });
  headings.forEach(function (heading) { heading.classList.add('pb__heading-pending'); });
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('pb__heading-enter');
      observer.unobserve(entry.target);
    });
  }, {threshold: 0, rootMargin: '0px'});
  function start() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (!reducedMotion.matches) headings.forEach(function (heading) { observer.observe(heading); });
      });
    });
  }
  // A slow body font must not keep every heading invisible.
  if (document.fonts) Promise.race([document.fonts.load('1em PBDisplay'), new Promise(function (resolve) { setTimeout(resolve, 450); })]).then(start, start);
  else start();
  reducedMotion.addEventListener('change', function (event) {
    if (!event.matches) return;
    observer.disconnect();
    headings.forEach(function (heading) { heading.classList.remove('pb__heading-pending', 'pb__heading-enter'); });
  });
}());
