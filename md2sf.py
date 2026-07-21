#!/usr/bin/env python3

import os
import subprocess
import sys

import click
from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml

SF_PRE_STYLE = (
    "background: #efefef; padding: 8px; display: block; "
    "border: 1px solid rgb(204, 204, 204); overflow-x: auto;"
)


def render_fence_sf(self, tokens, idx, options, env):
    """Render fenced code blocks (``` blocks) with Salesforce-friendly styling.

    Handles fences with or without a language info string, and escapes the
    code content properly so it renders instead of being interpreted as HTML.
    """
    token = tokens[idx]
    return (
        f'<pre class="language-markup" style="{SF_PRE_STYLE}">'
        f"<code>{escapeHtml(token.content)}</code></pre>\n"
    )


@click.command(help="Please supply the path to your .md file to convert to HTML")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
@click.option(
    "--lint", is_flag=True, help="Enable linting checks with proselint and spellchecker"
)
def main(filename, lint):
    with open(filename, "r") as sf_kb:
        raw_markdown = sf_kb.read()

    if lint:
        result = subprocess.run(["proselint", filename], capture_output=True, text=True)
        if result.returncode != 0:
            print("Linting Errors:")
            print(result.stdout)
            sys.exit(1)

    markdown = MarkdownIt()
    markdown.add_render_rule("fence", render_fence_sf)

    html_content = markdown.render(raw_markdown)
    html_filename = os.path.splitext(filename)[0] + ".html"

    with open(html_filename, "w") as sf_html:
        sf_html.write(html_content)


if __name__ == "__main__":
    main()
