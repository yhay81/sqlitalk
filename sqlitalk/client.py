import argparse
import socket
from logging import getLogger
from pathlib import Path
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

logger = getLogger()
HISTORY_FILE_PATH = '.sqlitalk_history'
Path(HISTORY_FILE_PATH).touch()
session = PromptSession(history=FileHistory(HISTORY_FILE_PATH))

HELP = """.exit                  Exit this program
.help                  Show this message
.quit                  Exit this program
.tables                List names of tables"""


def create_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-H', '--host', dest='host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, dest='port', default=6777)
    return parser.parse_args()


def main():
    args = create_parser()
    print(f"""SQLiTalk version 0.1.0 {datetime.now()} \nEnter ".help" for usage hints.""")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect((args.host, args.port))
        logger.info('connect: {}:{}'.format(args.host, args.port))
        while True:
            input_str = session.prompt('sqlitalk> ')
            logger.info('input: {}'.format(input_str))
            if input_str in ['.exit', '.quit']:
                break
            if input_str == '.help':
                print(HELP)
                continue
            if input_str == '.tables':
                input_str = "select name from sqlite_master where type='table'"
            my_socket.sendall(input_str.encode('utf-8'))
            logger.info('sent')
            data = my_socket.recv(1024)
            logger.info('data: {}'.format(data.decode('utf-8')))
            print(data.decode('utf-8'))


if __name__ == '__main__':
    main()
