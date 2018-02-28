# -*- coding: utf-8 -*-
#Библиотеки, които използват python и Kodi в тази приставка
import re
import sys
import os
import urllib
import urllib2
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import base64
import json
#import xbmcvfs
import cookielib

#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
__addon_id__= 'plugin.video.flixtor'
__Addon = xbmcaddon.Addon(__addon_id__)
__addondir__= xbmc.translatePath(__Addon.getAddonInfo('profile'))
searchicon = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/search.png")
baseurl = base64.b64decode('aHR0cHM6Ly9mbGl4dG9yLnRv')
MUA = 'Mozilla/5.0 (Linux; Android 5.0.2; bg-bg; SAMSUNG GT-I9195 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19' #За симулиране на заявка от мобилно устройство
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu/16.04.3 Chrome/64.0.3282.140 Safari/537.36' #За симулиране на заявка от  компютърен браузър

#init
url = (baseurl+'/')
req = urllib2.Request(url)
req.add_header('User-Agent', UA)
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
f = opener.open(req)
data = f.read()
#Меню с директории в приставката
def CATEGORIES():
        addDir('Търсене на видео',baseurl+'/show/search/',2,searchicon)
        addDir('Филми',baseurl + '/ajax/show/movies/all/from/1900/to/2099/rating/0/votes/0/language/all/latest/page/1',1,'DefaultFolder.png')
        addDir('Сериали',baseurl + '/ajax/show/tvshows/all/from/1900/to/2099/rating/0/votes/0/language/all/latest/page/1',1,'DefaultFolder.png')


#Разлистване видеата на първата подадена страница
def INDEXPAGES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        data = f.read()
        f.close()
        print 'tovaurle' + url
        #Начало на обхождането
        br = 0 #Брояч на видеата в страницата - 24 за този сайт
        match = re.compile('alt="(.+?)" src="(.+?)".+?normal">(.+?)<.+?data-href="(.+?)"').findall(data)
        for zaglavie,kartinka,godina,link in match:
            thumbnail = 'https:' + kartinka 
            desc = 'ГОДИНА: ' + godina
            #url = baseurl + '/ajax/gvid/m/' + link
            vid = baseurl + link
            addLink(zaglavie,vid,3,desc,thumbnail)
            br = br + 1
            print 'Items counter: ' + str(br)
        if br == 24: #тогава имаме следваща страница и конструираме нейния адрес
            getpage=re.compile('(.+?)/page/(.*)').findall(url)
            for newurl,page in getpage:
               newpage = int(page)+1
               url = newurl + '/page/' + str(newpage)
               print 'URL OF THE NEXT PAGE IS-' + url
               thumbnail='DefaultFolder.png'
               addDir('следваща страница>>',url,1,thumbnail)


#Търсачка
def SEARCH(url):
        keyb = xbmc.Keyboard('', 'Търси..')
        keyb.doModal()
        searchText = ''
        if (keyb.isConfirmed()):
            searchText = urllib.quote_plus(keyb.getText())
            searchText=searchText.replace(' ','%20')
            searchurl = baseurl + '/ajax/show/search/' + searchText + '/from/1900/to/2099/rating/0/votes/0/language/all/relevance/page/1'
            #searchurl = searchurl.encode('utf-8')
            print 'SEARCHING:' + searchurl
            INDEXPAGES(searchurl)


        else:
             addDir('Върнете се назад в главното меню за да продължите','','',"DefaultFolderBack.png")

def rot47(s):
    x = []
    for i in range(len(s)):
        j = ord(s[i])
        if j >= 33 and j <= 126:
            x.append(chr(33 + ((j + 14) % 94)))
        else:
            x.append(s[i])
    return ''.join(x)

