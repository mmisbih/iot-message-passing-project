import os
import paramiko
import sys


def restart_server(hostname, password, username='pi', port=22):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, username=username, password=password, port=port)
    stop_stdin, stop_stdout, stop_stderr = ssh_client.exec_command('sudo systemctl stop rabbitmq-server.service')
    print('Stop - stdin:{}, stdout:{}, stderr:{}'.format(stop_stdin, stop_stdout, stop_stderr))
    start_stdin, start_stdout, start_stderr = ssh_client.exec_command('sudo systemctl start rabbitmq-server.service')
    print('Start - stdin:{}, stdout:{}, stderr:{}'.format(start_stdin, start_stdout, start_stderr))
