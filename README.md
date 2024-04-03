# blogspot

Compiles a Blogger blog into a standalone html file and PDF.

Currently (as far as I'm aware) it only works for Blogger sites with the Contempo theme and a publicly-accessible index page.

## Usage

```bash
python3 blogspot_fetch.py <blog_index_url>
```

E.g.

```bash
python3 blogspot_fetch.py https://myblog.blogspot.com/p/index.html
```

This will output the blog to `myblog.html` and `myblog.pdf`.

It just copies the default Blogger styling, which can be modified in `style.html`. It terms of organization, it only adds a table of contents.
