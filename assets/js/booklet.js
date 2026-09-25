/* Grammar booklet pages (cefr/english-classes-*.html).

   On screen a booklet is a normal, fluid site page (assets/css/booklet.css).
   For print / Save as PDF it switches back to its original A4 layout
   (assets/css/booklet-print.css) and runs the booklet's own page-fitting
   script, fitAll() below, copied unchanged from the booklet project. That
   script measures real page boxes, so it runs under the class
   html.is-booklet-print, which turns the A4 layout on before the browser
   lays the page out for printing. Everything it changed is undone after
   printing. */
(function () {
  "use strict";

  // ---- From the booklet project, unchanged --------------------------------
  // Fit each page: scale content up on sparse pages (max 1.3x) and down on overfull ones (min 0.8x).
  function fitAll(){ var out=[]; document.querySelectorAll('.page:not(.cover)').forEach(function(p,i){
    var b=p.querySelector('.body'), inn=p.querySelector('.inner'); var cs=getComputedStyle(b);
    var avail=b.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
    var W=inn.clientWidth, target=avail*0.97;
    var fits=function(z){ inn.style.width=(W/z)+'px'; return inn.offsetHeight*z<=target; };
    var lo=0.78, hi=1.3, z;
    if(fits(hi)){ z=hi; } else if(!fits(lo)){ z=lo; } else { for(var k=0;k<14;k++){ var m=(lo+hi)/2; if(fits(m)) lo=m; else hi=m; } z=lo; }
    inn.style.width=(W/z)+'px';
    inn.querySelectorAll('.fx.one-line').forEach(function(f){ var s=12.5; while(f.scrollWidth>f.clientWidth+1 && s>8){ s-=0.25; f.querySelectorAll('.tok').forEach(function(t){t.style.fontSize=s+'pt';}); f.querySelectorAll('.op').forEach(function(o){o.style.fontSize=(s+1.5)+'pt';}); } var toks=f.querySelectorAll('.tok'); if(toks.length && toks[toks.length-1].offsetTop!==toks[0].offsetTop) document.body.setAttribute('data-oneline-bad','1'); });
    var used=inn.offsetHeight*z;
    if(Math.abs(z-1)<0.015){ inn.style.width=''; z=1; used=inn.offsetHeight; } else { inn.style.transform='scale('+z+')'; }
    out.push((i+1)+':'+Math.round(used/avail*100)+':'+z.toFixed(2));
  }); document.body.setAttribute('data-fill',out.join(','));
    // level page: shrink the contents list until it fits its panel
    var box=document.querySelector('.cover__contents'), list=document.querySelector('.toc2');
    if(box&&list){ var fs=10; while(box.scrollHeight>box.clientHeight+1 && fs>6.5){ fs-=0.25; list.style.fontSize=fs+'pt'; }
      document.body.setAttribute('data-cover', (box.scrollHeight>box.clientHeight+1?'OVERFLOW ':'ok ')+fs+'pt'); } }
  // --------------------------------------------------------------------------

  var root = document.documentElement;
  var booklet = document.getElementById("booklet");
  if (!booklet) return;

  var saved = null; // element -> original style attribute, while printing
  var scrollY = 0;

  function enterPrintLayout() {
    if (saved) return;
    scrollY = window.scrollY;
    saved = [];
    booklet.querySelectorAll(".inner, .inner *, .toc2").forEach(function (el) {
      saved.push([el, el.getAttribute("style")]);
    });
    root.classList.add("is-booklet-print");
    fitAll();
  }

  function leavePrintLayout() {
    if (!saved) return;
    saved.forEach(function (pair) {
      if (pair[1] === null) pair[0].removeAttribute("style");
      else pair[0].setAttribute("style", pair[1]);
    });
    saved = null;
    root.classList.remove("is-booklet-print");
    window.scrollTo(0, scrollY);
  }

  window.addEventListener("beforeprint", enterPrintLayout);
  window.addEventListener("afterprint", leavePrintLayout);
  // Safari fires the print media query change more reliably than the events.
  if (window.matchMedia) {
    var mq = window.matchMedia("print");
    var onChange = function (e) { if (e.matches) enterPrintLayout(); else leavePrintLayout(); };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  document.querySelectorAll("[data-booklet-print]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var go = function () {
        enterPrintLayout();
        window.print();
      };
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(go);
      else go();
    });
  });
})();
