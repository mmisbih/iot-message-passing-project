import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv 
import numpy as np
import sys

# array of dict, with (x, y, x_name, y_name) as keys
def plot(xy, name, x_label, y_label):
    legend = []
    for xy, lgnd in xy:
        plt.plot(xy[0],xy[1], 'o')
        legend.append(lgnd)

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

if __name__=="__main__":
    name = 'Message broker load'
    x_label = 'Messages (s)'
    y_label = 'Median delivery time (s)'
    filemqtt = "../csv/finalresults/mqtt_msg_time_test_14_12_piB"
    fileamqp = "../csv/finalresults/amqp_msg_time_test_14_12_piB"
    files = [filemqtt, fileamqp]

    xy = [ read_from_csv(f) for f in files ] 

    legend = []
    for xy, lgnd in xy:
        plt.plot(np.multiply(100,xy[0]),xy[1])
        
    legend.append("MQTT - PiB")
    legend.append("AMQP - PiB")
    
    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


    fileamqp = "../csv/finalresults/amqp_msg_time_test_14_12_"
    filemqtt = "../csv/finalresults/mqtt_msg_time_test_14_12_"
    files = ["{}desktop".format(filemqtt), "{}pi3".format(filemqtt), "{}desktop".format(fileamqp), "{}pi3".format(fileamqp)]

    xy = [ read_from_csv(f) for f in files ] 

    legend = []
    for xy, lgnd in xy:
        plt.plot(np.multiply(100,xy[0]),xy[1])
    
    legend.append("MQTT - Desktop")
    legend.append("MQTT - Pi3")
    legend.append("AMQP - Desktop")
    legend.append("AMQP - Pi3")

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()