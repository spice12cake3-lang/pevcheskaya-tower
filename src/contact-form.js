(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  if (!root) return;
  root.dataset.pbInput = 'pointer';
  document.addEventListener('pointerdown', function () { root.dataset.pbInput = 'pointer'; }, true);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Tab' || event.key.indexOf('Arrow') === 0) root.dataset.pbInput = 'keyboard';
  }, true);
  document.querySelectorAll('#pb-site [data-feedback-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      form.querySelector('[data-form-message]').hidden = false;
    });
  });
}());
