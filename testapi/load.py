import datetime
import os
import httplib2
import json

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

import pymongo

AUTH_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'auth'))
CLIENT_SECRETS_FILE = os.path.join(AUTH_PATH, 'client_secrets.json')
STORAGE_FILE = os.path.join(AUTH_PATH, 'tokens.dat')

GOOGLE_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
GOOGLE_MESSAGE = 'Something seems to have gone wrong, check the client secrets file'

class GoogleAnalayticsClient(object):
    def __init__(self):
        storage = Storage(STORAGE_FILE)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=GOOGLE_SCOPE, message=GOOGLE_MESSAGE)
            credentials = run(flow, storage)

        http = credentials.authorize(httplib2.Http())

        self.service = build('analytics', 'v3', http=http)

    def get(self, *args, **kwargs):
        return self.service.data().ga().get(*args, **kwargs)

def load_hourly_visits(ga, db):
    response = ga.get(
        metrics    = 'ga:visits',
        dimensions = 'ga:date,ga:hour',
        start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date   = datetime.date.today().strftime('%Y-%m-%d'),
        ids        = 'ga:63654109'
    ).execute()
    for row in response['rows']:
        start_at = datetime.datetime.strptime(''.join(row[:2]), '%Y%m%d%H')
        document = {
            'start_at':   start_at,
            'end_at':     start_at + datetime.timedelta(hours=1),
            'period':     'hour',
            'visits':     row[2],
            'dimensions': []
        }
        query = {
            'start_at': document['start_at'],
            'end_at':   document['end_at'],
            'visits':   {
                '$ne': None
            }
        }
        db.update(query, document, upsert=True)

def load_weekly_visits(ga, db):
    start_date = datetime.date.today() - datetime.timedelta(weeks=27)
    start_date = start_date - datetime.timedelta(days=(start_date.weekday() + 1) % 7)

    while True:
        end_date = start_date + datetime.timedelta(days=6)
        if end_date >= datetime.date.today():
            break

        response = ga.get(
            metrics = 'ga:visits',
            start_date = start_date.strftime('%Y-%m-%d'),
            end_date   = end_date.strftime('%Y-%m-%d'),
            ids = 'ga:53872948'
        ).execute()
        for row in response['rows']:
            start_at = datetime.datetime.combine(start_date, datetime.time())
            document = {
                'start_at':   start_at,
                'end_at':     start_at + datetime.timedelta(days=7),
                'period':     'week',
                'visits':     row[0],
                'dimensions': []
            }
            query = {
                'start_at': document['start_at'],
                'end_at':   document['end_at'],
                'visits':   {
                    '$ne': None
                }
            }
            db.update(query, document, upsert=True)

        start_date += datetime.timedelta(days=7)

def load_format_engagement(ga, db):
    start_date = datetime.date.today() - datetime.timedelta(weeks=20)
    start_date = start_date - datetime.timedelta(days=(start_date.weekday() + 1) % 7)

    while True:
        end_date = start_date + datetime.timedelta(days=6)
        print(start_date, end_date)
        if end_date >= datetime.date.today():
            break

        response = ga.get(
            metrics = 'ga:totalEvents',
            dimensions = 'ga:eventCategory,ga:eventAction,ga:eventLabel',
            start_date = start_date.strftime('%Y-%m-%d'),
            end_date = end_date.strftime('%Y-%m-%d'),
            ids = 'ga:53872948',
            filters = 'ga:eventCategory=~^MS_;ga:eventCategory!=MS_transaction',
            max_results = 5000
        ).execute()

        if response['totalResults'] > 0:
            for row in response['rows']:
                start_at = datetime.datetime.combine(start_date, datetime.time())
                key = 'successes' if row[2] == 'Success' else 'entries'
                document = {
                    'start_at':   start_at,
                    'end_at':     start_at + datetime.timedelta(days=7),
                    'period':     'week',
                    'format':     row[0][3:],
                    'slug':       row[1],
                    key:          row[3],
                    'dimensions': ['format', 'slug']
                }
                query = {
                    'start_at': document['start_at'],
                    'end_at':   document['end_at'],
                    'format':   document['format'],
                    'slug':     document['slug'],
                    'dimensions': ['format', 'slug']
                }
                if db.find(query).count():
                    db.update(query, {'$set': {key: row[3]}})
                else:
                    db.save(document)

        start_date += datetime.timedelta(days=7)

def load_format_engagement_no_slug(ga, db):
    start_date = datetime.date.today() - datetime.timedelta(weeks=20)
    start_date = start_date - datetime.timedelta(days=(start_date.weekday() + 1) % 7)

    while True:
        end_date = start_date + datetime.timedelta(days=6)
        if end_date >= datetime.date.today():
            break

        response = ga.get(
            metrics = 'ga:totalEvents',
            dimensions = 'ga:eventCategory,ga:eventLabel',
            start_date = start_date.strftime('%Y-%m-%d'),
            end_date = end_date.strftime('%Y-%m-%d'),
            ids = 'ga:53872948',
            filters = 'ga:eventCategory=~^MS_;ga:eventCategory!=MS_transaction',
            max_results = 5000
        ).execute()

        if response['totalResults'] > 0:
            for row in response['rows']:
                start_at = datetime.datetime.combine(start_date, datetime.time())
                key = 'successes' if row[1] == 'Success' else 'entries'
                document = {
                    'start_at':   start_at,
                    'end_at':     start_at + datetime.timedelta(days=7),
                    'period':     'week',
                    'format':     row[0][3:],
                    key:          row[2],
                    'dimensions': ['format']
                }
                query = {
                    'start_at':   document['start_at'],
                    'end_at':     document['end_at'],
                    'format':     document['format'],
                    'dimensions': ['format']
                }
                if db.find(query).count():
                    db.update(query, {'$set': {key: row[2]}})
                else:
                    db.save(document)

        start_date += datetime.timedelta(days=7)


def main():
    client     = GoogleAnalayticsClient()
    collection = pymongo.Connection()['testapi']['testapi']

    load_hourly_visits(client, collection)
    load_weekly_visits(client, collection)
    load_format_engagement(client, collection)
    load_format_engagement_no_slug(client, collection)

if __name__ == '__main__':
    main()
