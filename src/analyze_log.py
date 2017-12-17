import os
import paramiko
import sys


if __name__=="__main__":
    hostname = '80.196.35.233'
    password = sys.argv[1]
    username = 'pi'
    port = 22
    
    remotepath = '/var/log/rabbitmq/rabbit@raspberrypi.log'
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, username=username, password=password, port=port)

    ftp_client = ssh_client.open_sftp()
    ftp_client.get(remotepath, '../src/log/rabbitmq.log')
    ftp_client.close()


    # Analyze log file

    # high watermark set!
    memory_cap = []

    # entire log file, where each element is a line from the log file
    log_file = []

    with open('../src/log/rabbitmq.log') as f:
        for line in f:
            log_file.append(line)
        f.close()

    for l in range(len(log_file)):
        if 'vm_memory_high_watermark set' in log_file[l]:
            memory_cap.append(log_file[l-1] + log_file[l])

    for m in memory_cap:
        print(m)

    print(len(m))


