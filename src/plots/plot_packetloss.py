import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv 

if __name__ == '__main__':
    path = '../../csv/finalresults/'
    files = []
    files.append('amqp_msg_interval_test_10_12_pi3')
    files.append('amqp_msg_interval_test_10_12_piB')
    files.append('amqp_msg_interval_test_12_12_desktop')
    xy = [ read_from_csv(path + f) for f in files ] 

    legend = []
    for xy, lgnd in xy:
        plt.plot(xy[0],xy[1], 'o')
        legend.append(lgnd)

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
