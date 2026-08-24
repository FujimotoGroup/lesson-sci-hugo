#!/usr/bin/env python3
"""Exercise the snippet shortcode's success and fail-closed contracts."""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get("HUGO_BIN", "hugo")
LESSON_PATH = Path("content/lessons/01-measurement-basics.md")


def command(source_root: Path, output_root: Path) -> list[str]:
    return [
        HUGO,
        "--source",
        str(source_root),
        "--themesDir",
        str(REPOSITORY_ROOT.parent),
        "--theme",
        REPOSITORY_ROOT.name,
        "--destination",
        str(output_root),
        "--cleanDestinationDir",
        "--panicOnWarning",
    ]


def build(source_root: Path, output_root: Path) -> None:
    subprocess.run(command(source_root, output_root), check=True)


def snippet_code(page: str, *, occurrence: int = 0) -> tuple[str, str]:
    matches = list(
        re.finditer(
            r'<div class="source-snippet"[^>]*>.*?<code[^>]*>(.*?)</code>',
            page,
            re.DOTALL,
        )
    )
    if len(matches) <= occurrence:
        raise AssertionError(f"rendered page has no snippet occurrence {occurrence}")
    match = matches[occurrence]
    fragment = match.group(0)
    code = html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))
    return fragment, code


def copied_source(temporary_root: Path, name: str) -> Path:
    source_root = temporary_root / name / "source"
    shutil.copytree(REPOSITORY_ROOT / "exampleSite", source_root)
    return source_root


def append_shortcode(source_root: Path, shortcode: str) -> None:
    lesson = source_root / LESSON_PATH
    lesson.write_text(
        lesson.read_text(encoding="utf-8") + f"\n\n{shortcode}\n",
        encoding="utf-8",
    )


def require_failure(
    temporary_root: Path,
    name: str,
    shortcode: str,
    diagnostic: str,
    *,
    asset: str | None = None,
) -> None:
    source_root = copied_source(temporary_root, name)
    append_shortcode(source_root, shortcode)
    if asset is not None:
        asset_path = source_root / f"assets/snippets/{name}.py"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_text(asset, encoding="utf-8")
    environment = os.environ.copy()
    environment["HUGO_DISABLELANGUAGES"] = "en"
    result = subprocess.run(
        command(source_root, temporary_root / name / "output"),
        check=False,
        env=environment,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        raise AssertionError(f"invalid snippet case {name!r} did not fail")
    output = result.stdout + result.stderr
    if diagnostic not in output:
        raise AssertionError(f"invalid snippet case {name!r} lacks {diagnostic!r}")
    if "error calling" in output:
        raise AssertionError(f"invalid snippet case {name!r} has a secondary template error")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-sci-snippet-test-") as directory:
        temporary_root = Path(directory)
        output_root = temporary_root / "example-output"
        build(REPOSITORY_ROOT / "exampleSite", output_root)

        expected_region = (
            "measurements = [10.1, 9.9, 10.0, 10.2, 9.8]\n"
            "mean = fmean(measurements)\n"
            'print(f"mean: {mean:.2f} cm")\n'
        )
        for relative_path in (
            "lessons/01-measurement-basics/index.html",
            "en/lessons/01-measurement-basics/index.html",
        ):
            page = (output_root / relative_path).read_text(encoding="utf-8")
            fragment, code = snippet_code(page)
            if 'data-snippet-path="snippets/measurement.py"' not in fragment:
                raise AssertionError("snippet omits its source path metadata")
            if 'data-snippet-region="measurement-values"' not in fragment:
                raise AssertionError("snippet omits its region metadata")
            if code != expected_region:
                raise AssertionError(f"region was not extracted and dedented: {code!r}")
            if "--8<--" in fragment or "summarize_measurements" in fragment:
                raise AssertionError("region snippet leaked markers or surrounding code")

        full_source = copied_source(temporary_root, "whole-file")
        append_shortcode(
            full_source,
            '{{< snippet path="snippets/measurement.py" lang="python" >}}',
        )
        full_output = temporary_root / "whole-file" / "output"
        build(full_source, full_output)
        full_page = (full_output / "lessons/01-measurement-basics/index.html").read_text(
            encoding="utf-8"
        )
        full_fragment, full_code = snippet_code(full_page, occurrence=1)
        if "def summarize_measurements()" not in full_code or "return mean" not in full_code:
            raise AssertionError("whole-file snippet omitted source content")
        if "--8<--" in full_fragment:
            raise AssertionError("whole-file snippet leaked region markers")
        if "data-snippet-region" in full_fragment:
            raise AssertionError("whole-file snippet claims a region")

        require_failure(
            temporary_root,
            "missing-path",
            "{{< snippet >}}",
            "requires a path",
        )
        require_failure(
            temporary_root,
            "unsafe-path",
            '{{< snippet path="../config.toml" >}}',
            "must be a relative asset path",
        )
        require_failure(
            temporary_root,
            "missing-resource",
            '{{< snippet path="snippets/missing.py" >}}',
            "was not found in Hugo assets",
        )
        require_failure(
            temporary_root,
            "invalid-region",
            '{{< snippet path="snippets/measurement.py" region="bad.*" >}}',
            "must match [A-Za-z0-9][A-Za-z0-9._-]*",
        )
        require_failure(
            temporary_root,
            "missing-region",
            '{{< snippet path="snippets/measurement.py" region="absent" >}}',
            "requires exactly one start marker and one end marker",
        )
        require_failure(
            temporary_root,
            "duplicate-region",
            '{{< snippet path="snippets/duplicate-region.py" region="target" >}}',
            "requires exactly one start marker and one end marker",
            asset=(
                "# --8<-- [start:target]\nfirst = 1\n# --8<-- [end:target]\n"
                "# --8<-- [start:target]\nsecond = 2\n# --8<-- [end:target]\n"
            ),
        )
        require_failure(
            temporary_root,
            "reversed-region",
            '{{< snippet path="snippets/reversed-region.py" region="target" >}}',
            "has its end marker before its start marker",
            asset=(
                "# --8<-- [end:target]\nvalue = 1\n"
                "# --8<-- [start:target]\n"
            ),
        )


if __name__ == "__main__":
    main()
