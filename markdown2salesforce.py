#!/usr/bin/env python3


import os

import click
import mistune
from mistune.scanner import escape


###############################################
class MyRenderer(mistune.HTMLRenderer):
    def codespan(self, text):
        return '<code style="font-size:1em;color:#00f;">' + escape(text) + "</code>"

    def paragraph(self, text):
        return "<p>" + text + "</p>\n"

    def block_code(self, code, info=None):
        html = '<pre class="ckeditor_codeblock"'
        if info is not None:
            info = info.strip()
        return html + ">" + escape(code) + "</pre>\n"


@click.command(help="Plese supply the path to a KB article in Markdown format to parse")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
def main(filename):

    with open(filename) as sf_kb:
        sf_kb_file = sf_kb.read()

    markdown = mistune.create_markdown(renderer=MyRenderer())

    f = open(os.path.splitext(filename)[0] + ".html", "w")
    f.write(markdown(sf_kb_file))


if __name__ == "__main__":
    main()
