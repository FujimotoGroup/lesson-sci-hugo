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
/lessons/01-measurement-basics/
```

The minimum supported Hugo version is 0.92.2.

## Use in a site

Add the repository as a theme or Git submodule, then select it in the site
configuration:

```toml
theme = "lesson-sci-hugo"

[params]
homeEyebrow = "Science, one runnable step at a time"
tagline = "Runnable lessons for scientific software"
description = "Learn by predicting, running, and interpreting."
math = true
```

The header includes a light/dark mode switch. The initial mode follows the
visitor's system preference and their selection is saved in the browser. Set
`themeColor` and `themeDarkColor` to customize the browser chrome colors for
each mode.

Lesson pages live below `content/lessons/` and use ordinary front matter:

```yaml
---
title: "Measurement basics"
lesson: 1
weight: 1
duration: "20 min"
toc: true
summary: "Summarize repeated measurements."
prerequisites:
  - "Python basics"
objectives:
  - "Calculate a mean"
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
- `code-link`: link to a mounted or static code file while respecting the
  site's `baseURL` (for example,
  `{{</* code-link path="code/lesson-01.py" label="Open the code" */>}}`).

## Figures, tables, and cross-references

Figures and tables are numbered independently on each page. Give each item an
`id`, then use `xref` to create a link whose text is resolved to labels such as
`図1` or `表2`:

```go-html-template
本文から{{</* xref id="measurement-plot" */>}}を参照します。

{{</* figure
  id="measurement-plot"
  src="images/measurement-plot.svg"
  alt="測定値の分布"
  caption="5回の測定値と平均"
*/>}}

{{</* table id="measurement-values" caption="5回の長さ測定値" */>}}
| 測定回 | 長さ / cm |
| ---: | ---: |
| 1 | 10.1 |
| 2 | 9.9 |
{{</* /table */>}}
```

Use `label` on `xref` only when custom link text is needed. References work
even when they appear before the target figure or table.

The theme intentionally keeps lesson content in Markdown. Project-specific
code execution and validation should remain in the consuming repository's CI.

## License

MIT
