from celery import Celery
import subprocess
import time

app = Celery('tasks', broker='sqla+sqlite:///celerydb.sqlite', backend='db+sqlite:///celerydb.sqlite')

@app.task
def to_mp4(m3u8_url, output_path):
    cmd = 'ffmpeg -loglevel panic -protocol_whitelist file,http,https,tcp,tls -i {m3u8_path} -c copy {output_path}'.format(m3u8_path=m3u8_url, output_path=output_path).split()
    proc = subprocess.Popen(cmd)
    proc.wait()
    if proc.returncode == 0:
        time.sleep(2)
        return output_path
    else:
        return "error"

