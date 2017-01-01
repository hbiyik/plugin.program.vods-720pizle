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

import channel
import re
from operator import itemgetter

encoding="windows-1254"

class yediyuzyirmiizle(channel.abstract):
    domain = "http://www.720pizle.com"
    art = {
           "icon": "http://720pizle.com/images/logo.png",
           "thumb": "http://720pizle.com/images/logo.png"
           }

    def plus(self, apage):
        pid = re.findall('<div class="plusplayer.*?>(.*?)<', apage)[0]
        q = {"v": pid}
        ppage = self.download("http://720pizle.com/player/plusplayer.asp", \
                              referer=self.domain, \
                              query=q)
        vids = re.findall("file: '(/player.*?)'", ppage)
        return [self.domain + x for x in vids]

    def plusv2(self, apage):
        pid = re.findall('<div class="plusplayer.*?>(.*?)<', apage)[0]
        q = {"v": pid}
        ppage = self.download("http://720pizle.com/player/plusplayer2.asp", \
                              referer=self.domain, \
                              query=q)
        vids = re.findall('video.push\(\{"file":"(.*?)", "label":"(.*?)p"', ppage)
        vids = [[x[0], int(x[1])] for x in vids]
        vids.sort(key=itemgetter(1), reverse=True)
        return [self.domain + x[0] for x in vids]

    def listcats(self):
        page = self.download(self.domain, encoding)
        res = re.findall('class="menu-item".*?href="(.*?)">(.*?)</a>', page)
        for link, desc in res:
            if link == "/":
                continue
            if "imdb" in desc.lower():
                continue
            if "hit" in link:
                desc = u"En Çok İzlenen: " + re.sub("<.*?>", "", desc)
            self.additem(desc, link)

    def listmovies(self, cat=None):
        if self.pageargs:
            u = self.domain + self.pageargs
        else:
            if cat:
                u = self.domain + cat
            else:
                u = self.domain
        page = self.download(u, encoding)
        for item in re.findall('(<div class="film-kategori.*?</small></div>)', page, re.DOTALL):
            title = re.findall('<span class="oval">(.*?)</span>', item)[0]
            links = re.findall('<div class="film-kategori-tr-secenek">(.*?)<img', item)[0]
            links = re.findall('href="(.*?)"', links)
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
                self.setnext(next[0][0], next[0][1])

    def geturl(self, id):
        for lang in id:
            page = self.download(self.domain+lang, encoding)
            alts = re.findall('<a href="(.*?)" rel="nofollow">(.*?)<b class="alternatifrip">', page)
            print alts
            for alink, adesc in alts:
                print alink
                adesc = adesc.lower().replace(" ","")
                apage = self.download(self.domain + alink, encoding)
                if adesc == "plusplayerv2":
                    vids = self.plusv2(apage)
                elif adesc == "plusplayer":
                    vids = self.plus(apage)
            for vid in vids:
                self.play(vid)

                        