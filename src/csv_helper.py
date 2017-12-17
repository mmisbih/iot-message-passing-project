import pandas as pd

def write_to_csv(x, y, fileName, name):

    toCSV = ['{0}, {1}\n'.format(x, y) for x,y in zip(x,y)]
    with open('{0}.csv'.format(fileName), 'w') as csv_file:
            csv_file.write(name + '\n')
            csv_file.write(''.join(toCSV))

def read_from_csv(fileName):
    with open('{0}.csv'.format(fileName), 'r') as csv_file:
        name = csv_file.readline().strip('\n')
    dataframe = pd.read_csv('{0}.csv' .format( fileName ), skiprows=1, header=None, sep=',', dtype=float)
    return list(zip(*dataframe.values.tolist())), name

if __name__=="__main__":

    x = [1,2,3,4]
    y = [5,6,7,8]
    write_to_csv(x,y,'test', 'testname') 
    xy, name = read_from_csv('test')
    
    print(xy)
    print(x)
    #print(list(x), list(y), name)




