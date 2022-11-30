from xmlrpc.server import SimpleXMLRPCServer
import os
import sys
import shutil
import pandas as pd
import numpy as np
import json
import socket
import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="db"
)
port = 9999
locations = ['mumbai', 'delhi', 'bangalore']
seats_dir = 'seats/'
total_seats = 20


def init_seats():
    file_create = True

    if sys.argv.__len__() > 1:
        if sys.argv[1] == 'y':
            shutil.rmtree(seats_dir)
        else:
            file_create = False
    else:
        if os.path.exists(seats_dir):
            if input('\nFolder already exists!\nDo you want to recreate the folder and its content ? [y/n]: ') == 'y':
                shutil.rmtree(seats_dir)
            else:
                file_create = False

    if file_create:
        os.mkdir(seats_dir)
        for loc in locations:
            sql = "INSERT INTO movies (movieID,movieName) VALUES (%s,%s)"
            seats_df = pd.DataFrame({'Seat No.': range(1, total_seats+1),
                                     'Status': [0]*total_seats,
                                     'Timestamp': [np.nan]*total_seats})
            seats_df.to_csv(os.path.join(
                os.getcwd(), f'{seats_dir}/seats_{loc}.csv'), index=False)
            seats_df.to_csv(os.path.join(
                os.getcwd(), f'{seats_dir}/seats_{loc}1.csv'), index=False)


def request_database(city):
    print("--> database1 <--")
    df = pd.read_csv(f'{seats_dir}/seats_{city.lower()}.csv')
    print("--> database2 <--")
    df = pd.read_csv(f'{seats_dir}/seats_{city.lower()}1.csv')
    return df.to_json(orient='records')


def update_database(json_data, city):
    df = pd.DataFrame(json.loads(json_data))
    os.remove(os.path.join(
        os.getcwd(), f'{seats_dir}/seats_{city.lower()}.csv'))
    df.to_csv(os.path.join(
        os.getcwd(), f'{seats_dir}/seats_{city.lower()}.csv'), index=False)
    os.remove(os.path.join(
        os.getcwd(), f'{seats_dir}/seats_{city.lower()}1.csv'))
    df.to_csv(os.path.join(
        os.getcwd(), f'{seats_dir}/seats_{city.lower()}1.csv'), index=False)
    # TODO: Send updates database


def get_status():
    return 'Database server is up and running!'


if __name__ == '__main__':
    init_seats()

    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    print('\nDatabase server up and running!\n')

    server.register_function(request_database, 'request_database')
    server.register_function(update_database, 'update_database')
    server.register_function(get_status, 'get_status')
    server.serve_forever()