#Зареждане на видео
def PLAY(url):
        try:
         req = urllib2.Request(url)
         req.add_header('User-Agent', UA)
         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
         f = opener.open(req)
         data = f.read()
         match1 = re.compile('.+?/watch/.+?/(.+?)/').findall(url)
         for link in match1:
          #print link       
          zlink = baseurl + '/ajax/gvid/m/' + link
          #print zlink
          req = urllib2.Request(zlink)
          req.add_header('User-Agent', UA)
          opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
          f = opener.open(req)
          data = f.read()
          #print data
          html = base64.b64decode(data.encode("rot13"))
          links = (rot47(html))
          jsonrsp = json.loads(links)
          path0 = jsonrsp['file']
          #print path0
          path = path0.replace('master.m3u8', '720p')
          #print path
          req = urllib2.Request(path)
          req.add_header('User-Agent', UA)
          opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
          f = opener.open(req)
          data = f.read()
          match = re.compile('(https://.+?/.+?/)p').findall(path)
          for link in match:
           matchl = re.compile('(https://.+?)/(.*)').findall(link)
           for first, second in matchl:
           #print data
            data2 = data.replace('/'+second, link).replace('.bin', '.ts')
            file = open(__addondir__+'play.m3u', 'w')
            file.write(data2)
            file.close()
            finalurl = (__addondir__+'play.m3u8')
            li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=finalurl)
            li.setInfo('video', { 'title': name })
            try:
              xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
            except:
              xbmc.executebuiltin("Notification('Грешка','Видеото липсва на сървъра!')")
        except:
         req = urllib2.Request(url)
         req.add_header('User-Agent', UA)
         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
         f = opener.open(req)
         data = f.read()
         match1 = re.compile('.+?/watch/.+?/(.+?)/').findall(url)
         for link in match1:
          #print link       
          zlink = baseurl + '/ajax/gvid/m/' + link
          #print zlink
          req = urllib2.Request(zlink)
          req.add_header('User-Agent', UA)
          opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
          f = opener.open(req)
          data = f.read()
          #print data
          html = base64.b64decode(data.encode("rot13"))
          links = (rot47(html))
          jsonrsp = json.loads(links)
          path0 = jsonrsp['file']
          #print path0
          path = path0.replace('master.m3u8', '360p')
          #print path
          req = urllib2.Request(path)
          req.add_header('User-Agent', UA)
          opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
          f = opener.open(req)
          data = f.read()
          match = re.compile('(https://.+?/.+?/)p').findall(path)
          for link in match:
           matchl = re.compile('(https://.+?)/(.*)').findall(link)
           for first, second in matchl:
           #print data
            data2 = data.replace('/'+second, link).replace('.bin', '.ts')
            file = open(__addondir__+'play.m3u', 'w')
            file.write(data2)
            file.close()
            finalurl = (__addondir__+'play.m3u8')
            li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=finalurl)
            li.setInfo('video', { 'title': name })
            try:
              xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
            except:
              xbmc.executebuiltin("Notification('Грешка','Видеото липсва на сървъра!')")

#Модул за добавяне на отделно заглавие и неговите атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addLink(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage})
        liz.setInfo(type="Video", infoLabels={"Title": name, "plot": plot})
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

#Модул за добавяне на отделна директория и нейните атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage})
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def log(txt, loglevel=xbmc.LOGDEBUG):
    if (__addon__.getSetting( "logEnabled" ) == "true") or (loglevel != xbmc.LOGDEBUG):
        if isinstance (txt,str):
            txt = txt.decode("utf-8")
        message = u'%s: %s' % (__addonid__, txt)
        xbmc.log(msg=message.encode("utf-8"), level=loglevel)

#НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param







params=get_params()
url=None
name=None
iconimage=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        name=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass


#Списък на отделните подпрограми/модули в тази приставка - трябва напълно да отговаря на кода отгоре
if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
    
elif mode==1:
        print ""+url
        INDEXPAGES(url)

elif mode==2:
        print ""+url
        SEARCH(url)
        
elif mode==3:
        print ""+url
        PLAY(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
