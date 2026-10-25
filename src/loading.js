(function () {
  'use strict';
  var finish = window.pbFinishLoading;
  if (!finish) return;
  // Wait for the first photograph, never for lazy images, PDFs or the whole page.
  var hero = document.querySelector('#pb-site img[fetchpriority="high"]');
  if (!hero) { finish(); return; }
  function ready() {
    if (hero.decode && hero.naturalWidth) hero.decode().catch(function () {}).then(finish);
    else finish();
  }
  if (hero.complete) ready();
  else {
    hero.addEventListener('load', ready, {once: true});
    hero.addEventListener('error', finish, {once: true});
  }
}());
