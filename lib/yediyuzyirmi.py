# -*- coding: utf-8 -*-
'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2016
    License   : GPL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import vods
import re
from operator import itemgetter

encoding = "windows-1254"


class yediyuzyirmiizle(vods.movieextension):
    domain = "http://www.720pizle.com"
    info = {
        "title": "720pizle"
        }
    art = {
           "icon": "http://720pizle.com/images/logo.png",
           "thumb": "http://720pizle.com/images/logo.png"
           }

    def plus(self, apage):
        pid = re.findall('<div class="plusplayer.*?>(.*?)<', apage)[0]
        q = {"v": pid}
        ppage = self.download("http://720pizle.com/player/plusplayer.asp", \
                              referer=self.domain, \
                              params=q)
        vids = re.findall("file: '(/player.*?)'", ppage)
        return [[self.domain + x, 480] for x in vids]

    def plusv2(self, apage):
        pid = re.findall('<div class="plusplayer.*?>(.*?)<', apage)[0]
        q = {"v": pid}
        ppage = self.download("http://720pizle.com/player/plusplayer2.asp", \
                              referer=self.domain, \
                              params=q)
        vids = re.findall('"file":"(.*?)".*?"label":"([0-9]*)', ppage)
        vids = [[x[0], int(x[1])] for x in vids]
        print vids
        return vids

    def jsfunc(self, apage, fname, pattern, qual):
        oids = re.findall(fname + "\('(.*?)'", apage)
        vids = []
        for oid in oids:
            vids.append([pattern % oid, qual])
        return vids

    def movshare(self, apage):
        oids = re.findall("movshare\('(.*?)'", apage)
        vids = []
        for oid in oids:
            vids.append(["https://openload.co/embed/%s/" % oid, 720])
        return vids

    def scrapegrid(self, page):
        for item in re.findall('(<div class="film-kategori.*?</small></div>)', page, re.DOTALL):
            title = re.findall('<span class="oval">(.*?)</span>', item)[0]
            links = re.findall('<div class="film-kategori-tr-secenek">(.*?)</div', item)[0]
            links = re.findall('href="(/izle.*?)"', links)
            img = re.findall('<img src="(.*?)"', item)[0]
            stars = re.findall('<span class="c">(.*?)\/', item)[0]
            stars = float(stars.replace(",", "."))
            info = {
                    "title": title,
                    "rating": stars,
                    }
            art = {
                   "thumb": img,
                   "icon": img,
                   }
            self.additem(title, links, info, art)
        next = re.findall('<li class="active">.*?<li ><a href="(.*?)" title="(.*?)">[0-9]*?</a></li>', page, re.DOTALL)
        if len(next):
            self.setnextpage(next[0][0], next[0][1])

    def getcategories(self):
        page = self.download(self.domain, encoding=encoding)
        res = re.findall('class="menu-item".*?href="(.*?)">(.*?)</a>', page)
        for link, desc in res:
            if link == "/":
                continue
            if "imdb" in desc.lower():
                continue
            if "hit" in link:
                desc = u"En Çok İzlenen: " + re.sub("<.*?>", "", desc)
            self.additem(desc, link)

    def getmovies(self, cat=None):
        if self.page:
            u = self.domain + self.page
        else:
            if cat:
                u = self.domain + cat
            else:
                u = self.domain
        page = self.download(u, encoding=encoding)
        self.scrapegrid(page)

    def searchmovies(self, keyw):
        q = {"a": keyw}
        page = self.download(self.domain + "/ara.asp", \
                             encoding=encoding,
                             params=q,
                             referer=self.domain
                             )
        self.scrapegrid(page)

    def geturls(self, id):
        for lang in id:
            page = self.download(self.domain + lang, encoding=encoding)
            alts = re.findall('<a href="(.*?)" rel="nofollow">(.*?)<b class="alternatifrip">', page)
            print alts
            vids = []
            for alink, adesc in alts:
                adesc = adesc.lower().replace(" ", "")
                apage = self.download(self.domain + alink, encoding=encoding)
                if adesc == "plusplayerv2":
                    vids.extend(self.plusv2(apage))
                elif adesc == "plusplayer":
                    vids.extend(self.plus(apage))
                elif adesc == "openload":
                    pattern = "https://openload.co/embed/%s/"
                    vids.extend(self.jsfunc(apage, "openload", pattern, 720))
                elif adesc == "movshare":
                    pattern = "http://www.wholecloud.net/embed/?v=%s"
                    vids.extend(self.jsfunc(apage, "movshare", pattern, 720))
                elif adesc == "mail.ru":
                    pattern ="http://videoapi.my.mail.ru/videos/embed/%s"
                    vids.extend(self.jsfunc(apage, "mailru", pattern, 480))
                elif adesc == "uptobox":
                    pattern ="http://uptostream.com/%s"
                    vids.extend(self.jsfunc(apage, "uptobox", pattern, 480))
            vids.sort(key=itemgetter(1), reverse=True)
            for vid, qual in vids:
                yield vid

    def cachemovies(self, id):
        url = "/detay/" + id[0].split("/")[-1]
        page = self.download(self.domain + url, encoding=encoding)
        map = {
               u"Yönetmen": ["director",""],
               u"Vizyon Tarihi": ["year", "1 Ocak 1000"],
               u"IMDB": ["rating", "0"],
               u"Süre": ["duration", "0 Dakika"],
               u"Tür": ["genre", ""],
               }
        info = {}
        for k, v in map.iteritems():
            key, dfl = v
            try:
                str = re.findall(k + "\:</span>(.*?)</li", page, re.UNICODE)[0]
                str = re.sub("<.*?>", "", str)
                str = str.replace(u"\xa0", "")
                info[key] = str
            except:
                info[key] = dfl
        info["year"] = int(info["year"][-4:])
        info["rating"] = float(info["rating"].replace(",", "."))
        info["duration"] = int(info["duration"].replace("Dakika", ""))*60
        title = re.search("<h1>(.+?)\([0-9]{4}\)<\/h1>", page)
        if title:
            info["title"] = title.group(1)
        plot = re.findall("<hr>(.*?)</div>", page, re.DOTALL)
        if plot:
            plot = re.sub("<.*?>", "", plot[0])
            info["plot"] = plot.strip()
            info["plotoutline"] = plot.strip()
        cast = re.findall('<div class="oyuncuadi"><span>(.*?)</span>', page)
        if cast:
            info["cast"] = cast
        if info["year"] == 1000:
            year = re.findall("\(([0-9]*?)\)</h1>", page)
            if year:
                info["year"] = int(year[0])
        return info, {}
