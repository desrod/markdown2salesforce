#!/usr/bin/env python3

import os
import re
import subprocess
import sys

import click
from markdown_it import MarkdownIt


def markdown_tweaks(markdown_content):
    def code_block_replacer(match):
        code_content = match.group(1)
        return (
            '<pre class="language-markup" '
            'style="background: #efefef; padding: 8px; display: block; border: 1px solid rgb(204, 204, 204); '
            'overflow-x: auto;">'
            f"<code>{code_content}</code></pre>"
        )

    markdown_content = re.sub(
        r"```(?:\n|\r\n?)([\s\S]*?)```", code_block_replacer, markdown_content
    )
    return markdown_content

@click.command(help="Please supply the path to your .md file to convert to HTML")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
@click.option("--lint", is_flag=True, help="Enable linting checks with proselint and spellchecker")
def main(filename, lint):
    with open(filename, "r") as sf_kb:
        sf_kb_lines = sf_kb.readlines()

    if lint:
        result = subprocess.run(["proselint", filename], capture_output=True, text=True)
        if result.returncode != 0:
            print("Linting Errors:")
            print(result.stdout)
            sys.exit(1)

    markdown         = MarkdownIt()
    raw_markdown     = "".join(sf_kb_lines)
    tweaked_markdown = markdown_tweaks(raw_markdown)
    html_content     = markdown.render(tweaked_markdown)
    html_filename    = os.path.splitext(filename)[0] + ".html"

    with open(html_filename, "w") as sf_html:
        sf_html.write(html_content)

if __name__ == "__main__":
    main()
