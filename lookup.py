import requests
import pickle
import itertools
from collections import Counter
from difflib import SequenceMatcher
from bs4 import BeautifulSoup

def supers(text):
    response = " "
    split = text.split()
    for i in range(len(split)):
        if i != 0:
            response += " "
        response += "^" + split[i]
    return response

def findItem(name):
    name = name.replace("'","%27")

    #Ignore comments made by this bot.
    if name == "Wiki" or name == "item names":
        return ""

    with open('pages.pickle', 'rb') as handle:
        pages = pickle.load(handle)

    pageScores = {}
    for key in pages:
        pageScores[pages[key]] = SequenceMatcher(None, name, key).ratio()
    bestPages = Counter(pageScores).most_common(1)
    print(bestPages)
    for page in bestPages:
        test = itemLookup(page[0])
        if test != "":
            return test

    return ""

def printNonUnique(itemStats, itemMods, itemURL, response):
    for item in itemStats.children:
        try:
            temp = ""
            for child in item.children:
                if child.string:
                    temp += supers(child.string)
            response += temp
            if temp == "":
                response += " ^| "
        except:
            response += supers(item)
    response += "\n\n"

    #Print Mods
    for i in range(len(itemMods)):
        for item in itemMods[i].children:
            if item.string:
                if len(itemMods) == 2 and i == 0:
                    response += "*" + item.string + "*"
                else:
                    response += item.string
            else:
                response += "\n\n"
        response += "\n\n"
    return response

def printUnique(itemStats, itemMods, itemURL, itemFlavour, response):
    response += "\n\n"

    #Print item Stats
    response += "####"
    for item in itemStats.children:
        try:
            temp = ""
            for child in item.children:
                if child.string:
                    try:
                        if "-value" in dict(child.attrs)["class"]:
                            temp += "**" + child.string + "**"
                        else:
                            temp += child.string
                    except:
                        temp += child.string
                else:
                    response += "\n\n####"
            response += temp
            if temp == "":
                response += "\n\n####"
        except:
            response += item
    response += "\n\n"

    response += "[](#line)\n\n"

    #Print Mods
    for i in range(len(itemMods)):
        response += "#####"
        for item in itemMods[i].children:
            if item.string:
                    response += item.string
            else:
                response += "\n\n#####"
        response += "\n\n[](#line)\n\n"

    #Print flavour
    response += "*"
    for item in itemFlavour.children:
        if item.string:
                response += item.string.strip()
        else:
            response += "*\n\n*"
    response += "*"
    return response;


def itemLookup(page):
    # Try a URL
    r = requests.get("http://www.pathofexile.gamepedia.com" + page, timeout = 0.5)
    if r.status_code == 404:
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    itemspan = soup.find("span", { "class" : "infobox-page-container"})

    # Break if an invalid page has been reached
    if not itemspan:
        return ""

    itemspan = itemspan.find("span", { "class" : "item-box" })
    isUnique = "-unique" in dict(itemspan.attrs)["class"]

    # Get item title
    itemTitleRaw = itemspan.find("span", { "class" : "header"}).children
    itemTitle = ""
    itemTitleU = "#####"
    for item in itemTitleRaw:
        if item.string:
            itemTitle += item.string + " "
            itemTitleU += item.string
        else:
            itemTitleU +=  " [](#break) "
    itemTitle = itemTitle[:-1]

    # Get item stats
    itemStats = itemspan.find("span", { "class" : "item-stats"}).find("span")

    # Get item mods
    itemMods = itemspan.findAll("span", { "class" : "-mod"})

    # Get item flavour
    itemFlavour = itemspan.find("span", { "class" : "-flavour"})

    # Get image URL
    itemURL = itemspan.findAll("a", { "class" : "image"})[0].img["src"]


    # Print
    response = ""
    response += "[**" + itemTitle + "**](" + itemURL + ")"
    response += "[[Wiki]](http://www.pathofexile.gamepedia.com/" + page + ")\n\n"

    # Print Stats
    if not isUnique:
        return printNonUnique(itemStats, itemMods, itemURL, response)
    else:
        response += itemTitleU
        return printUnique(itemStats, itemMods, itemURL, itemFlavour, response)
