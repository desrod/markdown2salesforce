#!/usr/bin/env python3

import base64
import os

import click
import mistune
from mistune import escape


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
        import magic

        return magic.from_file(url, mime=True)


@click.command(help="Plese supply the path to a KB article in Markdown format to parse")
@click.argument("filename", type=click.Path(exists=True, readable=True), nargs=1)
def main(filename):
    """Main function to parse a Markdown file and save it as HTML."""
    with open(filename, "r") as sf_kb:
        sf_kb_file = sf_kb.read()

    markdown = mistune.create_markdown(renderer=sf_html_render())
    html_filename = os.path.splitext(filename)[0] + ".html"

    with open(html_filename, "w") as sf_html:
        sf_html.write(markdown(sf_kb_file))


if __name__ == "__main__":
    main()
