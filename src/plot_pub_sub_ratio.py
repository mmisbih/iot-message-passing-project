import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv 
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
    name = 'Ratio between producers and consumers'
    x_label = 'Ratio between producers and consumers'
    y_label = 'Median delivery time (s)'
    filemqtt = "../csv/finalresults/mqtt_pub_sub_ratio_test_12_12_"
    filesmqtt = ["{}desktop".format(filemqtt), "{}pi3".format(filemqtt), "{}piB".format(filemqtt)]

    xy = [ read_from_csv(f) for f in filesmqtt ] 

    legend = []
    for xy, lgnd in xy:
        #print(xy)
        plt.plot(xy[0],xy[1])
        #plt.plot(xy[0],xy[1], 'o')
        
    legend.append("MQTT - Desktop")
    legend.append("MQTT - Pi3")
    legend.append("MQTT - PiB")

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    #plt.show()


    fileamqp = "../csv/finalresults/amqp_pub_sub_ratio_test_12_12_"
    filesamqp = ["{}desktop".format(fileamqp), "{}pi3".format(fileamqp), "{}piB".format(fileamqp)]

    xy = [ read_from_csv(f) for f in filesamqp ] 

    for xy, lgnd in xy:
        plt.plot(xy[0],xy[1])

    legend.append("AMQP - Desktop")
    legend.append("AMQP - Pi3")
    legend.append("AMQP - PiB")

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()