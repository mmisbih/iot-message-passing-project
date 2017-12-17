'''
Created on 7. nov. 2017

@author: Andersen
'''

import paho.mqtt.client as mqtt
from IClient import IClient
import os
import time
from urllib.parse import urlparse
from paho.mqtt import publish
from topic import gettopic, gettimediff
import threading

# URL cloud: mqtt://yvqmqips:zqFw7ym66Lyk@m23.cloudmqtt.com:1103
# URL local: 'mqtt://iotgroup4:iot4@192.168.43.104:1883'

class mqttClient(IClient):
    '''
    classdocs
    '''

    def __init__(self, cid, url):
        '''
        Constructor
        '''
        self.mqttc = mqtt.Client()
        self.pt = None
        self.st = None
        self.connected = False
        self.subscribed = False
        url_str = os.environ.get(url) #, 'mqtt://localhost:1883')
        url_parse = urlparse(url_str)
        self.mqttc.username_pw_set('iotgroup4', 'iot4')
        self.hostname = '80.196.35.233'
        self.port = 1883
        self.id = str(cid)
        
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_subscribe = self.on_subscribe
        #self.mqttc.on_log = self.on_log
        
    def connect(self):
        #self.mqttc.connect(self.hostname, self.port, keepalive = 180 )
        self.mqttc.connect(self.hostname, self.port)
        self.mqttc.loop_start()
        self.waitForConnect()
    
    def isConnected(self):
        return self.connected != None
    
    def disconnect(self):
        self.mqttc.loop_stop()
        self.mqttc.disconnect()
    
	# self, topic={'topic':'', 'qos':''} kwargs = {'timeout':'', 'cb':''}
    def subscribe(self, topic, kwargs):
        self.mqttc.on_message = topic['cb']
        self.mqttc.subscribe(topic['topic'], topic['qos'])
        self.waitForSubscribed()
	
	# self, topic={'topic':'', 'psize':'', 'qos':''} kwargs = {'nr':'', 'ival':''}
    def publish(self, topic, kwargs):
        self.pt = threading.Thread(target=self.publishfunc, args=(topic, kwargs))
        self.pt.start() 
    
	# self, topic={'topic':'', 'psize':'', 'qos':''} kwargs = {'nr':'', 'ival':''}
    def publishfunc(self, topic, kwargs):
        for i in range(kwargs['nr']):
            self.mqttc.publish(topic['topic'], gettopic(self.id, i, topic['psize']), topic['qos'])
            time.sleep(kwargs['ival'])
        self.disconnect()
    
	# self, topic={'topic':'', 'qos':''} kwargs = {'timeout':'', 'cb':''}
    def subscribefunc(self, topic, kwargs):
        time.sleep(kwargs['timeout'])
        
        self.disconnect()
    
    def start_subscribe_timeout(self, topic, kwargs):
        self.st = threading.Thread(target=self.subscribefunc, args=(topic, kwargs))
        self.st.start();
        
    def waitForClient(self):
        if self.pt != None:
            self.pt.join()
        if self.st != None:
            self.st.join()
     
    def waitForConnect(self):
        while(self.connected == False):
            pass
    
    def waitForSubscribed(self):
        while(self.subscribed == False):
            pass
    '''
    Callbacks
    '''
    def on_disconnect(self, client, userdata, rc):
        #print(self.id + 'disconnected with the result code ' + mqtt.connack_string(rc))
        self.mqttc.loop_stop()
        
    def on_connect(self, client, userdata, flags, rc):
        #print(self.id + ' Connected with the result code '+mqtt.connack_string(rc))
        self.connected = True
        
    
    def on_log(self, client, obj, level, string):
        #print(string)
        pass
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        #print(str(self.id)+'on_suscribe')
        self.subscribed = True