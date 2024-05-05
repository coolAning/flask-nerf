import subprocess
from celery import Celery, current_task
from flask import current_app
import requests

redis_config='redis://127.0.0.1:6379/0'

celery_app = Celery(__name__, backend=redis_config, broker=redis_config)


@celery_app.task
def async_add(x, y):
    return x + y

@celery_app.task(bind=True)
def train(self , name , n_steps):
    
    command = ["python", "scripts/run.py", "--scene", f"./data/nerf/{name}", "--train", "--n_steps", str(n_steps), "--save_snapshot", f"data/nerf/{name}/{name}.ingp"]
    
    # 创建一个子进程来运行命令，并获取子进程的输出
    process = subprocess.Popen(command, cwd='./', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    while True:
        # 读取一行输出
        output = process.stdout.readline()
        if output:
            # 更新任务状态
            self.update_state(state='PROGRESS', meta={'current': output})
            
        # 如果子进程已经结束，那么退出循环
        if process.poll() is not None:
            break

    rc = process.poll()

    # 更新任务状态为 'SUCCESS'
    self.update_state(state='SUCCESS', meta={'current': 'Task completed'})
    
    task_id = self.request.id
    url = 'http://118.202.10.154:5000/camera/complete'
    data = {'task_id': task_id}
    response = requests.post(url, json=data)
    

    return rc