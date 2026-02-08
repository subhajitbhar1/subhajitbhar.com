import xml.etree.ElementTree as ET
from pathlib import Path


def on_post_build(config, **kwargs):
    site_dir = Path(config["site_dir"])
    sitemap_path = site_dir / "sitemap.xml"
    if not sitemap_path.exists():
        return

    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    extra_urls = [
        f"{config['site_url']}llms.txt",
        f"{config['site_url']}robots.txt",
    ]
    existing = {url_el.text for url_el in root.iter(f"{{{ns}}}loc")}

    for url in extra_urls:
        if url not in existing:
            url_el = ET.SubElement(root, f"{{{ns}}}url")
            loc_el = ET.SubElement(url_el, f"{{{ns}}}loc")
            loc_el.text = url

    tree.write(str(sitemap_path), xml_declaration=True, encoding="UTF-8")
