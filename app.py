from sanic import Sanic
from sanic.response import json
from sanic.response import text
import pickle
import numpy as np
import sys
import requests
import settings
from PIL import Image
from acquire_picture import img_denoise,img_split,img_list_to_array_list,get_image_url_and_filename
from io import BytesIO
from settings import image_api, query_api, img_api_headers, query_api_headers

import time
import datetime

app = Sanic()

@app.route('/')
async def test(request):
    return json({'hello': 'world'})

# 识别验证码
def img_verify_code(img):

    img = img_denoise(img,settings.threshold)
    img_list = img_split(img,settings.img_split_start,settings.img_split_width)
    array_list = img_list_to_array_list(img_list)
    model = pickle.load(open("model.pkl", "rb+"))
    code = model.predict(array_list)
    return "".join(code)

@app.route('/code',methods=['GET'])
async def getCode(request):
    try:
        start = time.time()
        img_url = request.raw_args.get('img_url')
        print(img_url)
        # 获取验证码图片并猜测
        startTime = time.time()
        img_resp = requests.get(img_url, timeout=10)
        dEndTime = time.time()
        if img_resp.status_code == 200:
            images = Image.open(BytesIO(img_resp.content))
            code = img_verify_code(images)
            VendTime = time.time()
            print('下载时间')
            print  (int(round((dEndTime - startTime) * 1000)))
            print('识别时间')
            print (int(round((VendTime - dEndTime) * 1000)))

            print('下载 - 识别时间')
            print (int(round((VendTime - startTime) * 1000)))

            print('开始时间 - 结束时间')
            print (int(round((VendTime - start) * 1000)))
            return json({'code': code})
        else:
            return json({'code': 0})
    except Exception:
        print("重新获取代理")
        return json({'code':0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8007, workers=4, debug=False, access_log=False)
