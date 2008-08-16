__all__ = []
"""Python wrapper


for Amazon web APIs

This module allows you to access Amazon's web APIs,
to do things like search Amazon and get the results programmatically.
Described here:
  http://www.amazon.com/webservices

You need a Amazon-provided license key to use these services.
Follow the link above to get one.  These functions will look in
several places (in this order) for the license key:
- the "license_key" argument of each function
- the module-level LICENSE_KEY variable (call setLicense once to set it)
- an environment variable called AMAZON_LICENSE_KEY
- a file called ".amazonkey" in the current directory
- a file called "amazonkey.txt" in the current directory
- a file called ".amazonkey" in your home directory
- a file called "amazonkey.txt" in your home directory
- a file called ".amazonkey" in the same directory as amazon.py
- a file called "amazonkey.txt" in the same directory as amazon.py

Sample usage:
>>> import amazon
>>> amazon.setLicense('...') # must get your own key!
>>> pythonBooks = amazon.searchByKeyword('Python')
>>> pythonBooks[0].ProductName
u'Learning Python (Help for Programmers)'
>>> pythonBooks[0].URL
...
>>> pythonBooks[0].OurPrice
...

Other available functions:
- browseBestSellers
- searchByASIN
- searchByUPC
- searchByAuthor
- searchByArtist
- searchByActor
- searchByDirector
- searchByManufacturer
- searchByListMania
- searchSimilar
- searchByWishlist

Other usage notes:
- Most functions can take product_line as well, see source for possible values
- All functions can take type="lite" to get less detail in results
- All functions can take page=N to get second, third, fourth page of results
- All functions can take license_key="XYZ", instead of setting it globally
- All functions can take http_proxy="http://x/y/z" which overrides your system setting
"""

__author__ = "Mark Pilgrim (f8dy@diveintomark.org)"
__version__ = "0.64.1"
__cvsversion__ = "$Revision: 1.1 $"[11:-2]
__date__ = "$Date: 2005/08/06 13:29:10 $"[7:-2]
__copyright__ = "Copyright (c) 2002 Mark Pilgrim"
__license__ = "Python"
# Powersearch and return object type fix by Joseph Reagle <geek@goatee.net>

# Locale support by Michael Josephson <mike@josephson.org>

# Modification to _contentsOf to strip trailing whitespace when loading Amazon key
# from a file submitted by Patrick Phalen.

# Support for specifying locale and associates ID as search parameters and 
# internationalisation fix for the SalesRank integer conversion by
# Christian Theune <ct@gocept.com>, gocept gmbh & co. kg

# Support for BlendedSearch contributed by Alex Choo

from xml.dom import minidom
import os, sys, getopt, cgi, urllib, string
try:
    import timeoutsocket # http://www.timo-tasi.org/python/timeoutsocket.py
    timeoutsocket.setDefaultSocketTimeout(10)
except ImportError:
    pass

LICENSE_KEY = ""
ASSOCIATE = "webservices-20"
HTTP_PROXY = None
LOCALE = "us"
# default API version is from 2005-10-05
APIVERSION='2008-06-26'

# don't touch the rest of these constants
class AmazonError(Exception): pass
class NoLicenseKey(Exception): pass
_amazonfile1 = ".amazonkey"
_amazonfile2 = "amazonkey.txt"
_licenseLocations = (
    (lambda key: key, 'passed to the function in license_key variable'),
    (lambda key: LICENSE_KEY, 'module-level LICENSE_KEY variable (call setLicense to set it)'),
    (lambda key: os.environ.get('AMAZON_LICENSE_KEY', None), 'an environment variable called AMAZON_LICENSE_KEY'),
    (lambda key: _contentsOf(os.getcwd(), _amazonfile1), '%s in the current directory' % _amazonfile1),
    (lambda key: _contentsOf(os.getcwd(), _amazonfile2), '%s in the current directory' % _amazonfile2),
    (lambda key: _contentsOf(os.environ.get('HOME', ''), _amazonfile1), '%s in your home directory' % _amazonfile1),
    (lambda key: _contentsOf(os.environ.get('HOME', ''), _amazonfile2), '%s in your home directory' % _amazonfile2),
    (lambda key: _contentsOf(_getScriptDir(), _amazonfile1), '%s in the amazon.py directory' % _amazonfile1),
    (lambda key: _contentsOf(_getScriptDir(), _amazonfile2), '%s in the amazon.py directory' % _amazonfile2)
    )
