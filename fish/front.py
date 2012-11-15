import argparse, os, requests, json
from db import DB
from flask import Flask, redirect, request

parser = argparse.ArgumentParser()
parser.add_argument('--address')
parser.add_argument('--buddy', default=None)
parser.add_argument('--dir')
parser.add_argument('--priority', type=int, default=0)
parser.add_argument('--want-master', action="store_true", default=False)
a = parser.parse_args()

db = DB(a.dir, a.address, a.priority, a.buddy, a.want_master, True)
app = Flask(__name__)

@app.route('/receive', methods=['PUT'])
def receive():
    addr = db.master_address()
    url = "http://{0}/data".format(addr)
    headers = {'content-type': 'application/json'}
    payload = {'hello': 'world'}
    #resp = requests.put(url, data=json.dump(payload))
    print('at=forward master=%s' % url)
    return(url)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
