import json
import datetime

from flask import Flask, request
import pymongo

from .timeutil import parse_iso8601

db = pymongo.Connection()['testapi']['testapi']

app = Flask(__name__)

@app.route('/api/v1')
def v1():
    query = {}
    if request.args.get('period'):
        query['period'] = request.args.get('period')
    # this is wrong, needs to know difference between dates and times
    if request.args.get('start-at'):
        query['start_at'] = {'$gte': parse_iso8601(request.args.get('start-at'))}
    if request.args.get('end-at'):
        query['end_at'] = {'$lte': parse_iso8601(request.args.get('end-at'))}

    metrics = filter(None, request.args.get('metrics', '').split(','))
    if metrics:
        query = dict(query.items() + [(metric, {'$ne':None}) for metric in metrics])

    query['dimensions'] = sorted(filter(None, request.args.get('dimensions', '').split(',')))

    response = db.find(query)

    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

    return json.dumps([row for row in response], default=dthandler)

if __name__ == '__main__':
    app.debug = True
    app.run()