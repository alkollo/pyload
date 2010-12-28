# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.
    
    @author: mkaay, RaNaN
"""

from threading import Lock

from Browser import Browser
from Bucket import Bucket
from HTTPRequest import HTTPRequest
from CookieJar import CookieJar

class RequestFactory():
    def __init__(self, core):
        self.lock = Lock()
        self.core = core
        self.bucket = Bucket()
        self.updateBucket()
        self.cookiejars = {}

    def getRequest(self, pluginName, account=None):
        self.lock.acquire()

        req = Browser(self.core.config["download"]["interface"], self.bucket, self.getProxies())

        if account:
            cj = self.getCookieJar(pluginName, account)
            req.setCookieJar(cj)
        else:
            req.setCookieJar(CookieJar(pluginName))

        self.lock.release()
        return req

    def getURL(self, url, get={}, post={}):
        h = HTTPRequest(None, self.core.config["download"]["interface"], self.getProxies())
        rep = h.load(url, get, post)
        h.close()
        return rep

    def getCookieJar(self, pluginName, account=None):
        if self.cookiejars.has_key((pluginName, account)):
            return self.cookiejars[(pluginName, account)]

        cj = CookieJar(pluginName, account)
        self.cookiejars[(pluginName, account)] = cj
        return cj

    def getProxies(self):
        """ returns a proxy list for the request classes """
        if not self.core.config["download"]["proxy"]:
            return {}
        else:
            type = "http"
            setting = self.core.config["proxy"]["type"].lower()
            if setting == "socks4": type = "socks4"
            if setting == "socks5": type = "socks5"

            username = None
            if self.core.config["proxy"]["username"] and self.core.config["proxy"]["username"].lower() != "none":
                username = self.core.config["proxy"]["username"]

            pw = None
            if self.core.config["proxy"]["password"] and self.core.config["proxy"]["password"].lower() != "none":
                pw = self.core.config["proxy"]["password"]

            return {
                "type": type,
                "address": self.core.config["proxy"]["address"],
                "port": self.core.config["proxy"]["port"],
                "username": username,
                "password": pw,
            }

    def updateBucket(self):
        """ set values in the bucket according to settings"""
        if not self.core.config["download"]["limit_speed"]:
            self.bucket.setRate(-1)
        else:
            self.bucket.setRate(self.core.config["download"]["max_speed"] * 1024)

# needs pyreq in global namespace
def getURL(url, get={}, post={}):
    return pyreq.getURL(url, get, post)