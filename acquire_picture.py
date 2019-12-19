#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import requests
import random
from settings import image_api, query_api, img_api_headers, query_api_headers
from numpy import array
from PIL import Image,ImageDraw
import queue
# 获取验证码
def save_image_to_file():

    myid = "340080181210211"
    new_id = myid.format(id=myid)
    img_api_url = image_api.format(id=new_id)
    img_api_resp = requests.get(img_api_url, headers=img_api_headers, timeout=10)
    img_url, filename = get_image_url_and_filename(img_api_resp.text)
    r = requests.get(img_url)
    with open("images/raw_picture/" + filename, "wb+") as f:
        f.write(r.content)
    '''
        for i in range(0,picture_num):
        r = requests.get(picture_url)
        random_num = str(random.random())[2:]
        with open("images/raw_picture/" + random_num + ".png", "wb+") as f:
            f.write(r.content)
    '''

# 灰度处理，二值化，降噪
def img_denoise(img, threshold):

    def init_table(threshold=threshold):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        return table

    img = img.convert("L").point(init_table(), '1')
    return img


def cfs(img):
    """传入二值化后的图片进行连通域分割"""
    pixdata = img.load()
    w,h = img.size
    visited = set()
    q = queue.Queue()
    offset = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    cuts = []
    for x in range(w):
        for y in range(h):
            x_axis = []
            #y_axis = []
            if pixdata[x,y] == 0 and (x,y) not in visited:
                q.put((x,y))
                visited.add((x,y))
            while not q.empty():
                x_p,y_p = q.get()
                for x_offset,y_offset in offset:
                    x_c,y_c = x_p+x_offset,y_p+y_offset
                    if (x_c,y_c) in visited:
                        continue
                    visited.add((x_c,y_c))
                    try:
                        if pixdata[x_c,y_c] == 0:
                            q.put((x_c,y_c))
                            x_axis.append(x_c)
                            #y_axis.append(y_c)
                    except:
                        pass
            if x_axis:
                min_x,max_x = min(x_axis),max(x_axis)
                if max_x - min_x >  3:
                    # 宽度小于3的认为是噪点，根据需要修改
                    cuts.append((min_x,max_x + 1))
    return cuts
 
def saveSmall(img, outDir, cuts):
    w, h = img.size
    pixdata = img.load()
    for i, item in enumerate(cuts):
        box = (item[0], 0, item[1], h)
        img.crop(box).save(outDir + str(i) + ".png")


# 图片分割
def img_split(img,img_split_start,img_split_width):
    img.save("test.jpg")
    # saveSmall(img,'cuts/',cfs(img))
    start = img_split_start
    width = img_split_width
    top = 0
    height = img.size[1]
    img_list = []
    for i in range(4):
        new_start = start + width * i
        box = (new_start, top, new_start + width, height)
        piece = img.crop(box)
        piece.save("%s.jpg" % i)
        img_list.append(piece)
    return img_list

# 将Image对象转换为array_list
def img_list_to_array_list(img_list):

    array_list = []
    for img in img_list:
        array_list.append(array(img).flatten())
    return array_list

# 获取验证码地址和文件名
def get_image_url_and_filename(resptext):

    name = resptext.split("/")[-1][:-3]
    url = "http://cet.neea.edu.cn/imgs/" + name
    print(url)
    return url,name

"""
if __name__ == "__main__":
    img = Image.open("2b86.png")
    img = img_denoise(img,128)
    img_list = img_split(img,20,20)
"""