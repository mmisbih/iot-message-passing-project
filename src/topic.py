'''
Created on 9. nov. 2017

@author: Andersen
'''

import json
import time

def gettopic(deviceid, msgid, psize):
    #timestamp = str(time.time()).ljust(20,'0') #pad zeros to timestamp!
    timestamp = str(time.perf_counter()).ljust(20,'0')
    size_msg = len(json.dumps({"deviceid":deviceid, "msgid":msgid, "Time":timestamp, "Payload":''}))
    return json.dumps({"deviceid":deviceid, "msgid":msgid, "time":timestamp, "payload":''.ljust(psize)})
   
def gettimediff(topic, time):
    msg = json.loads(topic)
    return time - float(msg['time'])

def getMsgId(topic):
    msg = json.loads(topic)
    return msg['msgid']

def getsize(topic):
    return len(topic)
    
def getDeviceId(topic):
    msg = json.loads(topic)
    return msg['deviceid']