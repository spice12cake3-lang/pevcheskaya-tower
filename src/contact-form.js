(function () {
  'use strict';
  document.querySelectorAll('#pb-site [data-feedback-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      form.querySelector('[data-form-message]').hidden = false;
    });
  });
}());
