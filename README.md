# ODT to HTML5

Convert [ODT](https://en.wikipedia.org/wiki/OpenDocument) text document to HTML5.

## Fetching

Just get the code and make temporary folder writable by web server. For example:

    git clone https://github.com/jroivas/odt-html5.git
    cd odt-html5

## Converting

To convert ODT to static HTML files do:

   python gen_html.py file.odt

Will generate HTML pages with default settings.

### Settings

One can define converting and output settings on command line.
Most common feature is to define title, it's easy as:

    python gen_html.py --title "My example title" file.odt

By default pages are named like `page_pagenum.html` where `pagenum` is numbering starting from 1. You may want for example localize the page name or change it. It's easy with prefix option:

    python gen_html.py --prefix test file.odt

This will generate now pages named as: `test_pagenum.html`

Sometimes your document contains index and you want your landing page (from first page to first chapter) contain more stylish info. Index can be generated with:

    python gen_html.py --index index file.odt

That will generate `index.html` with contents from first page till first chapter, and index of all chapters.

In the end you may end up using something like:

    python gen_html.py --index frontpage --page p --title "My example" file.odt

This will generate `frontpage.html` and `p_2.html`, `p_3.html`, ...

To see full options:

    python gen_html.py -h

## Distributing

To distribute your document as HTML, provide following:

 - All generated HTML files
 - `img` folder with extracted images
 - `odt.js`
 - `odt_black.css` OR `odt_white.css` renamed to `odt.css`
 - `jquery.min.js`
    * You may download it with script: `./download.sh`

## Known issues

 - Not fully compatible with [ODT spec](http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html), only minimal set supported
    * Feel free to improve
 - Tabs does not work properly
    * Mostly because of limitations of HTML
    * Could however handle them slightly better
 - Refactoring needed
