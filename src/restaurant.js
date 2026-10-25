(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  if (!root) return;
  var navigation = root.querySelector('#pb-navigation');
  var openers = root.querySelectorAll('[data-nav-open]');
  var opener;
  var previousOverflow;
  function placeNavigation() {
    var bounds = root.querySelector('.pb__restaurant-intro, .pb__careers-header').getBoundingClientRect();
    var mobile = window.matchMedia('(max-width:639px)').matches;
    var fromHeader = opener && opener.closest('.pb__header');
    var top = mobile ? 12 : fromHeader ? 0 : Math.max(0, bounds.top);
    navigation.style.setProperty('--pb-nav-left', bounds.left + 'px');
    navigation.style.setProperty('--pb-nav-top', top + 'px');
    navigation.style.setProperty('--pb-nav-width', bounds.width + 'px');
    navigation.style.setProperty('--pb-nav-height', Math.max(0, window.innerHeight - top - 12) + 'px');
  }
  openers.forEach(function (button) {
   button.addEventListener('click', function () {
    opener = button;
    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    placeNavigation();
    openers.forEach(function (item) { item.setAttribute('aria-expanded', 'true'); });
    navigation.showModal();
    navigation.querySelector('[data-nav-close]').focus({preventScroll: true});
   });
  });
  navigation.querySelector('[data-nav-close]').addEventListener('click', function () { navigation.close(); });
  navigation.addEventListener('click', function (event) { if (event.target === navigation) navigation.close(); });
  navigation.addEventListener('close', function () {
    document.documentElement.style.overflow = previousOverflow;
    openers.forEach(function (item) { item.setAttribute('aria-expanded', 'false'); });
    if (opener) opener.focus({preventScroll: true});
  });
  window.addEventListener('resize', function () { if (navigation.open) placeNavigation(); });
  navigation.querySelectorAll('a:not([data-pdf-source])').forEach(function (link) {
    link.addEventListener('click', function () { navigation.close(); });
  });
  var floatingHeader = root.querySelector('.pb__header');
  var firstSection = root.querySelector('.pb__restaurant, .pb__careers');
  function updateFloatingHeader() {
    var visibleFromStart = root.classList.contains('pb--careers') && window.matchMedia('(min-width:1200px)').matches;
    floatingHeader.hidden = !visibleFromStart && firstSection.getBoundingClientRect().bottom > 0;
  }
  window.addEventListener('scroll', updateFloatingHeader, {passive: true});
  window.addEventListener('resize', updateFloatingHeader);
  var headerObserver = new IntersectionObserver(updateFloatingHeader);
  headerObserver.observe(firstSection);
  updateFloatingHeader();
  var photo = root.querySelector('#pb-venue-photo');
  var thumbnails = root.querySelectorAll('[data-gallery-src]');
  thumbnails.forEach(function (button) {
    button.addEventListener('click', function () {
      photo.src = button.dataset.gallerySrc;
      photo.srcset = button.dataset.gallerySrcset || '';
      photo.alt = button.dataset.galleryAlt;
      thumbnails.forEach(function (item) { item.setAttribute('aria-pressed', String(item === button)); });
    });
  });
  var routeDialog = root.querySelector('#pb-route');
  var routeOpener;
  var routePageOverflow;
  root.querySelectorAll('[data-directions-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      routeOpener = button;
      routePageOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = 'hidden';
      routeDialog.showModal();
      routeDialog.querySelector('.pb__route-close').focus({preventScroll: true});
    });
  });
  routeDialog.querySelector('.pb__route-close').addEventListener('click', function () { routeDialog.close(); });
  routeDialog.addEventListener('click', function (event) {
    if (event.target !== routeDialog) return;
    var bounds = routeDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) routeDialog.close();
  });
  routeDialog.addEventListener('close', function () {
    document.documentElement.style.overflow = routePageOverflow;
    if (routeOpener) routeOpener.focus({preventScroll: true});
  });

  var toast = root.querySelector('#pb-toast');
  var toastTimer;
  root.querySelectorAll('[data-social]').forEach(function (button) {
    button.addEventListener('click', function () {
      toast.textContent = 'Ссылку на ' + button.getAttribute('aria-label') + ' добавим при подготовке сайта к запуску.';
      toast.hidden = false;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () { toast.hidden = true; }, 5000);
    });
  });
})();
