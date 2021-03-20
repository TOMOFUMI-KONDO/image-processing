import base64
import os
from datetime import datetime
from typing import List

import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

from src.image_process import main

app = Flask('image-processing')
app_env = os.environ.get('APP_ENV', '')

if app_env == 'development':
    app.config['DEBUG'] = True


# for health check
@app.route('/health', methods=['GET'])
def health() -> str:
    return '200'


@app.route('/image', methods=['POST'])
def process_image() -> object:
    try:
        img = request.files['image'].read()
        img_base64_bytes = base64.b64encode(img)

        converted_imgs_base64_bytes = [img_base64_bytes]
        # note(kondo): 画像処理が途中でこけるので、一旦実行しないようにしている
        # converted_imgs_base64_bytes = main(img_base64_bytes)
        converted_imgs_base64_str = [
            converted_img_base64_bytes.decode('utf-8')
            for converted_img_base64_bytes in converted_imgs_base64_bytes
        ]

        if app_env == 'production':
            put_s3(converted_imgs_base64_bytes)

        return jsonify({
            'status': 'success',
            'result': {
                'image': converted_imgs_base64_str
            }
        })
    except Exception as e:
        print(e)

        return jsonify({
            'status': 'failure',
            'message': str(e)
        })


def put_s3(imgs_base64: List[bytes], extension='png'):
    imgs = [base64.b64decode(img_base64) for img_base64 in imgs_base64]

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(os.environ.get('S3_BUCKET', ''))

    time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    for index, img in enumerate(imgs):
        key = f'{time_str}-{index}.{extension}'

        bucket.put_object(
            Body=img,
            Key=key
        )


CORS(app)
