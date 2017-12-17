import numpy as np
from amqpClient import amqpClient
import matplotlib.pyplot as plt
import copy
import time
from topic import *

timevals = []
recv_packets = []

def callback(ch, method, properties, body):
    global timevals
    global recv_packets
    topic = body.decode('utf-8')
    recv_packets.append(topic)
    timediff = gettimediff(topic, time.time())
    timevals.append(timediff)
    print('\nDeviceID: {0}, MsgID: {1}\nTime difference between sent and received: {2}' \
                                    .format(getDeviceId(topic), getMsgId(topic), timediff))

def pub_sub_test(url, nr_pub, queue_size, timeout):
    global timevals
    global recv_packets
    p_clients = []
    s_client = amqpClient(0, url)
    s_client.connect()
    kwargs_s = {'timeout' : timeout, 'arguments' : {'x-max-length-bytes' : queue_size}}
    msg_s = {'exchange': 'x', 'cb': callback, 'no_ack': True}
    s_client.subscribe(msg_s, kwargs_s)
    sent_pkt = []
    for c in range(0, nr_pub ):
        client = None
        topic = None
        kwargs = None

        client = amqpClient(c, url)
        topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1 } ]
        kwargs_p = {'nr': 1, 'ival': 1, 'sent_list' : sent_pkt }

        p_clients.append(client)
        client.connect()

    time.sleep(1) # wait for subscribers to be fully initialized

    for p in p_clients:
        p.publish(topic, kwargs_p)

    ## wait until they are terminated, make sure to disconnect so that connections at the host are freed
    s_client.waitForClient()

    for p in p_clients:
        p.waitForClient()

    timevals_median = np.median(timevals)
    timevals = []
    recv_pkt = copy.deepcopy(recv_packets)
    recv_packets = []
    return timevals_median, sent_pkt, recv_pkt


if __name__=="__main__":
    times = []
    packet_loss = []
    publishers = []
    queue_size = 300
    nbr_pub_max = 100
    nbr_pub_start = 90
    
    for i in range(nbr_pub_start, nbr_pub_max ):
        timeval, sent_pkt, recv_pkt = pub_sub_test('amqp://iotgroup4:iot4@192.168.43.104:5672', i, queue_size, i+3 if i<10 else 10)
        packet_loss.append(len(sent_pkt) / len(recv_pkt))
        times.append(timeval)

    plt.plot(range(nbr_pub_start, nbr_pub_max), packet_loss)
    plt.title('Number of publishers vs queue size')
    plt.xlabel('Number of publishers')
    plt.ylabel('Time (median)')
    plt.show()
