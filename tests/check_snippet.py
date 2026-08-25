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
    asset: str | bytes | None = None,
) -> None:
    source_root = copied_source(temporary_root, name)
    append_shortcode(source_root, shortcode)
    if asset is not None:
        asset_path = source_root / f"assets/snippets/{name}.py"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(asset, bytes):
            asset_path.write_bytes(asset)
        else:
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
            '{{< snippet path="snippets/measurement.py" >}}',
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
        if 'class="language-text"' not in full_fragment:
            raise AssertionError("snippet without lang did not default to text")

        literal_source = copied_source(temporary_root, "literal-dot")
        literal_asset = literal_source / "assets/snippets/literal-dot.py"
        literal_asset.write_bytes(
            b"// --8<-- [start:targetXname]\r\nwrong = True\r\n"
            b"// --8<-- [end:targetXname]\r\n"
            b"\t// --8<-- [start:target.name]\r\n\tright = True\r\n"
            b"\t// --8<-- [end:target.name]\r\n"
        )
        append_shortcode(
            literal_source,
            '{{< snippet path="snippets/literal-dot.py" region="target.name" lang="python" >}}',
        )
        literal_output = temporary_root / "literal-dot" / "output"
        build(literal_source, literal_output)
        literal_page = (
            literal_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        _, literal_code = snippet_code(literal_page, occurrence=1)
        if literal_code != "right = True\n":
            raise AssertionError(f"dotted region did not match literally: {literal_code!r}")

        embedded_source = copied_source(temporary_root, "embedded-marker")
        embedded_asset = embedded_source / "assets/snippets/embedded-marker.py"
        embedded_code = (
            'start_text = "--8<-- [start:not-a-marker]"\n'
            "middle = True\n"
            'end_text = "--8<-- [end:not-a-marker]"\n'
        )
        embedded_asset.write_text(embedded_code, encoding="utf-8")
        append_shortcode(
            embedded_source,
            '{{< snippet path="snippets/embedded-marker.py" lang="python" >}}',
        )
        embedded_output = temporary_root / "embedded-marker" / "output"
        build(embedded_source, embedded_output)
        embedded_page = (
            embedded_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        _, rendered_embedded_code = snippet_code(embedded_page, occurrence=1)
        if rendered_embedded_code != embedded_code:
            raise AssertionError(
                "whole-file rendering changed marker-shaped source text: "
                f"{rendered_embedded_code!r}"
            )

        boundary_source = copied_source(temporary_root, "marker-boundary-strings")
        boundary_asset = boundary_source / "assets/snippets/marker-boundary-strings.py"
        boundary_asset.write_text(
            'before = "    # --8<-- [start:target]"\n'
            "    # --8<-- [start:target]\n"
            '    inside = "    # --8<-- [end:target]"\n'
            "    must_remain = True\n"
            "    # --8<-- [end:target]\n",
            encoding="utf-8",
        )
        append_shortcode(
            boundary_source,
            '{{< snippet path="snippets/marker-boundary-strings.py" region="target" lang="python" >}}',
        )
        boundary_output = temporary_root / "marker-boundary-strings" / "output"
        build(boundary_source, boundary_output)
        boundary_page = (
            boundary_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        _, boundary_code = snippet_code(boundary_page, occurrence=1)
        expected_boundary_code = (
            'inside = "    # --8<-- [end:target]"\n'
            "must_remain = True\n"
        )
        if boundary_code != expected_boundary_code:
            raise AssertionError(
                f"marker-shaped strings changed extraction boundaries: {boundary_code!r}"
            )

        wrapper_source = copied_source(temporary_root, "marker-wrappers")
        wrapper_asset = wrapper_source / "assets/snippets/marker-wrappers.txt"
        wrappers = (
            ("bare", "", ""),
            ("hash", "# ", ""),
            ("slash", "// ", ""),
            ("semicolon", "; ", ""),
            ("dash", "-- ", ""),
            ("percent", "% ", ""),
            ("bang", "! ", ""),
            ("quote", "' ", ""),
            ("block", "/* ", " */"),
            ("html", "<!-- ", " -->"),
        )
        wrapper_lines: list[str] = []
        for name, prefix, suffix in wrappers:
            wrapper_lines.extend(
                (
                    f"{prefix}--8<-- [start:{name}]{suffix}",
                    f"{name}_value = True",
                    f"{prefix}--8<-- [end:{name}]{suffix}",
                )
            )
            append_shortcode(
                wrapper_source,
                f'{{{{< snippet path="snippets/marker-wrappers.txt" region="{name}" >}}}}',
            )
        wrapper_asset.write_text("\n".join(wrapper_lines) + "\n", encoding="utf-8")
        wrapper_output = temporary_root / "marker-wrappers" / "output"
        build(wrapper_source, wrapper_output)
        wrapper_page = (
            wrapper_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        for index, (name, _, _) in enumerate(wrappers, start=1):
            _, wrapper_code = snippet_code(wrapper_page, occurrence=index)
            if wrapper_code != f"{name}_value = True\n":
                raise AssertionError(f"documented marker wrapper {name!r} failed")

        malformed_source = copied_source(temporary_root, "malformed-wrappers")
        malformed_asset = malformed_source / "assets/snippets/malformed-wrappers.txt"
        malformed_code = (
            "/* --8<-- [start:mixed] -->\n"
            "mixed_value = True\n"
            "/* --8<-- [end:mixed] -->\n"
            "/* --8<-- [start:missing-c-close]\n"
            "--8<-- [end:stray-c-close] */\n"
            "<!-- --8<-- [start:missing-html-close]\n"
            "--8<-- [end:stray-html-close] -->\n"
        )
        malformed_asset.write_text(malformed_code, encoding="utf-8")
        append_shortcode(
            malformed_source,
            '{{< snippet path="snippets/malformed-wrappers.txt" >}}',
        )
        malformed_output = temporary_root / "malformed-wrappers" / "output"
        build(malformed_source, malformed_output)
        malformed_page = (
            malformed_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        _, rendered_malformed_code = snippet_code(malformed_page, occurrence=1)
        if rendered_malformed_code != malformed_code:
            raise AssertionError("whole-file rendering removed malformed wrapper text")

        escaping_source = copied_source(temporary_root, "escaping")
        escaping_asset = escaping_source / "assets/snippets/escaping.txt"
        escaping_code = (
            '<script>alert("snippet")</script>\n'
            '</code><img src=x onerror="alert(1)">\n'
            'symbols = "& \' quoted"\n'
        )
        escaping_asset.write_text(escaping_code, encoding="utf-8")
        append_shortcode(
            escaping_source,
            '{{< snippet path="snippets/escaping.txt" lang="text" >}}',
        )
        escaping_output = temporary_root / "escaping" / "output"
        build(escaping_source, escaping_output)
        escaping_page = (
            escaping_output / "lessons/01-measurement-basics/index.html"
        ).read_text(encoding="utf-8")
        escaping_fragment, rendered_escaping_code = snippet_code(
            escaping_page, occurrence=1
        )
        if rendered_escaping_code != escaping_code:
            raise AssertionError("highlighting changed HTML-significant source text")
        if "<script>" in escaping_fragment or "<img " in escaping_fragment:
            raise AssertionError("highlighted source created an executable HTML element")

        mounted_source = copied_source(temporary_root, "mounted-source")
        mounted_directory = mounted_source / "mounted-examples"
        mounted_directory.mkdir()
        mounted_asset = mounted_directory / "authoritative.py"
        mounted_asset.write_text("mounted_value = 1\n", encoding="utf-8")
        config = mounted_source / "config.toml"
        config.write_text(
            config.read_text(encoding="utf-8")
            + """

[module]
  [[module.mounts]]
    source = "assets"
    target = "assets"
  [[module.mounts]]
    source = "mounted-examples"
    target = "assets/snippets/mounted"
""",
            encoding="utf-8",
        )
        mounted_shortcode = (
            '{{< snippet path="snippets/mounted/authoritative.py" lang="python" >}}'
        )
        append_shortcode(mounted_source, mounted_shortcode)
        mounted_lesson = mounted_source / LESSON_PATH
        mounted_markdown = mounted_lesson.read_text(encoding="utf-8")
        mounted_output = temporary_root / "mounted-source" / "output"
        build(mounted_source, mounted_output)
        mounted_page_path = mounted_output / "lessons/01-measurement-basics/index.html"
        _, mounted_code = snippet_code(
            mounted_page_path.read_text(encoding="utf-8"), occurrence=1
        )
        if mounted_code != "mounted_value = 1\n":
            raise AssertionError("explicit Hugo assets mount did not resolve")
        mounted_asset.write_text("mounted_value = 2\n", encoding="utf-8")
        build(mounted_source, mounted_output)
        _, rebuilt_mounted_code = snippet_code(
            mounted_page_path.read_text(encoding="utf-8"), occurrence=1
        )
        if rebuilt_mounted_code != "mounted_value = 2\n":
            raise AssertionError("rebuilt snippet did not follow its mounted source")
        if mounted_lesson.read_text(encoding="utf-8") != mounted_markdown:
            raise AssertionError("mounted-source rebuild unexpectedly changed Markdown")

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
        for name, unsafe_path in (
            ("absolute-path", "/snippets/measurement.py"),
            ("leading-dot-segment", "./snippets/measurement.py"),
            ("nested-dot-segment", "snippets/./measurement.py"),
            ("backslash-path", "snippets\\measurement.py"),
        ):
            require_failure(
                temporary_root,
                name,
                f'{{{{< snippet path="{unsafe_path}" >}}}}',
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
            "unsafe-language",
            '{{< snippet path="snippets/measurement.py" lang=`text" onmouseover="alert(1)` >}}',
            "must match [A-Za-z0-9][A-Za-z0-9_+.-]*",
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
            "confusable-dot-region",
            '{{< snippet path="snippets/confusable-dot-region.py" region="target.name" >}}',
            "requires exactly one start marker and one end marker",
            asset=(
                "# --8<-- [start:targetXname]\nwrong = True\n"
                "# --8<-- [end:targetXname]\n"
            ),
        )
        require_failure(
            temporary_root,
            "inline-region-marker",
            '{{< snippet path="snippets/inline-region-marker.py" region="target" >}}',
            "requires exactly one start marker and one end marker",
            asset=(
                'start_text = "--8<-- [start:target]"\nvalue = True\n'
                'end_text = "--8<-- [end:target]"\n'
            ),
        )
        require_failure(
            temporary_root,
            "binary-source",
            '{{< snippet path="snippets/binary-source.py" >}}',
            "contains a NUL byte",
            asset=b"value = 1\x00\x01\n",
        )
        require_failure(
            temporary_root,
            "oversized-source",
            '{{< snippet path="snippets/oversized-source.py" >}}',
            "exceeds the 262144-byte output limit",
            asset="x" * 262145,
        )
        for name, marker_source in (
            (
                "mixed-wrapper",
                "/* --8<-- [start:target] -->\nvalue = True\n"
                "/* --8<-- [end:target] -->\n",
            ),
            (
                "missing-c-close",
                "/* --8<-- [start:target]\nvalue = True\n"
                "/* --8<-- [end:target]\n",
            ),
            (
                "stray-c-close",
                "--8<-- [start:target] */\nvalue = True\n"
                "--8<-- [end:target] */\n",
            ),
            (
                "missing-html-close",
                "<!-- --8<-- [start:target]\nvalue = True\n"
                "<!-- --8<-- [end:target]\n",
            ),
            (
                "stray-html-close",
                "--8<-- [start:target] -->\nvalue = True\n"
                "--8<-- [end:target] -->\n",
            ),
        ):
            require_failure(
                temporary_root,
                name,
                f'{{{{< snippet path="snippets/{name}.py" region="target" >}}}}',
                "requires exactly one start marker and one end marker",
                asset=marker_source,
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
