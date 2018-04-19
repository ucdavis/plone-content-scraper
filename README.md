Scraping tool for extracting data from Plone
===

This file is necessary for recursively populating a directory of all linked, image, and attachment content within a directory on Plone.

Part of a very rudimentary migration system.

Requires Python 3

# Install
Clone this repository onto your computer 
```
pip3 install bs4 url_normalize requests
```

# Usage

```
python3 scrape.py <url>
```
the script will populate the current directory with all directories it crawls and any subdirectories. It produces an errors.txt and index.json that describes which folder goes to which url on the original site.
