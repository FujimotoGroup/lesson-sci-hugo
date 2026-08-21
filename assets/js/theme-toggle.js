(function () {
  "use strict";

  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  var themeColor = document.querySelector('meta[name="theme-color"]');
  var storageKey = "lesson-sci-color-theme";

  if (!toggle) return;

  function applyTheme(theme) {
    var nextLabel = theme === "dark"
      ? "ライトモードに切り替える"
      : "ダークモードに切り替える";

    root.setAttribute("data-theme", theme);
    root.style.colorScheme = theme;
    toggle.setAttribute("aria-label", nextLabel);
    toggle.setAttribute("title", nextLabel);
    toggle.setAttribute("aria-pressed", String(theme === "dark"));

    if (themeColor) {
      themeColor.content = themeColor.getAttribute("data-" + theme);
    }
  }

  applyTheme(root.getAttribute("data-theme") === "dark" ? "dark" : "light");

  toggle.addEventListener("click", function () {
    var theme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(theme);
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {}
  });
}());
