(function () {
  "use strict";

  document.querySelectorAll("[data-cross-reference]").forEach(function (link) {
    var target = document.getElementById(link.getAttribute("data-cross-reference"));
    var label = target && target.getAttribute("data-reference-label");
    if (label) link.textContent = label;
  });
}());

(function () {
  "use strict";

  // Sites may declare named signals as {"name": ["identifier-prefix", ...]}.
  // Every identifier inside lesson code that starts with a declared prefix is
  // wrapped in <span class="signal signal--name"> so CSS can color it.
  var raw = document.body && document.body.getAttribute("data-signals");
  if (!raw) return;

  var signals;
  try {
    signals = JSON.parse(raw);
  } catch (error) {
    return;
  }

  var prefixes = [];
  Object.keys(signals).forEach(function (name) {
    if (!/^[a-z][a-z0-9-]*$/.test(name) || !Array.isArray(signals[name])) return;
    signals[name].forEach(function (prefix) {
      if (typeof prefix === "string" && /^[A-Za-z_][A-Za-z0-9_]*$/.test(prefix)) {
        prefixes.push({ prefix: prefix, name: name });
      }
    });
  });
  if (!prefixes.length) return;

  // Longer prefixes first so "output_adjoint" wins over a shorter "output".
  prefixes.sort(function (a, b) { return b.prefix.length - a.prefix.length; });
  var pattern = new RegExp(
    "\\b(" + prefixes.map(function (item) { return item.prefix; }).join("|") + ")\\w*",
    "g"
  );

  function signalName(identifier) {
    for (var i = 0; i < prefixes.length; i += 1) {
      if (identifier.indexOf(prefixes[i].prefix) === 0) return prefixes[i].name;
    }
    return null;
  }

  function mark(textNode) {
    var text = textNode.nodeValue;
    pattern.lastIndex = 0;
    if (!pattern.test(text)) return;
    pattern.lastIndex = 0;

    var fragment = document.createDocumentFragment();
    var cursor = 0;
    var match;
    while ((match = pattern.exec(text)) !== null) {
      var name = signalName(match[0]);
      if (!name) continue;
      if (match.index > cursor) {
        fragment.appendChild(document.createTextNode(text.slice(cursor, match.index)));
      }
      var span = document.createElement("span");
      span.className = "signal signal--" + name;
      span.textContent = match[0];
      fragment.appendChild(span);
      cursor = match.index + match[0].length;
    }
    if (cursor < text.length) {
      fragment.appendChild(document.createTextNode(text.slice(cursor)));
    }
    textNode.parentNode.replaceChild(fragment, textNode);
  }

  document.querySelectorAll(".prose code").forEach(function (code) {
    var walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(mark);
  });
}());
