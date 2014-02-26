# -*- coding: utf-8 -*-
from PIL import Image
from datetime import datetime
import math
import urllib
import imghdr
import os
import uuid

# 水印图片路径
_long_jpg = ''.join([os.path.dirname(__file__), '/long.jpg'])

# 保存url图片
def save_img(img_url, target_dir):
    filename = unique_filename()
    # 原始图片
    data = urllib.urlopen(img_url).read()
    target_path = target_dir + filename  # target_dir '/'结尾
    with open(target_path, 'wb') as f:
        f.write(data)

    return {
        'name': filename,
        'path': target_path,
        'size': get_image_size(target_path)
    }


# 压缩图片
def thumbnail_img(filename, filedir):
    filepath = filedir + filename
    # 对于gif类型图片，原图即为缩略图 FIXME
    if get_image_type(filepath) == 'gif':
        return {
            'name': filename,
            'path': filepath,
            'size': get_image_size(filepath)
        }

    crop = False
    # 缩略图尺寸
    resize = (210, 420)
    with open(filepath, 'rb') as f:
        img = Image.open(f)
        ori_width, ori_height = img.size
        _, new_height = img.size

        new_img = img
        # 设置裁剪区域
        if ori_width * 2 < ori_height:
            new_height = int(math.ceil(resize[1] * (float(ori_width) / resize[0])))
            if new_height > ori_height:
                new_height = ori_height

            if new_height != ori_height:
                crop = True
                box = (0, 0, ori_width, new_height)
                new_img = img.crop(box)

        # 生成缩略图
        new_img.thumbnail(resize, Image.ANTIALIAS)
        # 简单判断是否为长图
        if crop and ori_height - new_height > resize[0]:
            with open(_long_jpg, 'rb') as lf:  # FIXME path
                mark_img = Image.open(lf)
                new_img.paste(mark_img, (new_img.size[0] - mark_img.size[0], new_img.size[1] - mark_img.size[1]),
                              mark_img.convert('RGBA'))

        # 保存缩略图
        target_path = filedir + filename + '.thumb'
        new_img.save(target_path, "JPEG")
    # end
    return {
        'name': filename + '.thumb',
        'path': target_path,
        'size': get_image_size(target_path)
    }


# 获取图片尺寸
def get_image_size(filepath):
    img = Image.open(filepath)
    return img.size


# 获取图片类型，如果不是图片返回None
def get_image_type(filepath):
    return imghdr.what(filepath)


def unique_filename():
    date_prefix = datetime.now().strftime('%Y%m%d')
    filename = str(uuid.uuid1()).replace('-', '')
    return date_prefix + '_' + filename
