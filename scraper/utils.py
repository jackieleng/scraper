#!/usr/bin/env python
"""Mostly utils for making html requests.
"""

import urllib.request
from urllib.error import HTTPError, URLError


# Some user agent spoofing, seems to improve too many requests errors
SPOOF_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }


def head_request(url):
    """Make a HEAD request.

    NOTE: returns None if it fails, with exception of uncaught Exceptions
    """
    response = None
    r = urllib.request.Request(url, method='HEAD', headers=SPOOF_HEADERS)
    try:
        response = urllib.request.urlopen(r)
    except (HTTPError, URLError, UnicodeEncodeError) as e:
        print("Can't probe this url: %s" % url)
        print(e)
    except Exception as e:
        print("Unknown exception with: %s" % url)
        raise
    return response


def get_request(url):
    """Make a GET request.

    NOTE: returns None if it fails, with exception of uncaught Exceptions
    """
    response = None
    r = urllib.request.Request(url, headers=SPOOF_HEADERS)
    try:
        response = urllib.request.urlopen(r)
    except HTTPError as e:
        print("Failed to open url %s" % url)
        print(e)
    except Exception as e:
        print("Exception with url %s" % url)
        raise
    return response


def decode_html(html_bytes, url=None):
    html_text = ""
    try:
        html_text = html_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        print("Can't decode this into html: %s" % url)
        print(e)
    except Exception as e:
        print("Exception with url %s" % url)
        raise
    return html_text
