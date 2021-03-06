import re
from bs4 import BeautifulSoup
from time import sleep
import pickle

import praw
import OAuth2Util
from allpages import getPages
from lookup import findItem

r = praw.Reddit('bot1')

m = re.compile(r"\[\[[^\]]*\]\]")

def respond(lim, rate, subs):
    with open('ids.pickle', 'rb') as handle:
        ids = pickle.load(handle)
    i = 0
    while True:
        if i % 100 == 0:
            getPages()
        i += 1
        for sub in subs:
            subreddit = r.subreddit(sub)
            for submission in subreddit.new(limit=lim):
                comment_queue = submission.comments[:]
                while comment_queue:
                    com = comment_queue.pop(0)
                    if "[[" in com.body and "]]" in com.body and com.id not in ids:
                        print("Found Comment:" + com.id)
                        reply = ""
                        for item in m.findall(com.body)[:10]:
                            isPOE = sub.lower()=="pathofexile"
                            temp = findItem(item[2:-2], isPOE)
                            reply += temp
                            if temp != "":
                                reply += "\n\n---------\n\n"
                        if reply != "":
                            reply += " ^I ^am ^a ^bot. ^Reply ^to ^me ^with ^up ^to ^7 ^[[item names]]."
                            reply += " ^Please ^contact ^/u/liortulip, ^my ^creator"
                            reply += " ^with ^any ^questions ^or ^concerns. ^Thanks!"
                            print("Replying...")
                            com.reply(reply)
                        else:
                            print("False Reply ^")
                        ids.append(com.id)
                    comment_queue.extend(com.replies)
        with open('ids.pickle', 'wb') as handle:
            pickle.dump(ids, handle, protocol=pickle.HIGHEST_PROTOCOL)
        sleep(rate)

respond(50,10, ["test"])
