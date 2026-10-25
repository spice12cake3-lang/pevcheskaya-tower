(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  if (!root) return;
  var dialog = root.querySelector('#pb-banquet');
  if (!dialog) return;
  var opener;
  var previousOverflow;
  root.querySelectorAll('[data-banquet-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      opener = button;
      previousOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = 'hidden';
      dialog.showModal();
      dialog.querySelector('#pb-banquet-title').focus({preventScroll: true});
    });
  });
  dialog.querySelector('.pb__banquet-close').addEventListener('click', function () { dialog.close(); });
  dialog.addEventListener('click', function (event) {
    if (event.target !== dialog) return;
    var bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', function () {
    document.documentElement.style.overflow = previousOverflow;
    if (opener && opener.isConnected) opener.focus({preventScroll: true});
  });
}());
