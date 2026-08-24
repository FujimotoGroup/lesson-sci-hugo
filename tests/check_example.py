#!/usr/bin/env python3
"""Build the example site and check its bilingual rendered contract."""

from __future__ import annotations

import os
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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-sci-hugo-test-") as directory:
        output_root = Path(directory)
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
        subprocess.run(command, check=True)

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

        require(
            japanese_home,
            '<html lang="ja">',
            '<link rel="alternate" hreflang="en" href="http://example.org/en/">',
            'href="/en/" hreflang="en" lang="en"',
            "Lessonを始める",
            'data-copy-label="コピー"',
        )
        require(
            english_home,
            '<html lang="en">',
            '<link rel="alternate" hreflang="ja" href="http://example.org/">',
            'href="/" hreflang="ja" lang="ja"',
            "Start the lessons",
            'data-copy-label="Copy"',
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


if __name__ == "__main__":
    main()
