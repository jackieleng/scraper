"""Crawler logic.
"""

from html.parser import HTMLParser
import random
import time
from urllib.parse import urljoin, urlparse

from .utils import (
    head_request,
    get_request,
    decode_html,
    )

VISITED_URLS = set()
UNVISITED_URLS = [
    "https://www.reddit.com",
    "http://www.nu.nl",
    ]
INTERVAL = 10  # politeness policy

# TODO: db, redis, robotstxt, rand delay, rand user agent, multithreading

# TODO: make url frontier a dict with as key the base_url of the site. This
# way we can do threaded execution by using each thread to take urls only
# from one base url.


class LinkParser(HTMLParser):
    """Get all links in an HTML page

    This parser will ignore anchor links with the #-sign and those starting
    with the word 'javascript' (cases like: <a href="javascript: void(0)">")

    # TODO: #-sign links can possibly lead to other pages (not on the same
    page), so we should not ignore them but include them. There should be a
    check to see if they are on the same page, and if not, include the link.
    But with NEEDS to be ignored are links created for the sole purpose of
    activating a JS function, e.g.: <a href='#' onclick="JsFunc();">
    """
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href':
                    if 'http' in urlparse(val).scheme:
                        self.links.append(val)
                    # also avoid anchor links and javascript links
                    elif val != '' and '#' not in val and \
                            not val.startswith('javascript:'):
                        link = urljoin(self.base_url, val)
                        self.links.append(link)

    def get_links(self, url, html):
        self.base_url = url
        self.links = []
        super().feed(html)
        return self.links


def check_url(url):
    """Probe url first using a HEAD request and check if it's HTML.

    This checks if the page at the url is valid HTML based on its content
    type. Note that this probably doesn't 100% guarantee that it is HTML;
    web servers can mess with the content type...
    """
    HTML_CONTENTTYPES = {'text/html'}

    is_html = False
    response = head_request(url)
    if response:
        info = response.info()
        content_type = info.get_content_type()
        is_html = content_type in HTML_CONTENTTYPES
        response.close()
    return is_html


def get_links(url):
    """Extract all links from html page, and return a list of those links"""
    links = []
    response = get_request(url)
    if response:
        html_bytes = response.read()
        html_text = decode_html(html_bytes, url=url)
        response.close()
        if not html_text:
            return []

        parser = LinkParser()
        links = parser.get_links(url, html_text)
    return links


def parse_page(url):
    """Process the page from an url.
    """
    # link_parser = LinkParser()
    links = get_links(url)
    return links


def url_selector(urls):
    """URL selection policy.

    For now just random
    """
    i = random.randint(0, len(urls) - 1)
    return urls.pop(i)


def crawler(visited_urls, unvisited_urls):
    """This contains the actual crawler logic/structure.

    In the while loop the following steps are performed:

    1. Take a url from the set of unvisited urls.
    2. Probe the url with a HEAD request to check if it's actually HTML.
    3. If it's valid, first sleep, because we're gonna make another request,
       then parse the page of the url and return the links.
       Else sleep again, but skip the rest of the loop (i.e. go back to 2)
    4. If we got fetched links in 3, we will first check if they're not
       already visited, and then add them to the unvisited urls. The url
       is also added to the set of visited urls.
    """
    while len(unvisited_urls) > 0:
        next_url = url_selector(unvisited_urls)
        if check_url(next_url):
            time.sleep(INTERVAL)  # parse page makes a request
            fetched_urls = parse_page(next_url)
        else:
            time.sleep(INTERVAL)  # check_url makes a request
            continue
        visited_urls.add(next_url)
        for url in fetched_urls:
            if url not in visited_urls:
                unvisited_urls.append(url)

        print("Number of urls visited: %s, unvisited: %s" %
              (len(visited_urls), len(unvisited_urls)))
        print("URLs visited: %s" % visited_urls)
            #print("URL frontier: %s" % unvisited_urls)


class Crawler(object):
    def __init__(self, base_url):
        self.base_url = base_url


def main():
    crawler(VISITED_URLS, UNVISITED_URLS)
