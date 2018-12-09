import argparse
import socket
import sqlite3
from logging import getLogger

logger = getLogger()


def create_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('db')
    parser.add_argument('-H', '--host', dest='host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, dest='port', default=6777)
    return parser.parse_args()


def accept(my_socket, cursor):
    socket_conn, addr = my_socket.accept()
    with socket_conn:
        while True:
            data = socket_conn.recv(1024)
            data_str = data.decode('utf-8')
            logger.info('data : {}, address: {}'.format(data_str, addr))
            if data_str == 'exit':
                return True
            try:
                cursor.execute(data_str)
                logger.info('executed')
            except sqlite3.OperationalError as e:
                socket_conn.sendall(str(e).encode('utf-8'))
                logger.exception(e)
                continue
            result = cursor.fetchall()
            result_str = '\n'.join('|'.join(record) for record in result)
            response = result_str.encode('utf-8') or b' '
            socket_conn.sendall(response)
            logger.info('responded')


def main():
    args = create_parser()
    sqlite_conn = sqlite3.connect(args.db)
    cursor = sqlite_conn.cursor()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.bind((args.host, args.port))
        my_socket.listen(1)
        while True:
            try:
                end = accept(my_socket, cursor)
            except ConnectionResetError as e:
                logger.exception(e)
                continue
            sqlite_conn.commit()
            if end:
                break
    sqlite_conn.close()


if __name__ == '__main__':
    main()
