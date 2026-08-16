# lesson-sci-hugo

`lesson-sci-hugo` is a Hugo theme for progressive, code-centered science
lessons. It is derived from the in-house Fujimoto Group Hugo theme and keeps
its Japanese typography, blue palette, mathematical typesetting, and compact
table-of-contents treatment.

## Preview the example

```bash
hugo server --source exampleSite --themesDir ../..
```

Then open the URL printed by Hugo and navigate to:

```text
/lessons/01-first-hamiltonian/
```

The minimum supported Hugo version is 0.92.2.

## Use in a site

Add the repository as a theme or Git submodule, then select it in the site
configuration:

```toml
theme = "lesson-sci-hugo"

[params]
tagline = "Runnable lessons for scientific software"
description = "Learn by predicting, running, and interpreting."
math = true
```

Lesson pages live below `content/lessons/` and use ordinary front matter:

```yaml
---
title: "First Hamiltonian"
lesson: 1
weight: 1
duration: "20 min"
toc: true
summary: "Build and inspect the smallest model."
prerequisites:
  - "Python basics"
objectives:
  - "Construct a model"
  - "Interpret its output"
---
```

## Lesson shortcodes

- `goal`: state the result learners should reach.
- `predict`: ask learners to predict an outcome before running code.
- `exercise`: provide a bounded modification task.
- `hint`: add a collapsible hint.
- `solution`: add a collapsible solution.
- `expected-output`: distinguish terminal output from source code.

The theme intentionally keeps lesson content in Markdown. Project-specific
code execution and validation should remain in the consuming repository's CI.

## License

MIT
