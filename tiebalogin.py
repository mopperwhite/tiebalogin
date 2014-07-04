#!/usr/bin/env python
#encoding=UTF-8
#  
#  Copyright 2014 MopperWhite <mopperwhite@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
import cookielib,os,time,urllib2,urllib
import BeautifulSoup as BS
HEADER={
                "Accept":"text/html,*/*;q=0.8",
                "Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Cache-Control":"max-age=0",
                "Connection":"keep-alive",
                "Host":"tb.himg.baidu.com",
                "Referer":None,
                "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
                }
TIME_OUT=20

class LoginWebView(QWebView):
        def __init__(self,url,cookie_file,parent=None):
                super(QWebView,self).__init__(parent)
                self._url=url
                self._cookie_file=cookie_file
        def login(self):
                if os.path.exists(self._cookie_file):
                        self.__qncj=QNetworkCookieJar()
                else:
                        self.__qncj=self._MozillaCookieJar_to_QnetworkCookieJar(self._cookie_file)
                self.page().networkAccessManager().setCookieJar(self.__qncj)
                self.setUrl(QUrl(self._url))
                self.show()
        def closeEvent(self,ev):
                self.cookiejar=self._QNetworkCookieJar_to_MozillaCookieJar(self.__qncj,self._cookie_file)
        @staticmethod
        def _QNetworkCookieJar_to_MozillaCookieJar(qncj,cookie_file):
                f=open(cookie_file,'w')
                print >>f,"# Netscape HTTP Cookie File"
                print >>f,"# http://curl.haxx.se/rfc/cookie_spec.html"
                print >>f,"# This is a generated file!  Do not edit."
                print >>f
                for c in qncj.allCookies():
                        domain=unicode(QString(c.domain()))
                        initial_dot=unicode(domain.startswith(".")).upper()
                        path=unicode(QString(c.path()))
                        isSecure=str(c.isSecure()).upper()
                        expires=unicode(c.expirationDate().toTime_t())
                        name=unicode(QString(c.name()))
                        value=unicode(QString(c.value()))
                        print >>f, "\t".join([ domain,initial_dot,path,isSecure,expires,name,value ])
                f.close()
                mcj=cookielib.MozillaCookieJar(cookie_file)
                mcj.load()
                return mcj
        @staticmethod
        def _MozillaCookieJar_to_QnetworkCookieJar(cookie_file):
                def line2qcookie(line):
                        domain,initial_dot,path,isSecure,expires,name,value=line.split()
                        isSecure=(isSecure=="TRUE")
                        dt=QDateTime()
                        dt.setTime_t(int(expires))
                        expires=dt
                        c=QNetworkCookie()
                        c.setDomain(domain)
                        c.setPath(path)
                        c.setSecure(isSecure)
                        c.setExpirationDate(expires)
                        c.serName(name)
                        c.setValue(value)
                        return c
                cj=QNetworkCookieJar()
                cj.setAllCookies([line2qcookie(line) for line in open(cookie_file)  if not line.startswith("#") and not line])
                return cj
                
                
def open_url(url,cookiejar):
        header={
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip,deflate,sdch",
"Accept-Language":"zh-CN,zh;q=0.8",
"Connection":"keep-alive",
"Host":"tieba.baidu.com",
"Referer":url,
"User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
}
        req = urllib2.Request(url,None,header)
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
	return opener.open(req)
def post_url(url,cookiejar,post_dict,referer=""):
        header={
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip,deflate,sdch",
"Accept-Language":"zh-CN,zh;q=0.8",
"Connection":"keep-alive",
"Host":"tieba.baidu.com",
"Referer":referer,
"User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
}
        d=urllib.urlencode(post_dict)
        req = urllib2.Request(url,None,header)
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        return opener.open(req,d,TIME_OUT)
def check_login(cookie_file):
        mcj=cookielib.MozillaCookieJar(cookie_file)
        mcj.load()
        soup=BS.BeautifulSoup(open_url("http://wapp.baidu.com/",mcj).read())
        print soup.body.div.text
        if soup.body.div.text==u'登录&#160;注册':
                return None
        else:
                return mcj
def initial_login(cookie_file):
        app=QApplication([])
        window=LoginWebView("http://passport.baidu.com",cookie_file)
        window.login()
        app.exec_()
        return window.cookiejar
def login(cookie_file):
        if os.path.exists(cookie_file):
                print True
                check=check_login(cookie_file)
                if check is not None:
                        return check
        return initial_login(cookie_file)

def wap_submit_co(kz,cookiejar,text):
        page_url="http://tieba.baidu.com/mo/q---D911C290B25D3B4777AC40593A557281%3AFG%3D1--1-3-0----wapp_1404445098952_929/m?kz="+str(kz)
        submit_url="http://tieba.baidu.com/mo/q---D911C290B25D3B4777AC40593A557281%3AFG%3D1--1-3-0--2--wapp_1404445098952_929/submit"
        pagedata=open_url(page_url,cookiejar).read()
        open("cutout.html",'w').write(pagedata)
        soup=BS.BeautifulSoup(pagedata)
        form=soup.find("form",{"action":"submit"})
        post_dict=[(h.get("name"),h.get("value").encode("utf-8")) for h in form.findAll("input",{"type":"hidden"})]
        post_dict.append(("co",text.encode("utf-8")))
        post_dict.append(("sub1",u"回贴".encode("utf-8")))
        return post_url(submit_url,cookiejar,post_dict,page_url)
if __name__=='__main__':
        login("test.cookie")
        print bool(check_login("test.cookie"))
        
