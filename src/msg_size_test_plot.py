import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv 
import sys

if __name__ == '__main__':
    # run with -x file1 file2 file3 ..
    
    files = []
    
    name = 'Message size'
    x_label = 'x axis'
    y_label = 'y_axis'
    
    #mqtt piB
    mqttpib = 'mqtt_msg_size_test_med_12_12_piB'
    files.append(mqttpib)
    #mqtt pi3
    mqttpi3 = 'mqtt_msg_size_test_med_12_12_pi3'
    files.append(mqttpi3)
    #mqtt desktop
    mqttdesktop = 'mqtt_msg_size_test_med_12_12_desktop'
    files.append(mqttdesktop)
    
    #amqp piB
    amqppib = 'amqp_msg_size_test_med_11_12_piB'
    files.append(amqppib)
    #amqp pi3
    amqppi3 = 'amqp_msg_size_test_med_12_12_pi3'
    files.append(amqppi3)
    #amqp desktop
    amqpdesktop = 'amqp_msg_size_test_med_12_12_desktop'
    files.append(amqpdesktop)

    xy = [ read_from_csv(f) for f in files ] 
        
    legend = []
    for xy, lgnd in xy:
        #print(xy)
        ##plt.plot(xy[0],xy[1])
        plt.plot(xy[0],xy[1], 'o')
        legend.append(lgnd)

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()