import numpy as np
from amqpClient import amqpClient
from mqttClient import mqttClient
import matplotlib.pyplot as plt
from csv_helper import write_to_csv
import time
from topic import *
#import resource
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


def msg_size_test(broker, url, psize):
    if( broker == 'mqtt' or broker == 'amqp' ):
        p_client = None
        s_client = None
        if( broker == 'mqtt' ):
            p_client = mqttClient(1, url)
            s_client = mqttClient(2, url)
            topic = {'topic': 'x', 'psize': psize, 'qos':0 }
            kwargs_p = {'nr':10, 'ival':1}
            msg_s = {'topic':'x', 'qos':0, 'cb':on_message}
            kwargs_s = {'timeout' : 20}
        else:
            p_client = amqpClient(1, url)
            s_client = amqpClient(2, url)
            topic = [ {'exchange': 'x', 'routing_key': '', 'psize': psize } ]
            kwargs_p = {'nr': 10, 'ival': 1}
            msg_s = {'exchange': 'x', 'cb': callback, 'no_ack': True}
            kwargs_s = {'timeout' : 20}
            
        p_client.connect()
        s_client.connect()

        s_client.subscribe(msg_s, kwargs_s)
        s_client.start_subscribe_timeout(topic, kwargs_s)
        
        time.sleep(1)
        
        p_client.publish(topic, kwargs_p)

        ## wait until they are terminated, make sure to disconnect so that connections at the host are freed
        p_client.waitForClient()
        s_client.waitForClient()
        
    return np.median(timevals), np.mean(timevals), np.var(timevals)


if __name__=="__main__":
    print("Running msg_size_test")
    #resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
    device = 'desktop'
    date = '12_12'
    
    # minimum message size
    msg_min = 0
    
    # maximum message size
    msg_max = 2000000
    
    # number of messages
    msg_nr = 20
    
    # test repetisions
    rep_nr = 5
    
    # protocol 
    proto = 'amqp'
    
    # url
    url = 'amqp://iotgroup4:iot4@80.196.35.233:5672'
    
    msg_ival = int((msg_max-msg_min)/(msg_nr-1))
    msg_med_times  = []
    msg_mean_times = []
    msg_var_times  = []
    msg_psize = range(msg_min, msg_max+1, msg_ival)
    
    med_mat = []
    mean_mat = []
    var_mat = []
    for i in range(0,rep_nr):
        med_vec  = []
        mean_vec = []
        var_vec  = []
        for j in msg_psize:
            #print(j)
            timevals = []
            time_med, time_mean, time_var = msg_size_test(proto, url, j)
            med_vec.append(time_med)
            mean_vec.append(time_mean)
            var_vec.append(time_var)
        med_mat.append(med_vec)
        mean_mat.append(mean_vec)
        var_mat.append(var_vec)
    
    for i in range(0,len(msg_psize)):
        med = np.median([row[i] for row in med_mat])
        mean = np.median([row[i] for row in mean_mat])
        var = np.median([row[i] for row in var_mat])
        msg_med_times.append(med)
        msg_mean_times.append(mean)
        msg_var_times.append(var)
    
    write_to_csv(msg_psize, msg_med_times,  '../csv/finalresults/' + proto + '_msg_size_test_med_' + date + '_' + device,  proto + '_msg_size_test_med_' + date + '_' + device)
    write_to_csv(msg_psize, msg_mean_times, '../csv/finalresults/' + proto + '_msg_size_test_mean_' + date + '_' + device, proto + '_msg_size_test_mean_' + date + '_' + device)
    write_to_csv(msg_psize, msg_var_times,  '../csv/finalresults/' + proto + '_msg_size_test_var_' + date + '_' + device,  proto + '_msg_size_test_var_' + date + '_' + device)
    
