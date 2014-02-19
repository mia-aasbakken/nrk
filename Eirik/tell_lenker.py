#coding: utf-8

import re
import tldextract
import logging

def tell(soup, data, dictionary):
    # create logger with 'tldextract'
    logger = logging.getLogger('tldextract')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


    # only a's inside the article tag (not the menus and stuff)
    a = soup.article.find_all("a")

    lenker = []

    # these links we do not want to include..
    not_published_links = soup.select(".published a")
    not_sharing_links = soup.select(".sharing a")
    not_byline_links = soup.select(".byline a")
    # should we remove the whole aside-element? (I want to include the fack-box, but not "related stories")
    # we should remove all links that have a[href] javascript:location....
    # remove those..
    a = set(a) - set(not_published_links + not_sharing_links + not_byline_links)

    for lenke in a:
        href = lenke.get('href')
        if href != None:
            lenker.append(href)




    internal_domains = ['nrk','dit', 'ut', 'yr', 'p3', 'nrkaktivum', 'nrkbeta', 'nrkbutikken', 'nrksuper']
    # javascript ? mailto? 
    
    interne_lenker = []
    eksterne_lenker = []
    for lenke in lenker:
        # her må det en sjekk om url'n finnes i en liste av domener...
        ext = tldextract.extract(lenke)     # https://pypi.python.org/pypi/tldextract
        if ext.domain in internal_domains:
            interne_lenker.append(lenke)
        else:
            eksterne_lenker.append(lenke)

    dictionary['external_links'] = eksterne_lenker
    dictionary['internal_links'] = interne_lenker
    return