#!/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup
import pdfkit

if len(sys.argv) != 2:
    print("Usage: blogspot_fetch.py <blog_index_url>")
    exit(1)

url = sys.argv[1]
blog_name = url.split(".")[0].split("/")[-1]

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

links = [link["href"] for link in soup.select(".post-body > p > a")]

titles = []

output_html = ""
separator_html = "<div class=\"page-separator\"></div>\n"

article = 1
for link in links:
    link_response = requests.get(link)

    if "Sensitive Content Warning" in link_response.text:
        print(f"Unable to fetch {link} (sensitive content)")
        continue
    else:
        print(f"Fetched {link}")

    link_soup = BeautifulSoup(link_response.text, "html.parser")

    title_element = link_soup.select_one("#Blog1 > div > article > div > div > h3")
    if title_element:
        titles.append(title_element.text.strip())
        title_element['id'] = f"article-{article}"

    share_button = link_soup.select_one("#Blog1 > div > article > div > div > div.post-share-buttons.post-share-buttons-top")
    if share_button:
        share_button.decompose()

    post_bottom = link_soup.select_one("#Blog1 > div > article > div > div > div.post-bottom")
    if post_bottom:
        post_bottom.decompose()

    desired_element = link_soup.select_one("#Blog1 > div > article > div > div")
    if desired_element:
        output_html += desired_element.prettify() + "\n"
        output_html += separator_html

    article += 1

with open("style.html", "r") as file:
    style_html = file.read()

toc_html = "<h3 class=\"post-title entry-title\"> Table of Contents</h3>\n<ul>\n"
for i, title in enumerate(titles, start=1):
    toc_html += f'<li><a href="#article-{i}">{title}</a></li>\n'
toc_html += "</ul>" + separator_html

with open(f"{blog_name}.html", "w", encoding="utf-8") as file:
    file.write(style_html)
    file.write(toc_html)
    file.write(output_html)

print(f"Wrote to {blog_name}.html")

options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8'
}

print(f"Generating {blog_name}.pdf...")

pdfkit.from_file(f"{blog_name}.html", f"{blog_name}.pdf", options=options)

print(f"Generated {blog_name}.pdf")
