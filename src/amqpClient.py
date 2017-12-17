from IClient import IClient
from threading import Thread
from topic import *
import time
import pika
import copy

class amqpClient(IClient):

    def __init__(self, id,  amqp_url):
        self.connection = None
        self.pChannel = None
        self.pThread = None
        self.sThread = None
        self.sChannel = None
        self.sQueuename = None
        self.params = None
        self.url = amqp_url
        self.id = id
        self.qos = None

    def connect(self):
        self.params = pika.URLParameters(self.url)
        #self.params.socket_timeout = 160
        self.params.socket_timeout = 60
        retry = 500
        while( retry != 0 ):
            try:
                self.connection = pika.BlockingConnection(parameters=self.params)
                break
            except Exception as err:
                self.connection = None
                print('AMQP BlockingConnection error: {}'.format(err))
            retry -= 1
        if(retry == 0):
            print("All retries tried")
        #print(str(self.id)+' connected')

    def isConnected(self):
        return self.connection != None

    def publishThread(self, pubmsg, kwargs):
        for i in range( len(pubmsg) ): # for every message to be published
            self.pChannel.exchange_declare(exchange=pubmsg[i]['exchange'], exchange_type='fanout')
            psize = pubmsg[i].pop('psize', 10)
            for j in range( kwargs['nr'] ): # for the number of times a msg should be published
                pubmsg[i]['body'] = gettopic(self.id, j, psize) # added new json payload!
                if 'sent_list' in kwargs:
                    kwargs['sent_list'].append(pubmsg[i]['body'])
                    #print(pubmsg[i]['body'])
                self.pChannel.basic_publish( **pubmsg[i] )
                #print('sending msg: {0}'.format(i+j))
                time.sleep( kwargs['ival'] )
        #print('publishThread ended')

    def publish(self, pubmsg, kwargs):
        status = True
        if ( ( self.pThread == None ) or ( not self.pThread.is_alive() ) ) and self.connection != None: 
            try:
                if self.pChannel == None :
                    self.pChannel = self.connection.channel() # start a channel
                pubmsg_copy = copy.deepcopy(pubmsg) # makes it possible to reuse pubmsg
                qos = pubmsg_copy[0].pop('qos',{'pre_c' : 0, 'pre_s' : 0})
                self.pChannel.basic_qos(prefetch_size=qos['pre_s'], prefetch_count=qos['pre_c'])
                self.pThread = Thread( target=self.publishThread, kwargs={'kwargs' : kwargs, 'pubmsg' : pubmsg_copy} )
                self.pThread.start()
            except Exception as err:
                self.disconnect()
                self.connection = None
                print('AMQP Channel Connection error: {}'.format(err))
                status = False
        else:
            status = False

        return status

    def subscribeThread(self):
        #print('Started consuming')
        self.sChannel.start_consuming()
        #print('Ended consuming')

    def subscribe(self, submsg, kwargs):
        if self.connection != None:
            try:
                self.sChannel = self.connection.channel() # start a channel
                qos = submsg.pop('qos',{'pre_c' : 0, 'pre_s' : 0, 'no_ack' : False})
                self.sChannel.basic_qos(prefetch_size=qos['pre_s'], prefetch_count=qos['pre_c'])

                self.sChannel.exchange_declare(exchange=submsg['exchange'], exchange_type='fanout')
                result = self.sChannel.queue_declare(exclusive=True, auto_delete=kwargs.get('auto_delete', False), arguments=kwargs.get('arguments'))
                queueName = result.method.queue

                self.sChannel.queue_bind(exchange=submsg['exchange'],queue=queueName)
                self.sChannel.basic_consume(consumer_callback=submsg['cb'], queue=queueName, no_ack=submsg['no_ack'])
                self.sThread = Thread( target=self.subscribeThread )
                self.sThread.start()
            except Exception as err:
                self.disconnect()
                self.connection = None
                print('AMQP Channel Connection error: {}'.format(err))
        #print(str(self.id)+' subscribed')

    def start_subscribe_timeout(self, topic, kwargs):
        if self.connection != None:
            self.connection.add_timeout(deadline=kwargs.get('timeout', 10), callback_method=self.sChannel.stop_consuming ) #TODO: defaults to 30s

    def disconnect(self):
        if self.connection != None:
            self.connection.close()
        #print(str(self.id)+' disconnected')
        
    def waitForClient(self):
        if self.pThread != None:
            self.pThread.join()
        if self.sThread != None:
            self.sThread.join()
        self.disconnect()
        
    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection != None:
            self.disconnect()
