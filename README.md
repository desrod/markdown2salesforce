# Markdown to Salesforce Converter

This, like many other tools, evolved out of a necessity to increase velocity editing content, without fighting with the tools, formats or conversions.

It's a simple little bit of Python that I started writing after playing with the "[Markdown Preview Enhanced](https://shd101wyy.github.io/markdown-preview-enhanced/#/)" VSCodium extension. I also use [MarkdownLint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) extensively while authoring my KB and HOWTO articles.

I prefer to keep my content in a single, portable format since I regularly have to post the same content to multiple, disconnected, incompatible sources (namely Salesforce and Confluence), so I chose Markdown as the "Source of Truth&trade;" for all of my articles.

Ideally, I would have preferred Markdown Preview Enhanced to render this directly each time I saved the Markdown, using the VSCodium [pandoc extension](https://marketplace.visualstudio.com/items?itemName=DougFinke.vscode-pandoc), but that didn't work as well as I'd hoped, due to some odd choices in hard-coding the CSS and HTML in the Mamu dependency pandoc uses. It can save to HTML at each save of the .md file, but the HTML it emits is incompatible with Salesforce or Confluence.

So my journey took me through dozens of different Python modules, including [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Markdown](https://python-markdown.github.io/), [Markdown2](https://github.com/trentm/python-markdown2), lxml and finally [mistune](https://github.com/lepture/mistune).

Mistune allowed me to wrestle the output HTML in a way that I can override what is emitted and transform the tags before they hit the disk or output stream. That was the missing piece to getting the Markdown compatible with Salesforce, so it would accept it and render it as a proper visual article with code blocks and other lists/headings intact.

I don't know why in 2020 everything we write in a browser, doesn't support Markdown as a base format, but that's a discussion for another time...

To use this, simply take one of your articles in Markdown format, and pass it as an argument to md2sf.py. It will transform the markdown into a modified format of HTML that Salesforce can ingest and render in its own Knowledgebase system. 

```bash
./md2sf.py sample.md
```

The input .md file you pass in (sample.md in the above example), will be saved back as the same base filename with a .html extension.

```bash
$ ls -1 sample.*
sample.html
sample.md
```

Take that HTML and paste it into the Salesforce KB form under the "Source" view mode, then click "Source" again on that form to get Salesforce to re-render in its own format, suitable for saving.



That's it!