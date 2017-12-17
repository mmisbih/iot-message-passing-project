'''
Created on 7. nov. 2017

@author: Andersen
'''

from mqttClient import mqttClient 
import time
from topic import gettopic, gettimediff, getMsgId, getDeviceId

topic = 'my/topic'
message = '2'
# URL cloud: mqtt://yvqmqips:zqFw7ym66Lyk@m23.cloudmqtt.com:1103
# URL local: 
url = 'mqtt://iotgroup4:iot4@192.168.43.104:1883'
url_local = 'mqtt://localhost:1883'
x = []
y = []

def on_message(client, userdata, msg):
    timestamp = time.time()
    print("Topic: "+msg.topic+" DeviceId: "+str(getDeviceId(msg.payload))+" MsgId: "+ str(getMsgId(msg.payload))+" Time: "+str(gettimediff(msg.payload, timestamp)))
    x+[gettimediff(msg.payload, timestamp)]
    y+[getMsgId(msg.payload)]
    

local_client_1 = mqttClient('1',url)
local_client_2 = mqttClient('2',url)

local_client_1.connect()
local_client_2.connect()

local_client_1.subscribe(topic={'topic':topic, 'qos':0, 'cb':on_message}, kwargs={'timeout':15})

local_client_2.publish(topic={'topic':topic, 'psize':1000000, 'qos':0}, kwargs={'nr':10, 'ival':1})

local_client_1.waitForClient()
local_client_2.waitForClient()
