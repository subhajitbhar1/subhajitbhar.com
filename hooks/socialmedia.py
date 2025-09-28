from textwrap import dedent
import urllib.parse
import re

x_intent = "https://x.com/intent/tweet"
fb_sharer = "https://www.facebook.com/sharer/sharer.php"
linkedin_sharer = "https://www.linkedin.com/shareArticle"

include = re.compile(r"(blogs|projects)/(?!archive|category).+")

def on_page_markdown(markdown, **kwargs):
    page = kwargs['page']
    config = kwargs['config']
    if not include.match(page.url):
        return markdown

    page_url = config.site_url+page.url
    page_title = urllib.parse.quote(page.title+'\n')

    return markdown + dedent(f"""

    ---
    **Share this post:**

    [Share on :simple-x:]({x_intent}?text={page_title}&url={page_url}){{ .md-button }}
    [Share on :material-facebook:]({fb_sharer}?u={page_url}){{ .md-button }}
    """)
    # [Share on :material-linkedin:]({linkedin_sharer}?url={page_url}){{ .md-button }}