(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  if (!root) return;

  var navigation = root.querySelector('#pb-navigation');
  var navigationOpeners = root.querySelectorAll('[data-nav-open]');
  var navigationOpener;
  var previousPageOverflow;
  function placeNavigation() {
    var introBounds = root.querySelector('.pb__intro').getBoundingClientRect();
    var fromHeader = !!navigationOpener.closest('.pb__header');
    var mobile = window.matchMedia('(max-width:639px)').matches;
    var top = mobile ? 12 : fromHeader ? 0 : Math.max(0, introBounds.top);
    var height = mobile ? window.innerHeight - 24 : fromHeader ? window.innerHeight : Math.min(introBounds.bottom, window.innerHeight) - top;
    navigation.style.setProperty('--pb-nav-left', Math.max(0, introBounds.left) + 'px');
    navigation.style.setProperty('--pb-nav-top', top + 'px');
    navigation.style.setProperty('--pb-nav-width', introBounds.width + 'px');
    navigation.style.setProperty('--pb-nav-height', Math.max(0, height) + 'px');
  }
  navigationOpeners.forEach(function (button) {
    button.addEventListener('click', function () {
      navigationOpener = button;
      previousPageOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = 'hidden';
      placeNavigation();
      navigationOpeners.forEach(function (item) { item.setAttribute('aria-expanded', 'true'); });
      navigation.showModal();
      navigation.querySelector('[data-nav-close]').focus({preventScroll: true});
    });
  });
  navigation.querySelector('[data-nav-close]').addEventListener('click', function () { navigation.close(); });
  navigation.addEventListener('click', function (event) {
    if (event.target === navigation) navigation.close();
  });
  navigation.addEventListener('close', function () {
    document.documentElement.style.overflow = previousPageOverflow;
    navigationOpeners.forEach(function (button) { button.setAttribute('aria-expanded', 'false'); });
    if (navigationOpener) navigationOpener.focus({preventScroll: true});
  });
  window.addEventListener('resize', function () { if (navigation.open) placeNavigation(); });
  navigation.querySelectorAll('a:not([data-pdf-source])').forEach(function (link) {
    link.addEventListener('click', function () { navigation.close(); });
  });
  var floatingHeader = root.querySelector('.pb__header');
  var hero = root.querySelector('.pb__hero');
  var initialMenu = root.querySelector('.pb__intro-header [data-nav-open]');
  function updateFloatingHeader() {
    var trigger = window.matchMedia('(max-width:639.98px)').matches && initialMenu ? initialMenu : hero;
    floatingHeader.hidden = trigger.getBoundingClientRect().bottom > 0;
  }
  window.addEventListener('scroll', updateFloatingHeader, {passive: true});
  window.addEventListener('resize', updateFloatingHeader);
  var headerObserver = new IntersectionObserver(updateFloatingHeader);
  headerObserver.observe(hero);
  if (initialMenu) headerObserver.observe(initialMenu);
  updateFloatingHeader();

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

  root.querySelectorAll('[role="tablist"]').forEach(function (list) {
    var tabs = Array.from(list.querySelectorAll('[role="tab"]'));
    function activate(tab, focus) {
      tabs.forEach(function (item) {
        var selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        root.querySelector('#' + item.getAttribute('aria-controls')).hidden = !selected;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () { activate(tab, false); });
      tab.addEventListener('keydown', function (event) {
        var next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); activate(tabs[next], true); }
      });
    });
  });

  var toast = root.querySelector('#pb-toast');
  var toastTimer;
  function notify(message) {
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.hidden = true; }, 5000);
  }

  var arrival = root.querySelector('#pb-arrival');
  var departure = root.querySelector('#pb-departure');
  function isoDate(date) {
    return date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');
  }
  var today = new Date();
  var tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
  arrival.value = isoDate(today);
  arrival.min = isoDate(today);
  departure.value = isoDate(tomorrow);
  departure.min = isoDate(tomorrow);
  arrival.addEventListener('change', function () {
    if (!arrival.value) return;
    var date = new Date(arrival.value + 'T12:00:00');
    date.setDate(date.getDate() + 1);
    departure.min = isoDate(date);
    if (departure.value <= arrival.value) departure.value = isoDate(date);
  });
  root.querySelector('#pb-find-room').addEventListener('click', function () {
    notify('Это макет виджета. Поиск и бронирование подключим позже.');
  });
  root.querySelectorAll('[data-social]').forEach(function (button) {
    button.addEventListener('click', function () { notify('Ссылку на ' + button.getAttribute('aria-label') + ' добавим при подготовке сайта к запуску.'); });
  });
})();
