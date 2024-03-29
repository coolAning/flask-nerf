import os
import shutil
import subprocess
from flask import Flask, current_app, request
import zipfile
from celery_app import async_add, train
from flask import jsonify
import json
from scripts.generate_camera import CameraTransformer
from celery.result import AsyncResult
from celery_app import celery_app

app = Flask(__name__)

@app.route('/check', methods=['POST'])
def check():
    task_id = request.json.get("task_id")
    # 使用任务 ID 创建一个 AsyncResult 对象
    task = AsyncResult(task_id, app=celery_app)
    # 获取任务的状态和结果
    status = task.status
    result = task.result
    # 返回任务的状态和结果
    return jsonify({'status': status, 'result': result}), 200

@app.route('/upload', methods=['POST'])
def upload():
    # 获取上传的文件
    file = request.files['file']
    if file.filename.endswith('.zip'):
        # 提前处理文件名
        filename_without_ext = os.path.splitext(file.filename)[0]
        # 确保临时目录存在
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        # 保存文件到临时目录
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        # 确保目标目录存在
        target_dir = f'./data/nerf/{filename_without_ext}'
        os.makedirs(target_dir, exist_ok=True)
        # 解压文件到目标目录
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        # 删除临时文件
        os.remove(temp_path)
        n_steps = request.form.get('n_steps', 1000)
        result = train.delay(filename_without_ext, n_steps)
        
        # 创建camera.json文件
        
        # 读取 transforms.json 文件
        with open(f'./data/nerf/{filename_without_ext}/transforms.json', 'r') as f:
            data = json.load(f)

        # 创建一个新的字典，包含 transforms.json 文件中的所有参数
        new_data = {key: value for key, value in data.items() if key != 'frames'}

        # 添加 frames 列表的第一个元素
        new_data['frames'] = [data['frames'][0]]
        # 添加新的键值对
        
        new_data['x'] = 0
        new_data['y'] = 0
        new_data['z'] = 0
        new_data['pitch'] = 0
        new_data['yaw'] = 0
        new_data['roll'] = 0
        new_data['frames'][0]['file_path'] = '0_0_0_0_0_0.png'
        
        # 将新的数据写入 camera.json 文件
        with open(f'./data/nerf/{filename_without_ext}/camera.json', 'w') as f:
            json.dump(new_data, f, indent=2)
        
        
        # 返回一个包含任务 ID 的 JSON 响应
        return jsonify({'message': 'File uploaded and extracted.', 'task_id': result.id}), 200
    else:
        return 'Invalid file type. Please upload a zip file.', 400

@app.route('/render', methods=['POST'])
def render():
    data = request.get_json()
    origin = data.get('origin')
    filename = data.get('filename')
    if origin:
        # 相机回到原点
        # 读取 transforms.json 文件
        with open(f'./data/nerf/{filename}/transforms.json', 'r') as f:
            data = json.load(f)
        with open(f'./data/nerf/{filename}/camera.json', 'r') as f:
            new_data = json.load(f)
        new_data['frames'] = [data['frames'][0]]
        new_data['x'] = 0
        new_data['y'] = 0
        new_data['z'] = 0
        new_data['pitch'] = 0
        new_data['yaw'] = 0
        new_data['roll'] = 0
        new_data['frames'][0]['file_path'] = '0_0_0_0_0_0.png'
        # 将新的数据写入 camera.json 文件
        with open(f'./data/nerf/{filename}/camera.json', 'w') as f:
            json.dump(new_data, f, indent=2)
    else:
        
        # 调整相机位姿
        translation = data.get('translation')
        rotation = data.get('rotation')
        transformer = CameraTransformer(f'data/nerf/{filename}/camera.json')
        transformer.update_matrix(translation=translation, rotation=rotation)
        transformer.save()
    
    # 检查 screen_shot 目录是否存在，如果不存在则创建它
    # screenshot_dir = f'data/nerf/{filename}/screen_shot'
    screenshot_dir = f'static/screen_shot/{filename}'
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
        
    with open(f'./data/nerf/{filename}/camera.json', 'r') as f:
            new_data = json.load(f)
    x = new_data['x']
    y = new_data['y']
    z = new_data['z']
    pitch = new_data['pitch']
    yaw = new_data['yaw']
    roll = new_data['roll']
    if not os.path.exists(f'{screenshot_dir}/{x}_{y}_{z}_{pitch}_{yaw}_{roll}.png'):
        # 在命令行运行命令
        command = ["python", "scripts/run.py", "--load_snapshot", f"data/nerf/{filename}/{filename}.ingp", "--screenshot_transforms", f"data/nerf/{filename}/camera.json", "--screenshot_dir", screenshot_dir, "--screenshot_spp", "1"]
        subprocess.run(command)

    image_url = request.host_url + 'static/screen_shot/' + filename + '/' + f'{x}_{y}_{z}_{pitch}_{yaw}_{roll}.png'
    return jsonify({'message': 'render success', 'url': image_url}), 200
    
# 删除模型数据
@app.route('/delete', methods=['POST'])
def delete():
    
    data = request.get_json()
    filename = data.get('filename')
    # 删除模型数据
    model_dir = f"data/nerf/{filename}"
    print(f"Deleting {model_dir}")
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    else:
        return jsonify({'message': 'delete failed, model not found'}), 400
    # 删除截图
    screenshot_dir = f"static/screen_shot/{filename}"
    print(f"Deleting {screenshot_dir}")
    if os.path.exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    else:
        return jsonify({'message': 'delete failed, model not found'}), 400
        
    return jsonify({'message': 'delete success'}), 200


if __name__ == '__main__':
    app.run(port=5001,host='0.0.0.0')