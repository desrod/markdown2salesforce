#!/usr/bin/env python3


import os

import click
import mistune
from mistune.scanner import escape


class sf_html_render(mistune.HTMLRenderer):
    # This is a custom mistune extension that will override the default
    # behavior of several inline block element handlers to allow them to emit
    # the HTML needed by Saleforce's Knowledge system
    def codespan(self, text):
        """override the default `code` block handler"""
        return '<code style="font-size:1em;color:#00f;">' + escape(text) + "</code>"

    def paragraph(self, text):
        """override the default paragraph handler"""
        return "<p>" + text + "</p>\n"

    def block_code(self, code, info=None):
        """inject the correct `code` block handlers for styling"""
        html = '<pre class="ckeditor_codeblock"'
        if info is not None:
            info = info.strip()
        return html + ">" + escape(code) + "</pre>\n"


@click.command(help="Plese supply the path to a KB article in Markdown format to parse")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
def main(filename):

    with open(filename) as sf_kb:
        sf_kb_file = sf_kb.read()

    markdown = mistune.create_markdown(renderer=sf_html_render())

    sf_html = open(os.path.splitext(filename)[0] + ".html", "w")
    sf_html.write(markdown(sf_kb_file))


if __name__ == "__main__":
    main()
