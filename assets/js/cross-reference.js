(function () {
  "use strict";

  document.querySelectorAll("[data-cross-reference]").forEach(function (link) {
    var target = document.getElementById(link.getAttribute("data-cross-reference"));
    var label = target && target.getAttribute("data-reference-label");
    if (label) link.textContent = label;
  });
}());
