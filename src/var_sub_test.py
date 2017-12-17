import numpy as np
from amqpClient import amqpClient
from mqttClient import mqttClient
import matplotlib.pyplot as plt
from csv_helper import write_to_csv
#import resource

import time
from topic import *
from threading import Lock

mutex = Lock()
timevals = []

def callback(ch, method, properties, body):
    global timevals, mutex
    topic = body.decode('utf-8')
    timediff = gettimediff(topic, time.time())
    mutex.acquire()
    try:
        timevals.append(timediff)
    finally:
        mutex.release()
    #print('MsgID: {0} Time difference between sent and received: {1}'.format(getMsgId(topic), timediff))
                                   
def on_message(client, userdata, msg):
    global timevals, mutex
    timediff = gettimediff(msg.payload, time.time())
    mutex.acquire()
    try:
        timevals.append(timediff)
    finally:
        mutex.release()
    #print("Topic: "+msg.topic+" DeviceId: "+str(getDeviceId(msg.payload))+" MsgId: "+ str(getMsgId(msg.payload))+" Time: "+str(timediff))

def var_sub_test(broker, url, nr_pub, nr_con ):
    if( broker == 'mqtt' or broker == 'amqp' ):
        p_clients = []
        s_clients = []
        for c in range(0, nr_pub + nr_con):
            client = None
            topic = None
            kwargs = None

            if( broker == 'mqtt' ):
                client = mqttClient(c, url)
                topic = {'topic': 'x', 'psize': 1, 'qos':0 }
                kwargs_p = {'nr':1, 'ival':1}
                msg_s = {'topic':'x', 'qos':0, 'cb':on_message}
                kwargs_s = {'timeout' : 10}
            else:
                client = amqpClient(c, url)
                topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1 } ]
                kwargs_p = {'nr': 1, 'ival': 1}
                msg_s = {'exchange': 'x', 'cb': callback, 'no_ack': True}
                kwargs_s = {'timeout' : 10}

            if( c < nr_pub ):
                p_clients.append(client)
            else:
                s_clients.append(client)
            client.connect()

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

    return np.median(timevals), np.mean(timevals), np.var(timevals), len(timevals)
    
if __name__=="__main__":
    print("Running var_sub_test")
    #resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
    device = 'desktop'
    date = '12_12'
    
    #minimum number of subscribers
    sub_min = 10
    
    #maximum number of subscribers
    sub_max = 800
    
    # number of intervals
    sub_nr = 20
    
    #repetition number
    rep_nr = 5
    
    # protocol name
    proto = 'amqp'
    
    # url
    url = 'amqp://iotgroup4:iot4@80.196.35.233:5672'
    
    sub_ival = int((sub_max-sub_min)/(sub_nr-1))
    sub_vars = []
    sub_med = []
    sub_mean = []
    sub_xval = range(sub_min, sub_max+1, sub_ival)
    
    med_mat = []
    mean_mat = []
    var_mat = []
    for i in range(0,rep_nr):
        med_vec  = []
        mean_vec = []
        var_vec  = []
        for j in sub_xval:
            #print(j)
            timevals = []
            time_med, time_mean, time_var, _ = var_sub_test(proto, url, 1, j)
            med_vec.append(time_med)
            mean_vec.append(time_mean)
            var_vec.append(time_var)
        med_mat.append(med_vec)
        mean_mat.append(mean_vec)
        var_mat.append(var_vec)
        
    for i in range(0,len(sub_xval)):
        med = np.median([row[i] for row in med_mat])
        mean = np.median([row[i] for row in mean_mat])
        var = np.median([row[i] for row in var_mat])
        sub_med.append(med)
        sub_mean.append(mean)
        sub_vars.append(var)
    
    write_to_csv(sub_xval, sub_med,  '../csv/finalresults/' + proto + '_var_sub_test_med_' + date + '_' + device,  proto + '_var_sub_test_med_' + date + '_' + device)
    write_to_csv(sub_xval, sub_mean, '../csv/finalresults/' + proto + '_var_sub_test_mean_' + date + '_' + device, proto + '_var_sub_test_mean_' + date + '_' + device)
    write_to_csv(sub_xval, sub_vars,  '../csv/finalresults/' + proto + '_var_sub_test_var_' + date + '_' + device,  proto + '_var_sub_test_var_' + date + '_' + device)
        