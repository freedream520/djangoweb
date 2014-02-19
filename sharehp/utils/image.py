# -*- coding: utf-8 -*-
import common
import Image
import math
import urllib
import qiniu_helper

# 保存url图片
def save_img(img_url, target_dir):
    filename = common.unique_filename()
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
    crop = False
    # 缩略图尺寸
    resize = (210, 420)
    with open(filedir + filename, 'rb') as f:
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
            with open('long.jpg', 'rb') as lf:  # FIXME path
                mark_img = Image.open(lf)
                new_img.paste(mark_img, (new_img.size[0] - mark_img.size[0], new_img.size[1] - mark_img.size[1]),
                              mark_img.convert('RGBA'))

        # 保存缩略图
        target_path = filedir + 'thumbnail/' + filename
        new_img.save(target_path, "JPEG")
    # end
    return {
        'name': filename,
        'path': target_path,
        'size': get_image_size(target_path)
    }


# 用户头像
def crop_user_avatar(filedir, filename, box):
    with open(filedir + filename, 'rb') as f:
        img = Image.open(f)
        new_img = img.crop(box)

        target_path = filedir + filename
        # 保存缩略图 big
        new_img.thumbnail((100, 100), Image.ANTIALIAS)
        new_img.save(target_path + '.big', "JPEG")
        # 保存缩略图 middle
        new_img.thumbnail((36, 36), Image.ANTIALIAS)
        new_img.save(target_path + '.mid', "JPEG")
        # 保存缩略图 small
        new_img.thumbnail((28, 28), Image.ANTIALIAS)
        new_img.save(target_path + '.small', "JPEG")

    return {
        'big': {
            'name': filename + '.big',
            'path': target_path + '.big'},
        'mid': {
            'name': filename + '.mid',
            'path': target_path + '.mid'},
        'small': {
            'name': filename + '.small',
            'path': target_path + '.small'},
    }

# 获取图片尺寸
def get_image_size(filepath):
    img = Image.open(filepath)
    return img.size

# 上传文件至七牛
def qiniu_upload(filepath, tgturl):
    qiniu_helper.upload(filepath, tgturl)


