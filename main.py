
import httpx
import json
import time
import sys
import urllib
import discord
from headers import Headers
from random import randrange

class OmegleClient:
    def __init__(self, topics, invite, spy):
        self.session = httpx.Client(http2=True)
        self.topics = ""
        self.cserver = ""
        self.status = {}
        self.clientID = ""
        self.identDigests = ""
        self.temp = """%5B%22furry%22%5D"""
        self.tardsmessaged = int()
        self.connected = False
        
        self.__randid = ''
        self.__randidarray = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        self.GenRandID()
        self.HandleStatus()
        self.Topics(topics)

    def GenRandID(self):
        self.__randid = ''
        while len(self.__randid) < 8:
            self.__randid += self.__randidarray[randrange(0, len(self.__randidarray))]

    def HandleStatus(self):
        self.status = (self.session.get("http://front38.omegle.com/status", headers=Headers.getStatus)).json()

    def Topics(self, Topics):
        if isinstance(Topics, list):
            self.topics = ((urllib.parse.urlencode({'topics': Topics})).replace("+","").replace("%27","%22")).replace("topics=", "")
        else:
            print("Insert a list please")

    def Connect(self):
        self.cserver = self.status['servers'][randrange(0,len(self.status['servers']))]
        print(self.cserver)
        r = (self.session.post("http://%s.omegle.com/start?caps=recaptcha2,t&firstevents=1&spid=&randid=%s&topics=%s&lang=en" % (self.cserver, self.__randid, self.topics), headers=Headers.startChat)).json()
        eventjson = r['events']
        self.clientID = r['clientID']
        self.connected = True
        self.ProcEvents(eventjson)

    def ProcEvents(self, eventjson):
        while self.connected == True:
            for event in eventjson:
                if event[0] == 'strangerDisconnected':
                    self.connected = False
                    self.OnDisconnect()
                elif event[0] == 'connected':
                    self.OnConnect()
                elif event[0] == 'waiting':
                    self.OnWait()
                elif event[0] == 'gotMessage':
                    self.OnGotMessage(event[1])
                elif event[0] == 'statusInfo':
                    self.status = event[1]
                elif event[0] == 'identDigests':
                    self.identDigests = event[1]
                elif event[0] == 'typing':
                    self.OnTyping()
                elif event[0] == 'stoppedTyping':
                    self.OnStoppedTyping()
            
            print(eventjson)
            if eventjson == [] or eventjson[0][0] != 'strangerDisconnected':
                self.GetEvents()
        
    def GetEvents(self):
        print("Polled")
        r = (self.session.post("http://%s.omegle.com/events" % self.cserver,headers=Headers.getEvents,data='id=%s' % self.clientID, timeout=80.0)).json()
        if r is not None or r == []:
            self.ProcEvents(r)
        else:
            print(r)
        
    def SendMessage(self, m):
        return (self.session.post('http://%s.omegle.com/send' % self.cserver,headers=Headers.sendData,data='msg=%s&id=%s' % (m, self.clientID))).text

    def SetTypingStatus(self, status):
        if status == True:
            return(self.session.post('http://%s.omegle.com/typing' % self.cserver,headers=Headers.sendData,data='id=%s' % self.clientID)).text
        else:
            return(self.session.post('http://%s.omegle.com/stoppedtyping' % self.cserver,headers=Headers.sendData,data='id=%s' % self.clientID)).text

    def Disconnect(self):
        self.connected = False
        return(self.session.post('https://%s.omegle.com/disconnect' % self.cserver,headers=Headers.sendData,data='id=%s' % self.clientID)).text

    def OnDisconnect(self):
        pass
    
    def OnConnect(self):
        pass

    def OnWait(self):
        pass
        
    def OnGotMessage(self,M):
        pass
    
    def OnTyping(self):
        pass
    
    def OnStoppedTyping(self):
        pass

class Client(OmegleClient):
    def OnConnect(self):
        print("Connected")
        self.SetTypingStatus(True)
        time.sleep(1)
        #self.SendMessage('Yiff D1scord 8BguJBZc')
        self.SendMessage("My name is Ethan!!!!!, Im 19 years old gay furry femboy!!!!!!! Looking for ERP and friendship with no limits, i got no limits on any fetishes, dont worry I dont bite. Much :). I'm a bottom, Looking for a load to take :3 (Or we can just talk~)! My D1$cord is cr0ss#4421, lets talk!!!!")
        self.SetTypingStatus(False)
        time.sleep(3)
        print(self.Disconnect())
            

r = Client(['yiff','furry','fur'],"",1)

count = 1

while True:
    try:
        r.Connect()
        count += 1
        print(count)
        time.sleep(3)
    except Exception as e:
        print("error:")
        print(e)
        time.sleep(100)
        r.Connect()


