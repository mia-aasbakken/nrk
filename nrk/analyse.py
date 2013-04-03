#!/usr/bin/python
# coding: utf-8

from bs4 import BeautifulSoup, Comment
from argparse import ArgumentParser
from urllib2 import build_opener, unquote
from re import match, search
from itertools import izip
from tldextract import extract

class Page:
    def __init__(self, url=None):
        self.url = url
        self.published = {'date':'na', 'time':'na'}
        self.updated = {'date':'na', 'time':'na'}
        self.authors = []
        self.links = {'internal':0, 'external':0}

class Author:
    def __init__(self):
        self.name = None
        self.email = None

class Analyser:
    """
    Analyser for NRK articles.

    """

    def headers = [('User-agent',
                    'UiB NRK Proj (Contact: Eirik.Stavelin@infomedia.uib.no)')]
    def __init__(self):
        self.pagereader = build_opener()
        self.pagereader.addheaders(headers)

    def _analyse_old(url=None):
        doc = pagereader.open(url, None, 15)
        soup = BeautifulSoup(doc)
        page = Page(url)

        #Remove all comments
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        intro = soup.find(class_='intro-element-article')
        page.title = intro.h1.text

        # <p class="published">Publisert 15.05.2008 10:49. Oppdatert 15.05.2008 10:59.</p>
        published = soup.find('p', 'published').string
        page.published['date'] = published[10:20]
        page.published['time'] = published[21:26]

		if search(published, 'Oppdatert'):
            page.updated['date'] = published[38:48]
            page.updated['time'] = published[49:54]

        byline = soup.find('ul', 'byline')
        for address in byline.find_all('address'):
            author = Author()
            author.name = address.span.string
            # To find the mail we need to to do some unquoting
            # as nrk is trying to protect the mail address
            # from spammers behind a quoted string.
            script = address.script.string
            m = search(".*?'(.*)'.*$", script)
            m = search(".*?'(.*)'.*$", unquote(m.group(1)))
            html = BeautifulSoup(m.group(1))
            author.email = html.a.string

            page.authors.append(author)

        # The script tags need to be removed after finding the
        # byline. The email is in a script tag here.
        [script.extract() for script in soup.find_all('script')]

        article = soup.find(class_='article')
        for link in intro.find_all('a') + article.find_all('a'):
            domain = extract(link['href']).domain
            if domain is 'nrk':
                page.links['internal'] += 1
            else:
                page.links['external'] += 1

        images = intro.find_all('img') + article.find_all('img')
        page.images = len(images)

        # Remove all images as they might appear in the
        # .text otherwise.
        [img.extract() for img in soup.find_all(img)]
        text = intro.text
        text += article.text
        text = split("\s+", text.strip())
        page.wc = len(text)
        return page

    def _analyse_new(url=None):
        doc = pagereader.open(url, None, 15)
        soup = BeautifulSoup(doc)
        page = Page(url)

        # We don't need the html comments so they are removed.
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        # The same with the script tags. Here we can remove
        # at the beginning as the email has moved into a
        # href instead of a script.
        [script.extract() for script in soup.find_all('script')]

        article = soup.find('article')
        page.title = article.header.find('div', 'articletitle').h1.string

        published = soup.find('div', 'published').find('span', 'publish-date')['title']
        page.published['date'] = published[:10]
        page.published['time'] = published[15:21]

        updated = soup.find('div', 'published').find('span', 'update-date')
        if updated:
            updated = updated['title']
            page.updated['date'] = updated[:10]
            page.updated['time'] = updated[15:21]

        byline = soup.find('div', 'byline')
        # for some reason the mail is not connected to the
        # name, but we can fix that.
        for address, li in izip(byline.find_all('address'),
                                byline.find_all('li', 'icon-mail')):
            author = Author()
            author.name = address.find(class_='fn').string
            # NRK is still trying to hide the email address
            # from spammers.
            href = li.a['href']
            author.mail = unquote(href[21:-1])[7:]
            author.role = address.find(class_='role').string.strip()

            page.authors.append(author)

        header = article.header
        body = article.find(class_='articlebody')
        for link in header.find_all('a') + body.find_all('a'):
            domain = extract(link['href']).domain
            if domain is 'nrk':
                page.links['internal'] += 1
            else:
                page.links['external'] += 1

        images = header.find_all('img') + body.find_all('img')
        page.images = len(images)

        # Remove all images as they appear in the .text
        # otherwise.
        [img.extract() for img in soup.find_all(img)]
        text = header.text
        text += body.text
        text = split('\s+', text.strip())
        page.wc = len(text)
        return page

    def analyse(url=None):
        """
        Analyses NRK pages and returns a Page object ready
        for database serialization.

        Keyword argument:
        url -- the url from NRK to analyse

        returns a Page object.

        """
        if not url:
            raise TypeError("analyse needs 1 argument.")

        if match('^.*/\d\.\d+$', url):
            return analyse_old(url)
        else:
            return analyse_new(url)

if __name__ == '__main__':
    parser = ArgumentParser(description='Analyse nrk url.')
    parser.add_argument('url', metavar='URL')
    args = parser.parse_args()
    analyser = Analyser()
    analyser.analyse(url=args.url.strip())
