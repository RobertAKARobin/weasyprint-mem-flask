import collections
import datetime
import os

import flask
import psutil
import weasyprint

log_max = 50
log = collections.deque([], log_max)
data_unit = 'mb'
font_config = weasyprint.text.fonts.FontConfiguration()

pid = os.getpid()
mem = psutil.Process(pid).memory_full_info()
fields = [field for field in mem._fields]

words = 'all work and no play makes jack a dull boy'.split(' ')
words = words + words + words
cols = [*range(11)]
rows = [*range(10)]
table = []
for rownum in rows:
    row = []
    table.append(row)
    for colnum in cols:
        row.append(words[colnum + rownum])

app = flask.Flask(__name__)

@app.route("/")
def index():
    pid = os.getpid()
    mem = psutil.Process(pid).memory_full_info()
    now = datetime.datetime.now()

    context = {}
    request = flask.request

    output = request.args.get('output', '').lower()
    if output == 'pdf':
        output = 'pdf'
    else:
        output = 'html'

    context.update({
        'data_unit': data_unit,
        'fields': fields,
        'log': log,
        'log_max': log_max,
        'output': output,
        'showpdf': request.args.get('showpdf', '')
    })

    entry = {
        'time': now,
        'output': output,
    }
    for field in fields:
        entry[field] = round(getattr(mem, field) / 1000000)
    log.appendleft(entry)

    if context['output'] == 'pdf':
        html = flask.render_template('pdf.djt', **{ 'table': table })
        pdf = weasyprint.HTML(
            string=html,
            encoding='utf-8'
        ).write_pdf(
            font_config=font_config,
        )
        response = flask.make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        return response
    return flask.render_template('index.djt', **context)
