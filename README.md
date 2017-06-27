# ODT to HTML5

Convert [https://en.wikipedia.org/wiki/OpenDocument](ODT) text document to HTML5.

## Fetching

Just get the code and make temporary folder writable by web server. For example:

    git clone https://github.com/jroivas/odt-html5.git
    cd odt-html5

## Running

Start by:

    python index.py

Or script which makes it run even if it fails:

    ./runner.sh

After successfull setup just upload test.odt to same folder and see the result.
Default port is 8042, so try for example: http://localhost:8042

## Batch convert

To convert ODT to static HTML files do:

   python gen_html.py file.odt