_supportedLocales = {
        "us" : (None, "ecs.amazonaws.com/onca/xml?Service=AWSECommerceService"),   
        "uk" : ("uk", "ecs.amazonaws.co.uk/onca/xml?Service=AWSECommerceService"),
        "de" : ("de", "ecs.amazonaws.de/onca/xml?Service=AWSECommerceService"),
        "ca" : ("ca", "ecs.amazonaws.ca/onca/xml?Service=AWSECommerceService"),
        "fr" : ("fr", "ecs.amazonaws.fr/onca/xml?Service=AWSECommerceService"),
        "jp" : ("jp", "ecs.amazonaws.jp/onca/xml?Service=AWSECommerceService")
    }

## administrative functions
def version():
    print """PyAmazon %(__version__)s
%(__copyright__)s
released %(__date__)s
""" % globals()

def setAssociate(associate):
    global ASSOCIATE
    ASSOCIATE=associate

def getAssociate(override=None):
    return override or ASSOCIATE

## utility functions

def _checkLocaleSupported(locale):
    if not _supportedLocales.has_key(locale):
        raise AmazonError, ("Unsupported locale. Locale must be one of: %s" %
            string.join(_supportedLocales, ", "))

def setLocale(locale):
    """set locale"""
    global LOCALE
    _checkLocaleSupported(locale)
    LOCALE = locale

def getLocale(locale=None):
    """get locale"""
    return locale or LOCALE

def setLicense(license_key):
    """set license key"""
    global LICENSE_KEY
    LICENSE_KEY = license_key

def getLicense(license_key = None):
    """get license key

    license key can come from any number of locations;
    see module docs for search order"""
    for get, location in _licenseLocations:
        rc = get(license_key)
        if rc: return rc
    raise NoLicenseKey, 'get a license key at http://www.amazon.com/webservices'

def setProxy(http_proxy):
    """set HTTP proxy"""
    global HTTP_PROXY
    HTTP_PROXY = http_proxy

def getProxy(http_proxy = None):
    """get HTTP proxy"""
    return http_proxy or HTTP_PROXY

def getProxies(http_proxy = None):
    http_proxy = getProxy(http_proxy)
    if http_proxy:
        proxies = {"http": http_proxy}
    else:
        proxies = None
    return proxies

def _contentsOf(dirname, filename):
    filename = os.path.join(dirname, filename)
    if not os.path.exists(filename): return None
    fsock = open(filename)
    contents =  fsock.read().strip()
    fsock.close()
    return contents

def _getScriptDir():
    if __name__ == '__main__':
        return os.path.abspath(os.path.dirname(sys.argv[0]))
    else:
        return os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))

class Bag: pass

def unmarshal(element):
    rc = Bag()
    if isinstance(element, minidom.Element) and (element.tagName == 'Details'):
        rc.URL = element.attributes["url"].value
    childElements = [e for e in element.childNodes if isinstance(e, minidom.Element)]
    if childElements:
        for child in childElements:
            key = child.tagName
            if hasattr(rc, key):
                if type(getattr(rc, key)) <> type([]):
                    setattr(rc, key, [getattr(rc, key)])
                setattr(rc, key, getattr(rc, key) + [unmarshal(child)])
            elif isinstance(child, minidom.Element) and (child.tagName == 'Details'):
                # make the first Details element a key
                setattr(rc,key,[unmarshal(child)])
                #dbg: because otherwise 'hasattr' only tests
                #dbg: on the second occurence: if there's a
                #dbg: single return to a query, it's not a
                #dbg: list. This module should always
                #dbg: return a list of Details objects.
            else:
                setattr(rc, key, unmarshal(child))
    else:
        rc = "".join([e.data for e in element.childNodes if isinstance(e, minidom.Text)])
        if element.tagName == 'SalesRank':
            rc = rc.replace('.', '')
            rc = rc.replace(',', '')
            rc = int(rc)
    return rc

