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

The theme ships Japanese and English interface translations. Configure Hugo's
`languages` map and provide translated content using any of Hugo's supported
multilingual content layouts. When the current page has translations, the
header links directly to each corresponding page.

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

A bilingual configuration can define language-specific labels and menus:

```toml
defaultContentLanguage = "ja"

[languages]
  [languages.ja]
    languageCode = "ja-jp"
    languageName = "日本語"
    weight = 1
  [languages.en]
    languageCode = "en-us"
    languageName = "English"
    weight = 2
```

The header includes a light/dark mode switch. The initial mode follows the
visitor's system preference and their selection is saved in the browser. Set
`themeColor` and `themeDarkColor` to customize the browser chrome colors for
each mode.

Lesson pages live below `content/lessons/` and use ordinary front matter:

```yaml
---
title: "Measurement basics"
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

Lessons may be placed directly below `content/lessons/` or grouped into any
number of nested branch bundles. Give each chapter an `_index.md` with its own
`weight`, then use page `weight` values to order lessons within that chapter:

```text
content/lessons/
├── _index.md
├── 01-measurement-basics.md
├── 01-foundations/
│   ├── _index.md
│   └── 02-record-observations.md
└── 02-analysis/
    ├── _index.md
    ├── 01-differences/
    │   ├── _index.md
    │   ├── 99-interpret-sign.md
    │   └── 01-compare-magnitude.md
    └── 03-compare-results.md
```

The theme walks this tree depth first, sorting the children of every level by
`weight`. Only regular lesson pages receive numbers; chapter pages do not.
The same generated sequence drives the course list, sidebar, lesson heading,
and previous/next links, including links that cross chapter boundaries. Do not
add a manual `lesson` parameter.

Every rendered Lesson must also participate in Hugo's page lists. The theme
stops the build with a targeted error if a page is rendered with
`_build.render: always` but excluded using `_build.list: never`, because that
page cannot receive a valid position in the canonical sequence.

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
- `snippet`: include a whole source file or one named region from Hugo assets
  and highlight it as code.

## Source snippets

Keep runnable source authoritative by loading it through the `snippet`
shortcode instead of copying code into Markdown:

```go-html-template
{{</* snippet
  path="snippets/examples/quickstart.py"
  region="quickstart-watch"
  lang="python"
*/>}}
```

Use marker-only lines around a named region. The marker's leading indentation
is removed from selected lines that share it, so a region inside a function
renders without an unwanted leading indent:

```python
def run():
    # --8<-- [start:quickstart-watch]
    result = measure()
    print(result)
    # --8<-- [end:quickstart-watch]
```

Omit `region` to include the whole file; recognized marker lines are never
shown. `path` is resolved only through Hugo's assets namespace. A project can
store files directly below `assets/` or mount an existing source directory
without copying it:

```toml
[module]
  [[module.mounts]]
    source = "assets"
    target = "assets"
  [[module.mounts]]
    source = "examples"
    target = "assets/snippets/examples"
```

When declaring mounts, retain every assets source the project already uses.
The build fails for a missing or unsafe path, an invalid region name, missing
or duplicate markers, or an end marker that precedes its start marker.

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

## Verify the theme

Build the bilingual example and check its localized navigation and lesson
components:

```bash
python3 tests/check_example.py
node tests/check_scripts.js
python3 tests/check_snippet.py
```

Set `HUGO_BIN` to exercise a specific supported Hugo binary, including the
documented minimum version:

```bash
HUGO_BIN=/path/to/hugo-0.92.2 python3 tests/check_example.py
HUGO_BIN=/path/to/hugo-0.92.2 python3 tests/check_snippet.py
```

## License

MIT
