(function () {
  'use strict';
  var root = document.getElementById('pb-site');
  if (!root || !root.querySelector('#pb-menu')) return;
  var menuDialog = root.querySelector('#pb-menu');
  var pdfViewport = menuDialog.querySelector('.pb__pdf-viewport');
  var pdfCanvas = menuDialog.querySelector('canvas');
  var pdfStatus = menuDialog.querySelector('.pb__pdf-status');
  var pdfMessage = menuDialog.querySelector('[data-pdf-message]');
  var pdfRetry = menuDialog.querySelector('[data-pdf-retry]');
  var previousPage = menuDialog.querySelector('[data-pdf-prev]');
  var nextPage = menuDialog.querySelector('[data-pdf-next]');
  var zoomOut = menuDialog.querySelector('[data-pdf-out]');
  var zoomIn = menuDialog.querySelector('[data-pdf-in]');
  var fitWidth = menuDialog.querySelector('[data-pdf-fit]');
  var assetsBase = new URL('.', root.querySelector('.pb__navigation-header img').src);
  var lightbox = menuDialog.classList.contains('pb__pdf--lightbox');
  var previousOverflow;
  var pdfLibraryBase = new URL('pdfjs/', assetsBase);
  var pdfDocument;
  var pdfPromise;
  var loadedPdfSource;
  var pdfSource;
  var pdfPageNumber = 1;
  var pdfZoom = 1;
  var renderGeneration = 0;
  var activeRender;
  var menuOpener;
  var defaultTitle = menuDialog.querySelector('#pb-menu-title').textContent;

  function updatePdfControls() {
    previousPage.disabled = !pdfDocument || pdfPageNumber <= 1;
    nextPage.disabled = !pdfDocument || pdfPageNumber >= pdfDocument.numPages;
    zoomOut.disabled = !pdfDocument || pdfZoom <= 0.5;
    zoomIn.disabled = !pdfDocument || pdfZoom >= 3;
    fitWidth.disabled = !pdfDocument;
    menuDialog.querySelector('.pb__pdf-page-number').textContent = pdfDocument ? pdfPageNumber + ' / ' + pdfDocument.numPages : '— / —';
    menuDialog.querySelector('.pb__pdf-zoom').textContent = Math.round(pdfZoom * 100) + '%';
  }

  async function renderPdfPage() {
    if (!pdfDocument || !menuDialog.open) return;
    var generation = ++renderGeneration;
    if (activeRender) {
      activeRender.cancel();
      try { await activeRender.promise; } catch (error) { /* Previous drawing was cancelled. */ }
    }
    try {
      var page = await pdfDocument.getPage(pdfPageNumber);
      if (generation !== renderGeneration || !menuDialog.open) return;
      pdfStatus.hidden = false;
      pdfMessage.textContent = 'Открываем страницу…';
      pdfRetry.hidden = true;
      var padding = parseFloat(getComputedStyle(menuDialog.querySelector('.pb__pdf-page')).paddingLeft) * 2;
      var natural = page.getViewport({scale: 1});
      var fitScale = (pdfViewport.clientWidth - padding) / natural.width;
      if (lightbox) fitScale = Math.min(fitScale, (pdfViewport.clientHeight - padding) / natural.height);
      var scale = Math.max(0.1, fitScale) * pdfZoom;
      var view = page.getViewport({scale: scale});
      if (lightbox) menuDialog.style.setProperty('--pb-pdf-sheet-width', view.width + 'px');
      var pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      pdfCanvas.width = Math.ceil(view.width * pixelRatio);
      pdfCanvas.height = Math.ceil(view.height * pixelRatio);
      pdfCanvas.style.width = view.width + 'px';
      pdfCanvas.style.height = view.height + 'px';
      pdfCanvas.hidden = false;
      pdfCanvas.setAttribute('aria-label', 'Страница ' + pdfPageNumber + ' из ' + pdfDocument.numPages);
      activeRender = page.render({canvasContext: pdfCanvas.getContext('2d'), viewport: view, transform: [pixelRatio, 0, 0, pixelRatio, 0, 0]});
      await activeRender.promise;
      if (generation !== renderGeneration) return;
      activeRender = null;
      pdfStatus.hidden = true;
      pdfViewport.scrollTop = 0;
      updatePdfControls();
    } catch (error) {
      if (generation !== renderGeneration || error.name === 'RenderingCancelledException') return;
      pdfMessage.textContent = 'Не удалось показать страницу меню. Попробуйте ещё раз.';
      pdfRetry.hidden = false;
      pdfStatus.hidden = false;
    }
  }

  async function openPdf() {
    pdfStatus.hidden = false;
    pdfMessage.textContent = 'Открываем меню…';
    pdfRetry.hidden = true;
    var source = pdfSource;
    if (loadedPdfSource !== source) {
      loadedPdfSource = source;
      pdfPromise = null;
      pdfDocument = null;
      pdfPageNumber = 1;
      pdfZoom = 1;
      pdfCanvas.hidden = true;
      updatePdfControls();
    }
    try {
      if (!pdfPromise) {
        pdfPromise = import(new URL('pdf.mjs', pdfLibraryBase).href).then(function (pdfjs) {
          pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdf.worker.mjs', pdfLibraryBase).href;
          return pdfjs.getDocument({url: source, cMapUrl: new URL('cmaps/', pdfLibraryBase).href, cMapPacked: true, standardFontDataUrl: new URL('standard_fonts/', pdfLibraryBase).href, wasmUrl: new URL('wasm/', pdfLibraryBase).href}).promise;
        }).catch(function (error) { if (loadedPdfSource === source) pdfPromise = null; throw error; });
      }
      var document = await pdfPromise;
      if (pdfSource !== source || !menuDialog.open) return;
      pdfDocument = document;
      updatePdfControls();
      await renderPdfPage();
    } catch (error) {
      if (pdfSource !== source || !menuDialog.open) return;
      pdfMessage.textContent = 'Не удалось открыть меню. Попробуйте ещё раз.';
      pdfRetry.hidden = false;
    }
  }

  root.querySelectorAll('[data-pdf-source]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      pdfSource = new URL(link.dataset.pdfSource, document.baseURI).href;
      menuDialog.querySelector('#pb-menu-title').textContent = link.dataset.pdfTitle || defaultTitle;
      function showMenu() {
        previousOverflow = document.documentElement.style.overflow;
        document.documentElement.style.overflow = 'hidden';
        menuDialog.showModal();
        menuDialog.querySelector('.pb__pdf-close').focus({preventScroll: true});
        openPdf();
      }
      var navigation = link.closest('dialog');
      if (navigation && navigation.open) {
        menuOpener = root.querySelector('[data-nav-open][aria-expanded="true"]') || link;
        navigation.addEventListener('close', showMenu, {once: true});
        navigation.close();
      } else {
        menuOpener = link;
        showMenu();
      }
    });
  });
  menuDialog.querySelector('.pb__pdf-close').addEventListener('click', function () { menuDialog.close(); });
  menuDialog.addEventListener('close', function () {
    document.documentElement.style.overflow = previousOverflow;
    ++renderGeneration;
    if (activeRender) activeRender.cancel();
    if (menuOpener) menuOpener.focus({preventScroll: true});
  });
  previousPage.addEventListener('click', function () { if (pdfDocument && pdfPageNumber > 1) { --pdfPageNumber; updatePdfControls(); renderPdfPage(); } });
  nextPage.addEventListener('click', function () { if (pdfDocument && pdfPageNumber < pdfDocument.numPages) { ++pdfPageNumber; updatePdfControls(); renderPdfPage(); } });
  zoomOut.addEventListener('click', function () { pdfZoom = Math.max(0.5, pdfZoom - 0.25); updatePdfControls(); renderPdfPage(); });
  zoomIn.addEventListener('click', function () { pdfZoom = Math.min(3, pdfZoom + 0.25); updatePdfControls(); renderPdfPage(); });
  fitWidth.addEventListener('click', function () { pdfZoom = 1; updatePdfControls(); renderPdfPage(); });
  pdfRetry.addEventListener('click', openPdf);
  var pdfResizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(pdfResizeTimer);
    pdfResizeTimer = setTimeout(function () { if (menuDialog.open) renderPdfPage(); }, 150);
  });

  menuDialog.addEventListener('click', function (event) {
    if (lightbox && !event.target.closest('canvas, button, .pb__pdf-controls')) menuDialog.close();
  });
  menuDialog.addEventListener('keydown', function (event) {
    if (!lightbox || (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')) return;
    event.preventDefault();
    (event.key === 'ArrowLeft' ? previousPage : nextPage).click();
  });
  var touchStartX;
  var touchStartY;
  pdfCanvas.addEventListener('touchstart', function (event) {
    if (!lightbox || event.touches.length !== 1) return;
    touchStartX = event.touches[0].clientX;
    touchStartY = event.touches[0].clientY;
  }, {passive: true});
  pdfCanvas.addEventListener('touchend', function (event) {
    if (!lightbox || touchStartX === undefined) return;
    var dx = event.changedTouches[0].clientX - touchStartX;
    var dy = event.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) (dx > 0 ? previousPage : nextPage).click();
    touchStartX = undefined;
  }, {passive: true});
})();