def buildURL(search_type, searchfield, searchvalue, product_line, type, page, license_key, locale, associate):
    _checkLocaleSupported(locale)
    url = "http://" + _supportedLocales[locale][1]
    if search_type == 'ItemLookup':
        url += "&AssociateTag=%s" % associate
        url += "&AWSAccessKeyId=%s" % license_key.strip()
        url += "&ResponseGroup=%s" % type
        if product_line:
            url += "&SearchIndex=%s" % product_line
        url += "&Operation=%s" % search_type
        url += "&IdType=%s" % searchfield
        url += "&ItemId=%s" % searchvalue
    else:
        url += "&AssociateTag=%s" % associate
        url += "&AWSAccessKeyId=%s" % license_key.strip()
        url += "&ResponseGroup=%s" % type
        if page:
            url += "&ItemPage=%s" % page
        if product_line:
            url += "&SearchIndex=%s" % product_line
        url += "&Operation=%s" % search_type
        url += "&%s=%s" % (searchfield, urllib.quote(searchvalue))
        url += "&Sort=titlerank"
    if not APIVERSION is None:
        url += "&Version=%s" % APIVERSION
    return url


## main functions


def search(search_type, searchfield, searchvalue, product_line, type = "Large", page = None,
           license_key=None, http_proxy = None, locale = None, associate = None):
    """search Amazon

    You need a license key to call this function; see
    http://www.amazon.com/webservices
    to get one.  Then you can either pass it to
    this function every time, or set it globally; see the module docs for details.

    Parameters:
    keyword - keyword to search
    search_type - in (KeywordSearch, BrowseNodeSearch, AsinSearch, UpcSearch, AuthorSearch, ArtistSearch, ActorSearch, DirectorSearch, ManufacturerSearch, ListManiaSearch, SimilaritySearch)
    product_line - type of product to search for.  restrictions based on search_type
        UpcSearch - in (music, classical)
        AuthorSearch - must be "books"
        ArtistSearch - in (music, classical)
        ActorSearch - in (dvd, vhs, video)
        DirectorSearch - in (dvd, vhs, video)
        ManufacturerSearch - in (electronics, kitchen, videogames, software, photo, pc-hardware)
    http_proxy (optional) - address of HTTP proxy to use for sending and receiving SOAP messages

    Returns: list of Bags, each Bag may contain the following attributes:
      Asin - Amazon ID ("ASIN" number) of this item
      Authors - list of authors
      Availability - "available", etc.
      BrowseList - list of related categories
      Catalog - catalog type ("Book", etc)
      CollectiblePrice - ?, format "$34.95"
      ImageUrlLarge - URL of large image of this item
      ImageUrlMedium - URL of medium image of this item
      ImageUrlSmall - URL of small image of this item
      Isbn - ISBN number
      ListPrice - list price, format "$34.95"
      Lists - list of ListMania lists that include this item
      Manufacturer - manufacturer
      Media - media ("Paperback", "Audio CD", etc)
      NumMedia - number of different media types in which this item is available
      OurPrice - Amazon price, format "$24.47"
      ProductName - name of this item
      ReleaseDate - release date, format "09 April, 1999"
      Reviews - reviews (AvgCustomerRating, plus list of CustomerReview with Rating, Summary, Content)
      SalesRank - sales rank (integer)
      SimilarProducts - list of Product, which is ASIN number
      ThirdPartyNewPrice - ?, format "$34.95"
      URL - URL of this item
    """
    license_key = getLicense(license_key)
    locale = getLocale(locale)
    associate = getAssociate(associate)
    url = buildURL(search_type, searchfield, searchvalue, product_line, type, page, 
            license_key, locale, associate)
    proxies = getProxies(http_proxy)
    u = urllib.FancyURLopener(proxies)
    usock = u.open(url)
    xmldoc = minidom.parse(usock)

