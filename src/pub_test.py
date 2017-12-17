import numpy as np
from amqpClient import amqpClient
from mqttClient import mqttClient
import matplotlib.pyplot as plt
from csv_helper import write_to_csv
from threading import Lock
import resource

import time
from topic import *

mutex = Lock()
timevals = []

def callback(ch, method, properties, body):
    topic = body.decode('utf-8')
    timediff = gettimediff(topic, time.time())
    timevals.append(timediff)
    print('MsgID: {0} Time difference between sent and received: {1}' \
                                    .format(getMsgId(topic), timediff))
                                   
def on_message(client, userdata, msg):
    global timevals
    timediff = gettimediff(msg.payload, time.time())
    mutex.acquire()
    try:
        timevals.append(timediff)
    finally:
        mutex.release()
    print("Topic: "+msg.topic+" DeviceId: "+str(getDeviceId(msg.payload))+" MsgId: "+ str(getMsgId(msg.payload))+" Time: "+str(timediff))


if __name__=="__main__":
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

    url='amqp://iotgroup4:iot4@80.196.35.233:5672'
    broker = 'mqtt'
    p_clients = []
    s_clients = []
    subs = 0
    pubs = 0
    timeout = 90

    nr_pub = 339
    nr_con = 1

    if( broker == 'mqtt' or broker == 'amqp' ):
        for c in range(0, nr_pub + nr_con):
            client = None
            topic = None
            kwargs = None

            if( broker == 'mqtt' ):
                client = mqttClient(c, url)
                topic = {'topic': 'x', 'psize': 1, 'qos':0 }
                kwargs_p = {'nr':1, 'ival':1}
                msg_s = {'topic':'x', 'qos':0, 'cb':on_message}
                kwargs_s = {'timeout' : timeout}
            else:
                client = amqpClient(c, url)
                topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1 } ]
                kwargs_p = {'nr': 1, 'ival': 1}
                msg_s = {'exchange': 'x', 'cb': callback, 'no_ack': True}
                kwargs_s = {'timeout' : timeout}

            if( c < nr_pub ):
                p_clients.append(client)
                pubs += 1
            else:
                s_clients.append(client)
                subs += 1
            client.connect()

        print('Publishers: {0} Subscribers: {1}' .format( pubs, subs ))

        for s in s_clients:
            s.subscribe(msg_s, kwargs_s)

        for s in s_clients:
            s.start_subscribe_timeout(topic, kwargs_s)

        time.sleep(1)
        for p in p_clients:
            p.publish(topic, kwargs_p)

        ## wait until they are terminated, make sure to disconnect so that connections at the host are freed
        for p in p_clients:
            p.waitForClient()
        
        for s in s_clients:
            s.waitForClient()

    print(len(timevals))