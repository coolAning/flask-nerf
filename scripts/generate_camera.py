import json
import numpy as np

# 读取JSON文件
with open('data/nerf/fox/camera.json', 'r') as f:
    data = json.load(f)

# 获取第一个frame的transform_matrix
matrix = np.array(data['frames'][0]['transform_matrix'])

# 定义一个函数，根据方向生成一个平移矩阵
def get_translation_matrix(direction, distance=0.1):
    if direction == 'up':
        translation = np.array([0, distance, 0])
    elif direction == 'down':
        translation = np.array([0, -distance, 0])
    elif direction == 'left':
        translation = np.array([-distance, 0, 0])
    elif direction == 'right':
        translation = np.array([distance, 0, 0])
    elif direction == 'forward':
        translation = np.array([0, 0, distance])
    elif direction == 'backward':
        translation = np.array([0, 0, -distance])
    else:
        raise ValueError(f"Unknown direction: {direction}")

    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = translation
    return translation_matrix

# 定义一个函数，根据欧拉角生成一个旋转矩阵
def get_rotation_matrix(pitch, yaw, roll):
    pitch = np.radians(pitch)
    yaw = np.radians(yaw)
    roll = np.radians(roll)

    rotation_x = np.array([[1, 0, 0],
                           [0, np.cos(pitch), -np.sin(pitch)],
                           [0, np.sin(pitch), np.cos(pitch)]])
    rotation_y = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                           [0, 1, 0],
                           [-np.sin(yaw), 0, np.cos(yaw)]])
    rotation_z = np.array([[np.cos(roll), -np.sin(roll), 0],
                           [np.sin(roll), np.cos(roll), 0],
                           [0, 0, 1]])

    rotation = np.dot(rotation_z, np.dot(rotation_y, rotation_x))

    rotation_matrix = np.eye(4)
    rotation_matrix[:3, :3] = rotation
    return rotation_matrix

# 定义一个函数，根据平移和旋转的需求更新矩阵
def update_matrix(matrix, translation=None, rotation=None):
    if translation is not None:
        direction, distance = translation
        translation_matrix = get_translation_matrix(direction, distance)
        matrix = np.dot(translation_matrix, matrix)

    if rotation is not None:
        pitch, yaw, roll = rotation
        rotation_matrix = get_rotation_matrix(pitch, yaw, roll)
        matrix = np.dot(rotation_matrix, matrix)

    return matrix

# 更新矩阵
# new_matrix = update_matrix(matrix, translation=('up', 0.1), rotation=(-30, -20, 0))  #欧拉角：俯仰角 偏航角 翻滚角
new_matrix = update_matrix(matrix, translation=('backward', 1))  #欧拉角：俯仰角 偏航角 翻滚角
# 更新JSON数据
data['frames'][0]['transform_matrix'] = new_matrix.tolist()

# 保存修改后的JSON文件
with open('data/nerf/fox/camera.json', 'w') as f:
    json.dump(data, f, indent=2)