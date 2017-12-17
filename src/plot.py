import matplotlib.pyplot as plt
from csv_helper import read_from_csv, write_to_csv 
import sys

# array of dict, with (x, y, x_name, y_name) as keys
def plot(xy, name, x_label, y_label):
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

# array of dict, with (x, y, x_name, y_name) as keys
def histogram(xy, name, x_label, y_label):
    legend = []
    for xy, lgnd in xy:
        #print(xy)
        ##plt.plot(xy[0],xy[1])
        # histogram of y values!
        plt.hist(xy[1], normed=True) #bins=30
        legend.append(lgnd)

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def stem(xy, name, x_label, y_label):
    legend = []
    for xy, lgnd in xy:
        #print(xy)
        plt.stem(xy[0],xy[1])
        legend.append(lgnd)

    plt.legend( legend )
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

if __name__ == '__main__':
    # run with -x file1 file2 file3 ..

    plot_type = sys.argv[1]
    
    name = 'test'
    x_label = 'x axis'
    y_label = 'y_axis'

    xy = [ read_from_csv(f) for f in sys.argv[2:] ] 

    if plot_type == '-p': # plot
        plot(xy, name, x_label, y_label)
    elif plot_type == '-h': # histogram
        histogram(xy, name, x_label, y_label)
    elif plot_type == '-s': # stem
        stem(xy, name, x_label, y_label)
    else:
        print('wrong type argument given')
        sys.exit(1)

