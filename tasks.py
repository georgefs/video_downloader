from celery import Celery
import subprocess
import time
import requests
import re
import os
import urllib.request
import tempfile
import shutil

app = Celery('tasks', broker='sqla+sqlite:///celerydb.sqlite', backend='db+sqlite:///celerydb.sqlite')

@app.task
def to_mp4(m3u8_url, output_path, st=0, t=None):
    content = requests.get(m3u8_url).text
    vs = re.findall(".*.ts", content)
    vs = [v.strip() for v in vs]
    source = "|".join(vs)


    tempfolder = tempfile.mkdtemp()
    index = ""
    index_path = os.path.join(tempfolder, "index")
    idx = 0
    for scene in vs:
        file_name = os.path.join(tempfolder, "{}.ts".format(idx))
        urllib.request.urlretrieve(scene, file_name)
        index += "file {}\n".format(os.path.join(tempfolder, file_name))
        idx += 1

    with open(index_path, 'w+') as f:
        f.write(index)


    if t:
        cmd = 'ffmpeg -y -safe 0 -f concat -i {index_path} -ss {st} -t {t} -c copy {output_path}'.format(index_path=index_path, output_path=output_path).split()
    elif st:
        cmd = 'ffmpeg -y -safe 0 -f concat -i {index_path} -ss {st} -c copy {output_path}'.format(index_path=index_path, output_path=output_path).split()
    else:
        cmd = 'ffmpeg -y -safe 0 -f concat -i {index_path} -c copy {output_path}'.format(index_path=index_path, output_path=output_path).split()
    print(cmd)
    proc = subprocess.Popen(cmd)
    proc.wait()
    if proc.poll() == 0:
        time.sleep(2)
        shutil.rmtree(tempfolder)
        return output_path
    else:
        print("error")
        return "error"


# to_mp4('http://104.199.250.233:8000/material/collection/7609.m3u8', '/tmp/video.mp4')
