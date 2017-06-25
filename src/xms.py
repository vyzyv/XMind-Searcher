#!/usr/bin/env python

import argparse
import mysql.connector

#IMPORT MENU AND READING CREDENTIALS, DATABASE DATA
import xms_utilities

parser = argparse.ArgumentParser(
        description='''
        Scans through xmind notes and returns path and exact branch to your query\n\n
        [IMPORTANT]\n\n
        Before running this program you need to initialize database, check README.txt\n
        ''')

parser.add_argument('keyword',
        help='Keyword to be searched for')

args = parser.parse_args()
directory = '~/.xms/'
username, pwd = xms_utilities.receive_data(
        directory='~/.xms/',filename='data',
        error_message='Error occured when reading file, requesting credentials...',
        not_found_message='File not found, requesting credentials...',
        first_prompt_message='MySQL username: ',
        second_prompt_message='Password: '
        )
db, connection = xms_utilities.receive_data(
        directory='~/.xms/',filename='config',
        error_message='Error occured when reading file, requesting database and connection information...',
        not_found_message='File not found, requesting database and connection information...',
        first_prompt_message='Name of database: ',
        second_prompt_message='Location of database [e.g. localhost]: '
        )

#CONECTING TO DATABASE
database = mysql.connector.connect(
        user = username,
        password = pwd,
        host = connection,
        database = db
)

cursor = database.cursor()

xms_utilities.find_keyword(cursor, args.keyword)
