import sys
from amqpClient import amqpClient
from mqttClient import mqttClient

import time
from topic import *

def callback(ch, method, properties, body):
    topic = body.decode('utf-8')
    print('\nMsgID: {0} \nTime difference between sent and received: {1}\n' \
                                    .format(getMsgId(topic), gettimediff(topic, time.time())))

def on_message(client, userdata, msg):
    print("Topic: "+msg.topic+" DeviceId: "+str(getDeviceId(msg.payload))+" MsgId: "+ str(getMsgId(msg.payload))+" Time: "+str(gettimediff(msg.payload, time.time())))

                                    
if __name__=="__main__":

    if( sys.argv[1:][0] == [] or sys.argv[2:] == []):
        print('No inline args! Use -mqtt or -amqp and nbr of consumers and publishers')
        sys.exit()
    if( sys.argv[1:][0]  == '-mqtt'):
        print('Using mqtt')
    elif( sys.argv[1:][0]  == '-amqp' ):
        print('Using amqp')
    else:
        sys.exit()

    arg = sys.argv[1:][0]  #mqtt or amqp
    nbr_publishers = int(sys.argv[2:][0]) #publishers
    nbr_consumers = int(sys.argv[2:][1]) #consumers
    #url = 'amqp://bbjpgbhk:g460d0kQW8VRZA7KlLQ6uC4-Mxd_yG3e@golden-kangaroo.rmq.cloudamqp.com/bbjpgbhk'
    url = 'amqp://iotgroup4:iot4@192.168.43.104:5672'
    if( arg == '-mqtt' or arg == '-amqp' ):
        p_clients = []
        s_clients = []
        for c in range(0, nbr_publishers + nbr_consumers):
            client = None
            topic = None
            kwargs = None

            if( arg == '-mqtt' ):
                client = mqttClient(c, url)
                topic = {'topic':'x', 'psize':10000, 'qos':0 }
                kwargs_p = {'nr':10, 'ival':0.1}
                msg_s = {'topic':'x', 'qos':0, 'cb':on_message}
                kwargs_s = {'timeout' : 30}
            else:
                client = amqpClient(c, url)
                topic = [ {'exchange': 'x', 'routing_key': '', 'psize': 1000 } ]
                kwargs_p = {'nr': 3, 'ival': 2}
                msg_s = {'exchange': 'x', 'cb': callback, 'no_ack': True}
                kwargs_s = {'timeout' : 30}

            if( c < nbr_publishers ):
                p_clients.append(client)
            else:
                s_clients.append(client)
            client.connect()

        for s in s_clients:
            s.subscribe(msg_s, kwargs_s)

        for p in p_clients:
            p.publish(topic, kwargs_p)

        for s in s_clients:
            s.waitForClient()

        for p in p_clients:
            p.waitForClient()