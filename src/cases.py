import numpy as np
import sys
from amqpClient import amqpClient
#from mqttClientV2 import mqttClient
from mqttClient import mqttClient
import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv
#import resource

import time
from topic import *
from threading import Lock

mutex = Lock()
timevals = []
recv_msgs = 0

def callback_pub_sub_test(ch, method, properties, body):
    global timevals, mutex
    topic = body.decode('utf-8')
    timediff = gettimediff(topic, time.time())
    mutex.acquire()
    try:
        timevals.append(timediff)
    finally:
        mutex.release()
    #print('MsgID: {0} Time difference: {1}' .format(getMsgId(topic), timediff))

def callback_pub_sub_test_mqtt(client, userdata, msg):
    global timevals, mutex
    timediff = gettimediff(msg.payload, time.time())
    mutex.acquire()
    try:
        timevals.append(timediff)
    finally:
        mutex.release()
    #print('MsgID: {0} Time difference: {1}' .format(getMsgId(msg.payload), timediff))

def callback_msg_interval(ch, method, properties, body):
    global recv_msgs, timevals
    topic = body.decode('utf-8')
    timediff = gettimediff(topic, time.perf_counter())
    #timediff = gettimediff(topic, time.time())
    timevals.append(timediff)
    recv_msgs += 1
    #print('MsgID: {0} Time difference: {1}' .format(getMsgId(topic), timediff))

def callback_msg_interval_mqtt(client, userdata, msg):
    global recv_msgs, timevals
    timediff = gettimediff(msg.payload, time.perf_counter())
    #timediff = gettimediff(topic, time.time())
    timevals.append(timediff)
    recv_msgs += 1

def pub_sub_run(broker, url, nr_pub, nr_con, interval=1 ):
    global timevals
    timevals = []
    if( broker == 'mqtt' or broker == 'amqp' ):
        p_clients = []
        s_clients = []
        pubs = 0
        subs = 0
        timeout = 170

        for c in range(0, nr_pub + nr_con):
            client = None
            topic = None
            kwargs = None
                
            if( broker == 'mqtt' ):
                client = mqttClient(c, url)
                topic = {'topic': 'my/topic', 'psize': 1, 'qos':0 }
                kwargs_p = {'nr':1, 'ival': interval}
                msg_s = {'topic': 'my/topic', 'qos':0, 'cb':callback_pub_sub_test_mqtt}
                kwargs_s = {'timeout' : timeout}
            else:
                client = amqpClient(c, 'amqp://{0}'.format(url))
                topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1 } ]
                kwargs_p = {'nr': 1, 'ival': interval}
                msg_s = {'exchange': 'x', 'cb': callback_pub_sub_test, 'no_ack': True, 'auto_delete': True}
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

        time.sleep(5)

        for s in s_clients:
            s.start_subscribe_timeout(topic, kwargs_s)

        for p in p_clients:
            p.publish(topic, kwargs_p)

        ## wait until they are terminated, make sure to disconnect so that connections at the host are freed
        for p in p_clients:
            p.waitForClient()
        
        for s in s_clients:
            s.waitForClient()

        print('Total msgs received: {}' .format( len(timevals)) ) 
    return np.median(timevals), nr_pub-nr_con

def pub_sub_test(broker, url, fileName, iterations=10, stepsize=10):
    times = []
    ratios = []
    for i in range(10, iterations, stepsize):
        timeval, ratioval = pub_sub_run(broker, url, i, iterations - i, interval=stepsize)
        if( not np.isnan(timeval) ):
            times.append(timeval)
            ratios.append(ratioval)

    write_to_csv(ratios, times, '../csv/finalresults/{0}'.format(fileName), 'Pub vs con (median time)')