#     from xml.dom.ext import PrettyPrint
#     PrettyPrint(xmldoc)

    usock.close()
    data = unmarshal(xmldoc)
    if search_type == "BlendedSearch":
        if hasattr(data, 'BlendedSearch'):
            data = data.BlendedSearch
    elif hasattr(data, 'ItemSearchResponse'):
        data = data.ItemSearchResponse 
    elif hasattr(data, 'ItemLookupResponse'):
        data = data.ItemLookupResponse 

    if hasattr(data, 'Errors'):
        raise AmazonError, data.Errors
    else:
        if search_type == "BlendedSearch":
            return data 
        else:            
            if hasattr(data, 'Items'):
                return data.Items
            else:
                return data

def searchByKeyword(keyword, product_line="Books", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ItemSearch", 'Keywords', keyword, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByTitle(keyword, product_line="Books", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ItemSearch", 'Title', keyword, product_line, type, page, license_key, http_proxy, locale, associate)

def browseBestSellers(browse_node, product_line="Books", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("BrowseNodeSearch", 'Keywords', browse_node, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByASIN(ASIN, type="Large", license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ItemLookup", 'ASIN', ASIN, None, type, None, license_key, http_proxy, locale, associate)

def searchByUPC(UPC, product_line="Books", type="Large", license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ItemLookup", 'UPC', UPC, product_line, type, None, license_key, http_proxy, locale, associate)

def searchByEAN(EAN, product_line="Books", type="Large", license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ItemLookup", 'EAN', EAN, product_line, type, None, license_key, http_proxy, locale, associate)

def searchByAuthor(author, type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("AuthorSearch", 'Keywords', author, "Books", type, page, license_key, http_proxy, locale, associate)

def searchByArtist(artist, product_line="Music", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    if product_line not in ("music", "classical"):
        raise AmazonError, "product_line must be in ('Music', 'Classical')"
    return search("ArtistSearch", 'Keywords', artist, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByActor(actor, product_line="DVD", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    if product_line not in ("DVD", "VHS", "Video"):
        raise AmazonError, "product_line must be in ('DVD', 'VHS', 'Video')"
    return search("ActorSearch", 'Keywords', actor, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByDirector(director, product_line="DVD", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    if product_line not in ("DVD", "VHS", "Video"):
        raise AmazonError, "product_line must be in ('DVD', 'VHS', 'Video')"
    return search("DirectorSearch", 'Keywords', director, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByManufacturer(manufacturer, product_line="pc-hardware", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    if product_line not in ("electronics", "kitchen", "videogames", "software", "photo", "pc-hardware"):
        raise AmazonError, "product_line must be in ('electronics', 'kitchen', 'videogames', 'software', 'photo', 'pc-hardware')"
    return search("ManufacturerSearch", 'Keywords', manufacturer, product_line, type, page, license_key, http_proxy, locale, associate)

def searchByListMania(listManiaID, type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("ListManiaSearch", 'Keywords', listManiaID, None, type, page, license_key, http_proxy, locale, associate)

def searchSimilar(ASIN, type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("SimilaritySearch", 'Keywords', ASIN, None, type, page, license_key, http_proxy, locale, associate)

def searchByWishlist(wishlistID, type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("WishlistSearch", 'Keywords', wishlistID, None, type, page, license_key, http_proxy, locale, associate)

def searchByPower(keyword, product_line="Books", type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("PowerSearch", 'Keywords', keyword, product_line, type, page, license_key, http_proxy, locale, associate)
    # >>> RecentKing = amazon.searchByPower('author:Stephen King and pubdate:2003')
    # >>> SnowCrash = amazon.searchByPower('title:Snow Crash')

def searchByBlended(keyword, type="Large", page=1, license_key=None, http_proxy=None, locale=None, associate=None):
    return search("BlendedSearch", 'Keywords', keyword, None, type, page, license_key, http_proxy, locale, associate)
