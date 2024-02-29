# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/2/29
@Software: PyCharm
@disc:
======================================="""
import base64
import json
import os
import time
from datetime import datetime
import urllib.request
from core.hash import get_combined_hash

webui_server_url = 'http://218.31.113.195:57860'
out_dir = 'api_out'
out_dir_i2i = os.path.join(out_dir, 'img2img')


def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    if not os.path.exists(out_dir_i2i):
        os.makedirs(out_dir_i2i)
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def call_img2img_api(save_path: str, **payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')):
        decode_and_save_base64(image, save_path)
    return save_path


def bulk_frame_diffusion():
    pass


def frame_diffusion(frame_img_fp, params, batch_size: int = 1):
    init_images = [
        encode_file_to_base64(frame_img_fp),
        # "https://image.can/also/be/a/http/url.png",
    ]
    payload = {
        **params
    }
    payload["init_images"] = init_images
    payload["batch_size"] = batch_size if len(init_images) == 1 else len(init_images)
    # "mask": encode_file_to_base64(r"/Users/shadikesadamu/Pictures/img.png")

    # if len(init_images) > 1 then batch_size should be == len(init_images)
    # else if len(init_images) == 1 then batch_size can be any value int >= 1
    print("params:", params)
    hash_value = get_combined_hash(frame_img_fp, params)
    print("hash_value:", hash_value)
    save_fp = os.path.join(out_dir_i2i, f'{hash_value}.png')
    if not os.path.exists(save_fp):
        call_img2img_api(save_fp, **payload)
    return save_fp


if __name__ == '__main__':
    init_images = [
        encode_file_to_base64(r"/Users/shadikesadamu/Pictures/vlcsnap-2024-02-29-05h24m21s922.png"),
        # encode_file_to_base64(r"B:\path\to\img_2.png"),
        # "https://image.can/also/be/a/http/url.png",
    ]
    batch_size = 2
    Seed = 1666545269
    payload = {
        "prompt": "1girl, blue hair",
        "seed": 1,
        "steps": 20,
        "width": 512,
        "height": 512,
        "denoising_strength": 0.5,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": batch_size if len(init_images) == 1 else len(init_images),
        # "mask": encode_file_to_base64(r"/Users/shadikesadamu/Pictures/img.png")
    }
    # if len(init_images) > 1 then batch_size should be == len(init_images)
    # else if len(init_images) == 1 then batch_size can be any value int >= 1
    call_img2img_api(**payload)
