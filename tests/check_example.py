#!/usr/bin/env python3
"""Build the example site and check its bilingual rendered contract."""

from __future__ import annotations

import os
import re
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


def build(output_root: Path, *, disable_english: bool = False) -> None:
    environment = os.environ.copy()
    if disable_english:
        environment["HUGO_DISABLELANGUAGES"] = "en"
    command = [
        HUGO,
        "--source",
        str(REPOSITORY_ROOT / "exampleSite"),
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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-sci-hugo-test-") as directory:
        output_root = Path(directory)
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
            '<ol class="course-list__nested">',
        )
        require_order(
            english_lesson_list,
            '<span class="course-list__index">01</span>',
            '<span class="course-list__index">02</span>',
            '<span class="course-list__index">03</span>',
        )
        if english_lesson_list.count('class="course-list__index"') != 3:
            raise AssertionError("lesson index does not contain exactly three numbered pages")
        require(
            english_record_lesson,
            '<span class="lesson-sidebar__chapter-title">Observation foundations</span>',
            '<span class="lesson-sidebar__chapter-title">Compare results</span>',
            '<span class="lesson-number"><span>Lesson 2</span></span>',
            '<a href="/en/lessons/01-foundations/">Observation foundations</a>',
            'class="lesson-pagination__prev" href="/en/lessons/01-measurement-basics/"',
            'class="lesson-pagination__next" href="/en/lessons/02-analysis/03-compare-results/"',
            'href="/en/lessons/01-foundations/02-record-observations/" aria-current="page"',
        )
        require(
            english_compare_lesson,
            '<span class="lesson-number"><span>Lesson 3</span></span>',
            '<a href="/en/lessons/02-analysis/">Compare results</a>',
            'class="lesson-pagination__prev" href="/en/lessons/01-foundations/02-record-observations/"',
        )
        if 'class="lesson-pagination__next"' in english_compare_lesson:
            raise AssertionError("last nested lesson renders a next link")

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


if __name__ == "__main__":
    main()
