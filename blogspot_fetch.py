#!/usr/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup
import pdfkit
import os
from urllib.parse import urljoin

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    return None

def generate_pdf(html_file, pdf_file):
    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': 'UTF-8',
        'enable-local-file-access': None
    }
    print(f"Generating {pdf_file}...")
    pdfkit.from_file(html_file, pdf_file, options=options)
    print(f"Generated {pdf_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: blogspot_fetch.py <blog_index_url>")
        sys.exit(1)

    url = sys.argv[1]
    blog_slug = url.split(".")[0].split("/")[-1]
    html_file = f"{blog_slug}.html"

    if os.path.exists(html_file):
        use_existing = input(f"{html_file} already exists.\nDo you want to use it to generate the PDF?\nOtherwise, all pages from the index will be redownloaded. (y/n): ").lower()
        if use_existing == 'y':
            generate_pdf(html_file, f"{blog_slug}.pdf")
            return

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = [link["href"] for link in soup.select(".post-body > p > a")]
    blog_title = soup.select_one('#Header1 > div > div > h1 > a').text
    blog_image_url = soup.select_one('#Profile1 > div > div > a > img')['src']
    
    # Fix the image URL if it's a relative URL
    if blog_image_url.startswith('//'):
        blog_image_url = 'https:' + blog_image_url
    elif not blog_image_url.startswith(('http:', 'https:')):
        blog_image_url = urljoin(url, blog_image_url)
    
    blog_image_filename = f"{blog_slug}_image.jpg"
    blog_image = download_image(blog_image_url, blog_image_filename)
    blog_description = soup.select_one('#Profile1 > div > div > div > dl > dd > div.snippet-item.r-snippetized').text
    blog_author = soup.select_one('#Profile1 > div > div > div > dl > dt > a').text

    article_data = []
    url_to_slug = {}

    output_html = ""
    separator_html = "<div class=\"page-separator\"></div>\n"

    for link in links:
        link_response = requests.get(link)
        article_slug = link.split("/")[-1].replace(".html", "")
        url_to_slug[link] = article_slug

        if "Sensitive Content Warning" in link_response.text:
            print(f"Unable to fetch {link} (sensitive content)")
            continue
        else:
            print(f"Fetched {link}")

        link_soup = BeautifulSoup(link_response.text, "html.parser")

        title_element = link_soup.select_one("#Blog1 > div > article > div > div > h3")
        if title_element:
            title = title_element.text.strip()
            title_element['id'] = article_slug
            article_data.append({"title": title, "slug": article_slug})

        share_button = link_soup.select_one("#Blog1 > div > article > div > div > div.post-share-buttons.post-share-buttons-top")
        if share_button:
            share_button.decompose()

        post_bottom = link_soup.select_one("#Blog1 > div > article > div > div > div.post-bottom")
        if post_bottom:
            post_bottom.decompose()

        desired_element = link_soup.select_one("#Blog1 > div > article > div > div")
        if desired_element:
            for a in desired_element.find_all('a', href=True):
                if a['href'] in url_to_slug:
                    a['href'] = f"#{url_to_slug[a['href']]}"
                    a.attrs.pop('target', None)
            output_html += str(desired_element) + "\n"
            output_html += separator_html

    with open("style.html", "r") as file:
        style_html = file.read()

    title_page_html = f"""
    <div class="title-page">
        <h1 class="blog-title">{blog_title}</h1>
        <img src="{blog_image_filename}" alt="Blog Image" class="blog-image">
        <p class="blog-description">{blog_description}</p>
        <p class="blog-author">by {blog_author}</p>
    </div>
    """

    toc_html = "<h3 class=\"post-title entry-title\">Table of Contents</h3>\n<ul>\n"
    for article in article_data:
        toc_html += f'<li><a href="#{article["slug"]}">{article["title"]}</a></li>\n'
    toc_html += "</ul>" + separator_html

    with open(html_file, "w", encoding="utf-8") as file:
        file.write(style_html)
        file.write(title_page_html)
        file.write(toc_html)
        file.write(output_html)

    print(f"Wrote to {html_file}")

    generate_pdf(html_file, f"{blog_slug}.pdf")

if __name__ == "__main__":
    main()
