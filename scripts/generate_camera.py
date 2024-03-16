import json
import numpy as np

class CameraTransformer:
    def __init__(self, json_path):
        self.json_path = json_path
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.matrix = np.array(self.data['frames'][0]['transform_matrix'])

    # def get_translation_matrix(self, direction, distance=0.1):
    #     if direction == 'd':
    #         translation = np.array([0, distance, 0])
    #     elif direction == 'a':
    #         translation = np.array([0, -distance, 0])
    #     elif direction == 'w':
    #         translation = np.array([-distance, 0, 0])
    #     elif direction == 's':
    #         translation = np.array([distance, 0, 0])
    #     elif direction == 'up':
    #         translation = np.array([0, 0, distance])
    #     elif direction == 'down':
    #         translation = np.array([0, 0, -distance])
    #     else:
    #         raise ValueError(f"Unknown direction: {direction}")

    #     translation_matrix = np.eye(4)
    #     translation_matrix[:3, 3] = translation
    #     return translation_matrix
    def get_translation_matrix(self, direction, distance=0.1):
        if direction == 'd':
            translation = np.array([distance, 0, 0])
        elif direction == 'a':
            translation = np.array([-distance, 0, 0])
        elif direction == 'w':
            translation = np.array([0, 0, -distance])
        elif direction == 's':
            translation = np.array([0, 0, distance])
        elif direction == 'up':
            translation = np.array([0, distance, 0])
        elif direction == 'down':
            translation = np.array([0, -distance, 0])
        else:
            raise ValueError(f"Unknown direction: {direction}")
        # 将平移向量旋转到相机的局部坐标系
        rotation_matrix = self.matrix[:3, :3]
        translation = np.dot(rotation_matrix, translation)

        translation_matrix = np.eye(4)
        translation_matrix[:3, 3] = translation
        return translation_matrix

    def get_rotation_matrix(self, pitch, yaw, roll):
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


        

    # def update_matrix(self, translation=None, rotation=None):
    #     if translation is not None:
    #         direction, distance = translation
    #         translation_matrix = self.get_translation_matrix(direction, distance)
    #         self.matrix = np.dot(translation_matrix, self.matrix)

    #         # 更新 x, y, z 的值
    #         if direction == 'd':
    #             self.data['y'] += distance
    #         elif direction == 'a':
    #             self.data['y'] -= distance
    #         elif direction == 'w':
    #             self.data['x'] -= distance
    #         elif direction == 's':
    #             self.data['x'] += distance
    #         elif direction == 'up':
    #             self.data['z'] += distance
    #         elif direction == 'down':
    #             self.data['z'] -= distance

    #     if rotation is not None:
    #         pitch, yaw, roll = rotation
    #         rotation_matrix = self.get_rotation_matrix(pitch, yaw, roll)
    #         self.matrix = np.dot(rotation_matrix, self.matrix)

    #         # 更新 pitch, yaw, roll 的值
    #         self.data['pitch'] += pitch
    #         self.data['yaw'] += yaw
    #         self.data['roll'] += roll

    #     return self.matrix
    def update_matrix(self, translation=None, rotation=None):
        if translation is not None:
            direction, distance = translation
            translation_matrix = self.get_translation_matrix(direction, distance)
            self.matrix = np.dot(translation_matrix, self.matrix)

            # 更新 x, y, z 的值
            translation_vector = self.get_translation_vector(direction, distance)
            self.data['x'] = round(self.data['x'] + translation_vector[0])
            self.data['y'] = round(self.data['y'] + translation_vector[1])
            self.data['z'] = round(self.data['z'] + translation_vector[2])

        if rotation is not None:
            pitch, yaw, roll = rotation
            rotation_matrix = self.get_rotation_matrix(pitch, yaw, roll)
            self.matrix = np.dot(rotation_matrix, self.matrix)

            # 更新 pitch, yaw, roll 的值
            self.data['pitch'] += pitch
            self.data['yaw'] += yaw
            self.data['roll'] += roll

        return self.matrix
    def get_translation_vector(self, direction, distance):
        if direction == 'd':
            translation = np.array([distance, 0, 0])
        elif direction == 'a':
            translation = np.array([-distance, 0, 0])
        elif direction == 'w':
            translation = np.array([0, 0, -distance])
        elif direction == 's':
            translation = np.array([0, 0, distance])
        elif direction == 'up':
            translation = np.array([0, distance, 0])
        elif direction == 'down':
            translation = np.array([0, -distance, 0])
        else:
            raise ValueError(f"Unknown direction: {direction}")

        # 将平移向量转换到全局坐标系下
        rotation_matrix = self.get_rotation_matrix(self.data['pitch'], self.data['yaw'], self.data['roll'])
        translation = np.dot(rotation_matrix[:3, :3], translation)

        return translation

    def save(self):
        x = str(self.data.get('x', ''))
        y = str(self.data.get('y', ''))
        z = str(self.data.get('z', ''))
        pitch = str(self.data.get('pitch', ''))
        yaw = str(self.data.get('yaw', ''))
        roll = str(self.data.get('roll', ''))
        self.data['frames'][0]['transform_matrix'] = self.matrix.tolist()
        self.data['frames'][0]['file_path'] = '_'.join([x, y, z, pitch, yaw, roll]) + '.png'
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f, indent=2)