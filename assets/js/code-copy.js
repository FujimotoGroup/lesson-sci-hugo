(function () {
  "use strict";

  var blocks = document.querySelectorAll(".prose pre");
  blocks.forEach(function (block) {
    if (block.closest(".expected-output")) return;

    var button = document.createElement("button");
    button.className = "code-copy";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "コードをコピー");

    button.addEventListener("click", function () {
      var code = block.querySelector("code");
      var text = code ? code.innerText : block.innerText;
      navigator.clipboard.writeText(text).then(function () {
        button.textContent = "Copied";
        window.setTimeout(function () { button.textContent = "Copy"; }, 1400);
      });
    });

    var frame = document.createElement("div");
    frame.className = "code-frame";
    block.parentNode.insertBefore(frame, block);
    frame.appendChild(block);
    frame.appendChild(button);
  });
})();
