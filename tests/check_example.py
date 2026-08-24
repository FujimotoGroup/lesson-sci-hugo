#!/usr/bin/env python3
"""Build the example site and check its bilingual rendered contract."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get("HUGO_BIN", "hugo")


def read_page(output_root: Path, relative_path: str) -> str:
    path = output_root / relative_path
    if not path.is_file():
        raise AssertionError(f"expected rendered page: {relative_path}")
    return path.read_text(encoding="utf-8")


def require(page: str, *fragments: str) -> None:
    for fragment in fragments:
        if fragment not in page:
            raise AssertionError(f"rendered page is missing {fragment!r}")


def require_order(page: str, *fragments: str) -> None:
    position = -1
    for fragment in fragments:
        next_position = page.find(fragment, position + 1)
        if next_position < 0:
            raise AssertionError(f"rendered page is missing ordered fragment {fragment!r}")
        position = next_position


def language_switcher(page: str) -> str:
    match = re.search(r'<div class="language-switcher".*?</div>', page)
    if match is None:
        raise AssertionError("rendered page has no language switcher")
    return match.group(0)


def lesson_sidebar(page: str) -> str:
    match = re.search(r'<aside class="lesson-sidebar".*?</aside>', page, re.DOTALL)
    if match is None:
        raise AssertionError("rendered lesson has no lesson sidebar")
    return match.group(0)


def build(
    output_root: Path,
    *,
    disable_english: bool = False,
    source_root: Path | None = None,
) -> None:
    environment = os.environ.copy()
    if disable_english:
        environment["HUGO_DISABLELANGUAGES"] = "en"
    command = [
        HUGO,
        "--source",
        str(source_root or REPOSITORY_ROOT / "exampleSite"),
        "--themesDir",
        str(REPOSITORY_ROOT.parent),
        "--theme",
        REPOSITORY_ROOT.name,
        "--destination",
        str(output_root),
        "--cleanDestinationDir",
        "--panicOnWarning",
    ]
    subprocess.run(command, check=True, env=environment)


def require_excluded_lesson_failure(temporary_root: Path) -> None:
    source_root = temporary_root / "excluded-source"
    shutil.copytree(REPOSITORY_ROOT / "exampleSite", source_root)
    excluded_lesson = source_root / "content/lessons/99-excluded.md"
    excluded_lesson.write_text(
        """---
title: "Excluded lesson"
weight: 99
_build:
  list: never
  render: always
---

