# Generates a list of every page on pathofexile.gamepedia.com
# This list is used to find the most appropriate page for a user's request.

# Imports
import pickle
import requests
from bs4 import BeautifulSoup

def getPages():
    print("Getting pages...", end=" ")
    pages = dict()
    def getSet(url):
        r = requests.get('http://www.pathofexile.gamepedia.com' + url)
        soup = BeautifulSoup(r.content, 'html.parser')
        allPages = soup.find("div", { "class" : "mw-allpages-body"})
        links = allPages.findAll("li")
        for link in links:
            aTag = link.find("a")
            pages[str(aTag.string)] = aTag["href"]
        nav = soup.find("div", { "class" : "mw-allpages-nav"})
        for link in nav.findAll("a"):
            if "Next page" in link.string:
                return link["href"]
        return None

    url = "/Special:AllPages"
    while url:
        url = getSet(url)
    with open('pages.pickle', 'wb') as handle:
        pickle.dump(pages, handle)
    print("finished.")
