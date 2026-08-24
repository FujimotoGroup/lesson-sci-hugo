(function () {
  "use strict";

  var labels = document.body.dataset;
  var blocks = document.querySelectorAll(".prose pre");
  blocks.forEach(function (block) {
    if (block.closest(".expected-output")) return;

    var button = document.createElement("button");
    button.className = "code-copy";
    button.type = "button";
    button.textContent = labels.copyLabel;
    button.setAttribute("aria-label", labels.copyAriaLabel);

    button.addEventListener("click", function () {
      var code = block.querySelector("code");
      var text = code ? code.innerText : block.innerText;
      navigator.clipboard.writeText(text).then(function () {
        button.textContent = labels.copiedLabel;
        window.setTimeout(function () { button.textContent = labels.copyLabel; }, 1400);
      });
    });

    var frame = document.createElement("div");
    frame.className = "code-frame";
    block.parentNode.insertBefore(frame, block);
    frame.appendChild(block);
    frame.appendChild(button);
  });
})();
