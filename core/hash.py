# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/2/29
@Software: PyCharm
@disc:
======================================="""
import hashlib
import json


# 首先，计算图片的哈希值
def get_file_hash(file_path):
    BUF_SIZE = 65536  # 读取文件的缓冲区大小
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


# 接着，获取参数字典的哈希值
def get_params_hash(params):
    # 确保参数字典有序，以保证哈希值的一致性
    params_string = json.dumps(params, sort_keys=True)
    return hashlib.sha256(params_string.encode('utf-8')).hexdigest()


# 将图片哈希和参数哈希连在一起，再次进行哈希计算得到最终哈希值
def get_combined_hash(img_filepath, params):
    img_hash = get_file_hash(img_filepath)
    params_hash = get_params_hash(params)

    combined_hash_input = (img_hash + params_hash).encode('utf-8')
    return hashlib.sha256(combined_hash_input).hexdigest()