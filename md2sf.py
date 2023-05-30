#!/usr/bin/env python3


import os

import click
import mistune
from mistune.scanner import escape
import base64
import magic

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

    def image(self, url, alt, title=None):
        """override the default image handler to base64 encode the
           file content, if the file is available"""
        
        if os.path.isfile(url):
            with open(url, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            mimetype = magic.from_file(url, mime=True)
            url = f'data:{mimetype};base64,{encoded_string}'

        return f'<img alt="{alt}" title="{title}" src="{url}" style="margin-top: 5px; margin-bottom: 5px;" />'

    def heading(self, text, level, **attrs):
        """Our KB template does not like headers, so converting them just to a bold text
           First Heading should not have a margin-top"""

        return f"<p style='margin-top: 15px;'><b>{text}</b></p>\n"

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
