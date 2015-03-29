#! /usr/bin/env python

# 2014-2015 Markus Hsi-Yang Fritz

from __future__ import print_function, division
import click
from flask import Flask, render_template, request
from tempfile import NamedTemporaryFile
import os
import gzip
import json
from readfq import readfq
import maze

app = Flask(__name__)
cfg = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/matches')
def data():
    length = request.args.get('length', type=int)
    match_type = request.args.get('matches')
    ref = json.loads(request.args.get('ref'))
    queries = json.loads(request.args.get('query'))
    m = []
    with NamedTemporaryFile(delete=False) as f_ref:
        fn_ref = f_ref.name
        print('>{}'.format(ref['name']), file=f_ref)
        print(ref['seq'], file=f_ref)
    for query in queries:
        with NamedTemporaryFile(delete=False) as f_query:
            fn_query = f_query.name
            print('>{}'.format(query['name']), file=f_query)
            print(query['seq'], file=f_query)
        matches = maze.mummer_matches(fn_ref,
                                      fn_query,
                                      length,
                                      match_type,
                                      cfg['debug'])
        m.append(matches)
        os.remove(fn_query)
    os.remove(fn_ref)
    return json.dumps(m)

@click.command()
@click.option('-p', '--port', default=5000, help='port number')
@click.option('--debug/--no-debug', default=False,
              help='run server in debug mode')
@click.option('-c', '--coords', help='reference coordinates BED file')
def cli(port, debug, coords):
    global cfg
    cfg = {
        'debug': debug
    }
    app.run(port=port, debug=debug)

if __name__ == '__main__':
    cli()