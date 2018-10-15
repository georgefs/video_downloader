from celery import Celery
import subprocess
import time
import requests
import re
import os

app = Celery('tasks', broker='sqla+sqlite:///celerydb.sqlite', backend='db+sqlite:///celerydb.sqlite')

@app.task
def to_mp4(m3u8_url, output_path, st=0, t=None):
    content = requests.get(m3u8_url).text
    vs = re.findall(".*.ts", content)
    vs = [v.strip() for v in vs]
    source = "|".join(vs)

    if t:
        cmd = 'ffmpeg -loglevel panic -protocol_whitelist concat,file,http,https,tcp,tls -i concat:{source} -vcodec copy -ss {st} -t {t} {output_path}'.format(source=source, output_path=output_path, st=st, t=t).split()
    elif st:
        cmd = 'ffmpeg -loglevel panic -protocol_whitelist concat,file,http,https,tcp,tls -i concat:{source} -vcodec copy -ss {st} {output_path}'.format(source=source, output_path=output_path, st=st).split()
    else:
        cmd = 'ffmpeg -loglevel panic -protocol_whitelist concat,file,http,https,tcp,tls -i concat:{source} -vcodec copy {output_path}'.format(source=source, output_path=output_path, st=st).split()

    proc = subprocess.Popen(cmd)
    proc.wait()
    if proc.returncode == 0:
        time.sleep(2)
        return output_path
    else:
        return "error"
