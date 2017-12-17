from amqpClient import amqpClient

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

url = 'amqp://bbjpgbhk:g460d0kQW8VRZA7KlLQ6uC4-Mxd_yG3e@golden-kangaroo.rmq.cloudamqp.com/bbjpgbhk'
amqpC = amqpClient(url)
amqpC.connect()
amqpC.subscribe({'exchange': 'logs', 'callback': callback, 'no_ack': True})
