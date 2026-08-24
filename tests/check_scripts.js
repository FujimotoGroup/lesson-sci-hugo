"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const repositoryRoot = path.resolve(__dirname, "..");

function runScript(relativePath, context) {
  const source = fs.readFileSync(path.join(repositoryRoot, relativePath), "utf8");
  vm.runInNewContext(source, context, { filename: relativePath });
}

function checkThemeToggle() {
  const rootAttributes = { "data-theme": "light" };
  const toggleAttributes = {
    "data-switch-to-dark": "Switch to dark",
    "data-switch-to-light": "Switch to light",
  };
  let clickHandler;
  const root = {
    style: {},
    getAttribute(name) { return rootAttributes[name]; },
    setAttribute(name, value) { rootAttributes[name] = value; },
  };
  const toggle = {
    getAttribute(name) { return toggleAttributes[name]; },
    setAttribute(name, value) { toggleAttributes[name] = value; },
    addEventListener(event, handler) {
      if (event === "click") clickHandler = handler;
    },
  };
  const themeColor = {
    content: "",
    getAttribute(name) { return name === "data-dark" ? "#000" : "#fff"; },
  };
  const context = {
    document: {
      documentElement: root,
      querySelector(selector) {
        return selector === "[data-theme-toggle]" ? toggle : themeColor;
      },
    },
    localStorage: { getItem() { return null; }, setItem() {} },
    window: { matchMedia() { return { matches: false }; } },
  };

  runScript("assets/js/theme-toggle.js", context);
  assert.equal(toggleAttributes["aria-label"], "Switch to dark");
  assert.equal(toggleAttributes.title, "Switch to dark");
  assert.equal(toggleAttributes["aria-pressed"], "false");

  clickHandler();
  assert.equal(rootAttributes["data-theme"], "dark");
  assert.equal(toggleAttributes["aria-label"], "Switch to light");
  assert.equal(toggleAttributes.title, "Switch to light");
  assert.equal(toggleAttributes["aria-pressed"], "true");
}

async function checkCodeCopy() {
  let copyButton;
  let clickHandler;
  let resetLabel;
  let clipboardText;
  const code = { innerText: "print('hello')" };
  const block = {
    innerText: code.innerText,
    closest() { return null; },
    querySelector() { return code; },
    parentNode: { insertBefore() {} },
  };
  const frame = { appendChild() {} };
  const context = {
    document: {
      body: {
        dataset: {
          copyLabel: "Copy",
          copiedLabel: "Copied",
          copyAriaLabel: "Copy code",
        },
      },
      querySelectorAll() { return [block]; },
      createElement(name) {
        if (name === "div") return frame;
        copyButton = {
          setAttribute(attribute, value) { this[attribute] = value; },
          addEventListener(event, handler) {
            if (event === "click") clickHandler = handler;
          },
        };
        return copyButton;
      },
    },
    navigator: {
      clipboard: {
        writeText(value) {
          clipboardText = value;
          return Promise.resolve();
        },
      },
    },
    window: { setTimeout(handler) { resetLabel = handler; } },
  };

  runScript("assets/js/code-copy.js", context);
  assert.equal(copyButton.textContent, "Copy");
  assert.equal(copyButton["aria-label"], "Copy code");

  clickHandler();
  await Promise.resolve();
  assert.equal(clipboardText, code.innerText);
  assert.equal(copyButton.textContent, "Copied");

  resetLabel();
  assert.equal(copyButton.textContent, "Copy");
}

checkThemeToggle();
checkCodeCopy().catch((error) => {
  process.nextTick(() => { throw error; });
});
