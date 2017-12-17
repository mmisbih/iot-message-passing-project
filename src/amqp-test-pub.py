from amqpClient import amqpClient
from threading import Thread
import pika
import time

def callback(ch, method, properties, body):
    print(body.decode('utf-8'))

if __name__ == "__main__":

    #url = 'amqp://bbjpgbhk:g460d0kQW8VRZA7KlLQ6uC4-Mxd_yG3e@golden-kangaroo.rmq.cloudamqp.com/bbjpgbhk'
    url =  'amqp://iotgroup4:iot4@192.168.43.104:5672'
    
    amqp = amqpClient( 1, url )

    amqp.connect()
    topic = [ {'exchange': 'y', 'routing_key': '', 'psize': 10 } ]
    amqp.publish( pubmsg=topic, kwargs={'nr': 3, 'ival': 0.3} )
    #amqp.subscribe('temp')

    print("going to while loop")
    while(True):
        time.sleep(1)
    #    print('in script')

