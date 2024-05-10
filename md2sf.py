#!/usr/bin/env python3

import base64
import os
import subprocess
import sys

import click
import mistune
from mistune.util import escape
from spellchecker import SpellChecker


class sf_html_render(mistune.HTMLRenderer):
    # This is a custom mistune extension that will override the default
    # behavior of several inline block element handlers to allow them to emit
    # the HTML needed by Saleforce's Knowledge system
    """Custom renderer for converting Markdown to Salesforce's Knowledge system HTML format."""

    def codespan(self, text):
        """Override for `code` span with specific style."""
        return '<code style="font-size:1em;color:#00f;">' + escape(text) + "</code>"

    def paragraph(self, text):
        """Override for paragraph to maintain standard HTML paragraph tagging."""
        return "<p>" + text + "</p>\n"

    def image(self, url, alt, title=None):
        """Override for images to handle base64 encoding if the image file exists."""
        if os.path.isfile(url):
            with open(url, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                mimetype = self._get_mime_type(url)
                url = f"data:{mimetype};base64,{encoded_string}"
        return f'<img alt="{alt}" title="{title}" src="{url}" style="margin-top: 5px; margin-bottom: 5px;" />'

    def heading(self, text, level, **attrs):
        """Override for headings to convert them into bold text paragraphs as per what SF needs."""
        margin_style = "margin-top: 15px;" if level == 1 else ""
        return f'<p style="{margin_style}"><b>{text}</b></p>\n'

    def block_code(self, code, info=None):
        """Override for `code` blocks to use custom SF page styles."""
        info = info.strip() if info is not None else ""
        return '<pre class="ckeditor_codeblock">' + escape(code) + "</pre>\n"

    def _get_mime_type(self, url):
        """Lazy-load magic here since it's only used once, faster import loading"""
        import puremagic as magic

        return magic.from_file(url, mime=True)


@click.command(
    help="Please supply the path to a KB article in Markdown format to parse and convert")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
@click.option('--lint', is_flag=True, help="Enable linting checks with proselint and spellchecker")
def main(filename, lint):
    """Main function to parse a Markdown file, check it with 'proselint', spellcheck, and save it as HTML if it passes."""
    with open(filename, "r") as sf_kb:
        sf_kb_lines = sf_kb.readlines()

    if lint:
        # Running proselint to check the markdown content for prohibited content
        result = subprocess.run(["proselint", filename], capture_output=True, text=True)
        if result.returncode != 0:
            print("Linting Errors:")
            print(result.stdout)
            sys.exit(1)  # Exit if there are linting errors

        # Spellchecking with pyspellchecker, still needs a better allowlist for 
        # technical industry words (eg: DHCP, br0, LXD and others)
        # spell = SpellChecker()
        # for line_number, line in enumerate(sf_kb_lines, start=1):
        #     words = spell.split_words(line)
        #     misspelled = spell.unknown(words)
        #     if misspelled:
        #         print(f"Possible misspelled word(s) on line {line_number}: {', '.join(misspelled)}")

    markdown = mistune.create_markdown(renderer=sf_html_render())
    html_filename = os.path.splitext(filename)[0] + ".html"
    with open(html_filename, "w") as sf_html:
        sf_html.write(markdown("".join(sf_kb_lines)))


if __name__ == "__main__":
    main()