def msg_interval_test(broker, url, fileName, iterations=1, stepsize=1, interval=0.01):
    y_packetloss = []
    x_msg_s = []
    
    y_times = []
    for i in range(stepsize, iterations + 1, stepsize):
        global recv_msgs, timevals
        recv_msgs = 0
        timevals = []
        p_clients = []
        s_client = None
        msgs_pr_publisher = 600
        timeout = 170
        
        if( broker == 'mqtt' or broker == 'amqp' ):
            client = None
            topic = None
            kwargs = None

            subs = 0
            pubs = 0
            for j in range(i + 1):
                if( broker == 'mqtt' ):
                    client = mqttClient(j, url)
                    topic = {'topic': 'x', 'psize': 1, 'qos':0 }
                    kwargs_p = {'nr': msgs_pr_publisher, 'ival': interval}
                    msg_s = {'topic':'x', 'qos':0, 'cb': callback_msg_interval_mqtt}
                    kwargs_s = {'timeout' : timeout}
                else:
                    client = amqpClient(j, 'amqp://{0}'.format(url))
                    topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1 } ]
                    kwargs_p = {'nr': msgs_pr_publisher, 'ival': interval}
                    msg_s = {'exchange': 'x', 'cb': callback_msg_interval, 'no_ack': True, 'auto_delete': True}
                    kwargs_s = {'timeout': timeout}
                
                if( j < i ):
                    p_clients.append(client)    
                    pubs += 1
                else:
                    s_client = client
                    subs += 1

                client.connect()

            print('Publishers: {0} Subscribers: {1}' .format( pubs, subs ))
            if (not s_client.isConnected()):
                s_client.connect()

            s_client.subscribe(msg_s, kwargs_s)
            s_client.start_subscribe_timeout(topic, kwargs_s)
            
            time.sleep(1)

            for p in p_clients:
                p.publish(topic, kwargs_p)

            ## wait until they are terminated, make sure to disconnect so that connections at the host are freed
            s_client.waitForClient()

            for p in p_clients:
                p.waitForClient()

            sent_msgs = i / interval

            x_msg_s.append(i * interval)

            if( sent_msgs > 0 ):
                y_packetloss.append( recv_msgs / sent_msgs)
            else:
                y_packetloss.append(0)

            y_times.append(np.median(timevals))
        print('Total msgs received: {}' .format( len(timevals)) )
        
    write_to_csv(x_msg_s, y_packetloss, '../csv/finalresults/{0}'.format(fileName[0]), 'Packet loss test')
    write_to_csv(x_msg_s, y_times, '../csv/finalresults/{0}'.format(fileName[1]), 'Median receive time single consumer')


if __name__=="__main__":
    #resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

    ip = '80.196.35.233'
    #ip = 'localhost'
    broker = 'mqtt'
    device = 'desktop'
    date = '14_12'

    case = None
    if( len(sys.argv) < 2 ):
        print('No inline args! Specify case')
        sys.exit()
    
    case = sys.argv[1]
    if( case  == 'pub-sub-test'):
        print('Running pub-sub-test')
        pub_sub_test(broker=broker, url='iotgroup4:iot4@{}:5672'.format(ip), iterations=400, stepsize=10, fileName='{0}_pub_sub_ratio_test_{1}_{2}' .format(broker, date, device))

    elif( case == 'msg-interval-test' ):
        print('Running msg-interval-test')
        msg_interval_test(broker=broker, url='iotgroup4:iot4@{}:5672'.format(ip), iterations=60, stepsize=5, interval=0.1, \
                                                fileName=['{0}_msg_interval_test_{1}_{2}' .format(broker, date, device), '{0}_msg_time_test_{1}_{2}' .format(broker, date, device)])
    
    elif( case == 'all'):
        broker = 'amqp'
        print('Running msg-interval-test')
        msg_interval_test(broker=broker, url='iotgroup4:iot4@80.196.35.233:5672', iterations=60, stepsize=5, interval=0.1, \
                                                fileName=['{0}_msg_interval_test_{1}_{2}' .format(broker, date, device), '{0}_msg_time_test_{1}_{2}' .format(broker, date, device)])
        broker = 'mqtt'
        print('Running msg-interval-test')
        msg_interval_test(broker=broker, url='iotgroup4:iot4@80.196.35.233:5672', iterations=60, stepsize=5, interval=0.1, \
                                                fileName=['{0}_msg_interval_test_{1}_{2}' .format(broker, date, device), '{0}_msg_time_test_{1}_{2}' .format(broker, date, device)])
    else:
        print('Exit')
        sys.exit()
