#!/bin/env python3

import requests
import sys
from bs4 import BeautifulSoup

if len(sys.argv) != 2:
    print("Usage: blogspot_fetch.py <url>")
    exit(1)

url = sys.argv[1]

# Send a GET request to the URL
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find all links matching the specified CSS selector
links = [link["href"] for link in soup.select("#post-body-4425880098561414349 > p > a")]

# Create an empty list to store the article titles
titles = []

output_html = ""
separator_html = "<div class=\"page-separator\"></div>\n"

# Iterate over each link
for i, link in enumerate(links, start=1):
    print(f"Fetching {link}")
    # Send a GET request to each link
    link_response = requests.get(link)
    # Create a BeautifulSoup object for the link's content
    link_soup = BeautifulSoup(link_response.text, "html.parser")
    # Extract the article title
    title_element = link_soup.select_one("#Blog1 > div > article > div > div > h3")
    if title_element:
        titles.append(title_element.text.strip())
        title_element['id'] = f"article-{i}"
    # Delete the specified elements
    share_button = link_soup.select_one("#Blog1 > div > article > div > div > div.post-share-buttons.post-share-buttons-top")
    if share_button:
        share_button.decompose()
    post_bottom = link_soup.select_one("#Blog1 > div > article > div > div > div.post-bottom")
    if post_bottom:
        post_bottom.decompose()
    # Get the desired element from the link's content
    desired_element = link_soup.select_one("#Blog1 > div > article > div > div")
    # Append the element's HTML text to the output file
    if desired_element:
        output_html += desired_element.prettify() + "\n"
        output_html += separator_html

with open("style.html", "r") as file:
    style_html = file.read()

# Create the table of contents HTML
toc_html = "<h3 class=\"post-title entry-title\"> Table of Contents</h3>\n<ul>\n"
for i, title in enumerate(titles, start=1):
    toc_html += f'<li><a href="#article-{i}">{title}</a></li>\n'
toc_html += "</ul>\n"

# Write the output file with the table of contents and output HTML
with open("output.html", "w", encoding="utf-8") as file:
    file.write(style_html)
    file.write(toc_html)
    file.write(output_html)

print("Wrote to output.html")