This rendered page must not silently receive Lesson 0.
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["HUGO_DISABLELANGUAGES"] = "en"
    command = [
        HUGO,
        "--source",
        str(source_root),
        "--themesDir",
        str(REPOSITORY_ROOT.parent),
        "--theme",
        REPOSITORY_ROOT.name,
        "--destination",
        str(temporary_root / "excluded-output"),
        "--cleanDestinationDir",
        "--panicOnWarning",
    ]
    result = subprocess.run(
        command,
        check=False,
        env=environment,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        raise AssertionError("rendered but unlisted lesson did not fail the build")
    diagnostic = result.stdout + result.stderr
    if "excluded from the canonical lesson sequence" not in diagnostic:
        raise AssertionError("unlisted lesson failure lacks its targeted diagnostic")
    if "error calling add" in diagnostic:
        raise AssertionError("unlisted lesson failure includes a secondary arithmetic error")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-sci-hugo-test-") as directory:
        temporary_root = Path(directory)
        output_root = temporary_root / "rendered"
        build(output_root)

        japanese_home = read_page(output_root, "index.html")
        english_home = read_page(output_root, "en/index.html")
        japanese_lesson = read_page(
            output_root,
            "lessons/01-measurement-basics/index.html",
        )
        english_lesson = read_page(
            output_root,
            "en/lessons/01-measurement-basics/index.html",
        )
        english_lesson_list = read_page(output_root, "en/lessons/index.html")
        english_record_lesson = read_page(
            output_root,
            "en/lessons/01-foundations/02-record-observations/index.html",
        )
        english_compare_lesson = read_page(
            output_root,
            "en/lessons/02-analysis/03-compare-results/index.html",
        )
        english_sign_lesson = read_page(
            output_root,
            "en/lessons/02-analysis/01-differences/99-interpret-sign/index.html",
        )
        english_magnitude_lesson = read_page(
            output_root,
            "en/lessons/02-analysis/01-differences/01-compare-magnitude/index.html",
        )
        japanese_lesson_list = read_page(output_root, "lessons/index.html")
        japanese_sign_lesson = read_page(
            output_root,
            "lessons/02-analysis/01-differences/99-interpret-sign/index.html",
        )

        require(
            japanese_home,
            '<html lang="ja">',
            '<link rel="alternate" hreflang="en" href="http://example.org/en/">',
            'href="/en/" hreflang="en" lang="en"',
            "Lessonを始める",
            'data-copy-label="コピー"',
            'data-copied-label="コピーしました"',
            'data-copy-aria-label="コードをコピー"',
            'aria-label="メインナビゲーション"',
            'data-switch-to-dark="ダークモードに切り替える"',
            'data-switch-to-light="ライトモードに切り替える"',
        )
        require(
            english_home,
            '<html lang="en">',
            '<link rel="alternate" hreflang="ja" href="http://example.org/">',
            'href="/" hreflang="ja" lang="ja"',
            "Start the lessons",
            'data-copy-label="Copy"',
            'data-copied-label="Copied"',
            'data-copy-aria-label="Copy code"',
            'aria-label="Main navigation"',
            'data-switch-to-dark="Switch to dark mode"',
            'data-switch-to-light="Switch to light mode"',
        )
        english_home_cards = re.findall(
            r'<a class="lesson-card" href="([^"]+)">', english_home
        )
        if english_home_cards != [
            "/en/lessons/01-measurement-basics/",
            "/en/lessons/01-foundations/02-record-observations/",
            "/en/lessons/02-analysis/01-differences/99-interpret-sign/",
        ]:
            raise AssertionError(f"homepage lesson cards are not canonical pages: {english_home_cards}")
        require_order(
            english_home,
            '<span class="lesson-card__number">Lesson 1</span>',
            '<span class="lesson-card__number">Lesson 2</span>',
            '<span class="lesson-card__number">Lesson 3</span>',
        )
        if "&lt;no value&gt;" in english_home or "<no value>" in english_home:
            raise AssertionError("homepage renders a missing manual lesson number")
        require(
            japanese_lesson,
            'href="/en/lessons/01-measurement-basics/"',
            "このLessonの到達点",
            "表1",
            "ヒントを見る",
            "期待する出力",
        )
        require(
            english_lesson,
            'href="/lessons/01-measurement-basics/"',
            "Objectives",
            "Table 1",
            "Show hint",
            "Expected output",
        )
        require(
            english_lesson_list,
            '<li class="course-list__chapter">',
            '<h2>Observation foundations</h2>',
            '<h2>Compare results</h2>',
            '<h2>Read differences</h2>',
            '<ol class="course-list__nested">',
        )
        require_order(
            english_lesson_list,
            '<span class="course-list__index">01</span>',
            '<span class="course-list__index">02</span>',
            '<span class="course-list__index">03</span>',
            '<span class="course-list__index">04</span>',
            '<span class="course-list__index">05</span>',
        )
        require_order(
            english_lesson_list,
            "Interpret the sign",
            "Interpret the magnitude",
            "Compare results",
        )
        if english_lesson_list.count('class="course-list__index"') != 5:
            raise AssertionError("lesson index does not contain exactly five numbered pages")
        require(
            english_record_lesson,
            '<span class="lesson-sidebar__chapter-title">Observation foundations</span>',
            '<span class="lesson-sidebar__chapter-title">Compare results</span>',
            '<span class="lesson-number"><span>Lesson 2</span></span>',
            '<a href="/en/lessons/01-foundations/">Observation foundations</a>',
            'class="lesson-pagination__prev" href="/en/lessons/01-measurement-basics/"',
            'class="lesson-pagination__next" href="/en/lessons/02-analysis/01-differences/99-interpret-sign/"',
            'href="/en/lessons/01-foundations/02-record-observations/" aria-current="page"',
        )
        require(
            english_sign_lesson,
            '<span class="lesson-number"><span>Lesson 3</span></span>',
            '<a href="/en/lessons/02-analysis/">Compare results</a>',
            '<a href="/en/lessons/02-analysis/01-differences/">Read differences</a>',
            'class="lesson-pagination__prev" href="/en/lessons/01-foundations/02-record-observations/"',
            'class="lesson-pagination__next" href="/en/lessons/02-analysis/01-differences/01-compare-magnitude/"',
            'href="/en/lessons/02-analysis/01-differences/99-interpret-sign/" aria-current="page"',
        )
        require(
            english_magnitude_lesson,
            '<span class="lesson-number"><span>Lesson 4</span></span>',
            'class="lesson-pagination__prev" href="/en/lessons/02-analysis/01-differences/99-interpret-sign/"',
            'class="lesson-pagination__next" href="/en/lessons/02-analysis/03-compare-results/"',
        )
        require(
            english_compare_lesson,
            '<span class="lesson-number"><span>Lesson 5</span></span>',
            'class="lesson-pagination__prev" href="/en/lessons/02-analysis/01-differences/01-compare-magnitude/"',
        )
        if 'class="lesson-pagination__next"' in english_compare_lesson:
            raise AssertionError("last lesson renders a next link")
        require_order(
            japanese_lesson_list,
            '<span class="course-list__index">01</span>',
            '<span class="course-list__index">02</span>',
            '<span class="course-list__index">03</span>',
            '<span class="course-list__index">04</span>',
            '<span class="course-list__index">05</span>',
        )
        require(
            japanese_sign_lesson,
            '<span class="lesson-sidebar__chapter-title">差を読む</span>',
            '<span class="lesson-number"><span>Lesson 3</span></span>',
            '<a href="/lessons/02-analysis/">比較する</a>',
            '<a href="/lessons/02-analysis/01-differences/">差を読む</a>',
            'class="lesson-pagination__next" href="/lessons/02-analysis/01-differences/01-compare-magnitude/"',
        )
        for sidebar in (
            lesson_sidebar(english_sign_lesson),
            lesson_sidebar(japanese_sign_lesson),
        ):
            require_order(
                sidebar,
                "<span>01</span>",
                "<span>02</span>",
                "<span>03</span>",
                "<span>04</span>",
                "<span>05</span>",
            )
            if sidebar.count('<li class="lesson-sidebar__lesson">') != 5:
                raise AssertionError("sidebar does not contain exactly five lessons")

        japanese_switcher = language_switcher(japanese_lesson)
        english_switcher = language_switcher(english_lesson)
        require(
            japanese_switcher,
            'aria-label="言語"',
            'href="/lessons/01-measurement-basics/" hreflang="ja" lang="ja" aria-label="日本語" aria-current="page"',
            'href="/en/lessons/01-measurement-basics/" hreflang="en" lang="en" aria-label="English"',
        )
        require(
            english_switcher,
            'aria-label="Language"',
            'href="/lessons/01-measurement-basics/" hreflang="ja" lang="ja" aria-label="日本語"',
            'href="/en/lessons/01-measurement-basics/" hreflang="en" lang="en" aria-label="English" aria-current="page"',
        )
        if japanese_switcher.count("<a ") != 2:
            raise AssertionError("Japanese lesson switcher has unrelated links")
        if english_switcher.count("<a ") != 2:
            raise AssertionError("English lesson switcher has unrelated links")

        require(
            japanese_lesson,
            'class="site-nav__repo" href="https://github.com/FujimotoGroup/lesson-sci-hugo" aria-label="リポジトリ"',
            '<span class="language-switcher__short" aria-hidden="true">JA</span>',
        )
        require(
            english_lesson,
            'class="site-nav__repo" href="https://github.com/FujimotoGroup/lesson-sci-hugo" aria-label="Repository"',
            '<span class="language-switcher__short" aria-hidden="true">EN</span>',
        )

        code_copy_script = (REPOSITORY_ROOT / "assets/js/code-copy.js").read_text(
            encoding="utf-8",
        )
        theme_toggle_script = (
            REPOSITORY_ROOT / "assets/js/theme-toggle.js"
        ).read_text(encoding="utf-8")
        require(
            code_copy_script,
            "labels.copyLabel",
            "labels.copiedLabel",
            "labels.copyAriaLabel",
        )
        require(
            theme_toggle_script,
            'toggle.getAttribute("data-switch-to-light")',
            'toggle.getAttribute("data-switch-to-dark")',
            'toggle.setAttribute("aria-label", nextLabel)',
        )

        japanese_only_root = output_root / "ja-only"
        build(japanese_only_root, disable_english=True)
        japanese_only_home = read_page(japanese_only_root, "index.html")
        if 'class="language-switcher"' in japanese_only_home:
            raise AssertionError("single-language page renders a language switcher")
        if 'hreflang="en"' in japanese_only_home:
            raise AssertionError("single-language page links to disabled English content")

        lesson_sources = [REPOSITORY_ROOT / "archetypes/lesson.md"]
        lesson_sources.extend(
            (REPOSITORY_ROOT / "exampleSite/content/lessons").rglob("*.md")
        )
        for source in lesson_sources:
            if re.search(r"^lesson\s*:", source.read_text(encoding="utf-8"), re.MULTILINE):
                raise AssertionError(f"manual lesson number remains in {source}")

        require_excluded_lesson_failure(temporary_root)


if __name__ == "__main__":
    main()
