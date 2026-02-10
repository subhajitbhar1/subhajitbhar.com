import re
import urllib.parse
from textwrap import dedent

x_intent = "https://x.com/intent/tweet"
fb_sharer = "https://www.facebook.com/sharer/sharer.php"
linkedin_sharer = "https://www.linkedin.com/shareArticle"

include = re.compile(r"(blogs|projects)/(?!archive|category).+")


def on_page_markdown(markdown, **kwargs):
    page = kwargs["page"]
    config = kwargs["config"]
    if not include.match(page.url):
        return markdown

    page_url = config.site_url + page.url
    page_title = urllib.parse.quote(page.title + "\n")

    return markdown + dedent(f"""
    ---
    ## Stay Updated

    Join my newsletter for the latest insights on Document AI, RAG, and LLM technologies:

    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; margin: 1.5rem 0;">
        <iframe src="https://documentai.substack.com/embed" width="100%" height="320" style="border: none; background: white; border-radius: 4px; max-width: 100%;" frameborder="0" scrolling="no"></iframe>
    </div>

    ---
    ## Share This Post

    [Share on :simple-x:]({x_intent}?text={page_title}&url={page_url}){{ .md-button }}
    [Share on :material-facebook:]({fb_sharer}?u={page_url}){{ .md-button }}
    """)
    # [Share on :material-linkedin:]({linkedin_sharer}?url={page_url}){{ .md-button }}
