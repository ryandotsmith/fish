import argparse, os
from db import DB
from flask import Flask, redirect, request

parser = argparse.ArgumentParser()
parser.add_argument('--address')
parser.add_argument('--buddy', default=None)
parser.add_argument('--dir')
parser.add_argument('--priority', type=int, default=0)
parser.add_argument('--want-master', action="store_true", default=False)
args = parser.parse_args()

db = DB(args.dir, args.address, args.priority, args.buddy, args.want_master)
app = Flask(__name__)

@app.route('/is-master')
def is_master():
  if db.is_master():
    return('yes')
  else:
    return('no')

@app.route('/receive', methods=['PUT'])
def receive():
  if db.is_master():
    return('at=accept body=%s' % request.form['data'])
  else:
    addr = db.master_address()
    return('at=deny master=%s' % addr)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
