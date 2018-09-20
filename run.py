from bottle import route, run, template, request, redirect, static_file, default_app, response, hook
from tasks import to_mp4, app
from celery.result import AsyncResult
import hashlib
import os

STATIC='static'

def url_hash(url):
    m = hashlib.md5()
    m.update(url.encode('utf-8'))
    return m.hexdigest()


def check_file(filename):
    return os.path.exists(filename)


def to_static_url(filename):
    return "/" + filename


@route('/hls_to_mp4')
def hls_to_mp4():
    m3u8_url = request.query.get('m3u8_url')
    mp4_file = os.path.join(STATIC, url_hash(m3u8_url) + ".mp4")
    if check_file(mp4_file):
        return redirect(to_static_url(mp4_file))
    else:
        task = to_mp4.delay(m3u8_url, mp4_file)
        return redirect('/wait/{}'.format(task.id))


@route('/wait/<task_id:re:[-\w]+>')
def wait(task_id):
    result = to_mp4.AsyncResult(task_id=task_id)
    if result.state != 'SUCCESS':
        return '<meta http-equiv="refresh" content="3" /> code:{}'.format(result.state)
    else:
        return redirect(to_static_url(result.get()))


@route('/static/<path:path>')
def static(path):
    return static_file(path, root=STATIC)

    
app = default_app()
if __name__ == '__main__':
    run(host='localhost', port=8080)

