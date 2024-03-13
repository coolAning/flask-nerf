from flask import Flask, request
import base64
import io
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

# @app.route('/upload', methods=['POST'])

# def upload():
#     # 获取上传的文件
#     file = request.files['file']
#     file_path = 'file.jpg'
#     file.save(file_path)
#     image=start('file.jpg')
#     byte_stream = io.BytesIO()
#     image.save(byte_stream, format='JPEG')
#     base64_string = base64.b64encode(byte_stream.getvalue()).decode('utf-8')

#     # 将base64编码的内容返回给客户端
#     return base64_string, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(port=6000)