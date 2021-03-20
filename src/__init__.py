import base64
import os
from datetime import datetime

import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask('image-processing')

if os.environ.get('APP_ENV', '') == 'development':
    app.config['DEBUG'] = True


# for health check
@app.route('/health', methods=['GET'])
def health() -> str:
    return '200'


@app.route('/image', methods=['POST'])
def process_image() -> object:
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('image-processing-181562662531')

        img = request.files['image'].read()
        img_base64 = base64.b64encode(img).decode('utf-8')
        img_file = base64.b64decode(img_base64.encode('UTF-8'))

        time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        key = time_str + '.png'

        bucket.put_object(
            Body=img_file,
            Key=key
        )

        return jsonify({
            'status': 'success',
            'result': {
                'image': img_base64
            }
        })
    except Exception as e:
        print(e)

        return jsonify({
            'status': 'failure',
            'message': str(e)
        })


CORS(app)
