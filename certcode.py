"""验证码识别文件，在此文件夹修改验证方式"""
import requests
from io import BytesIO
import base64
import json

# 来源：Github Mondayfirst的UCAS_course_select项目


def certCode(self):
    response = self.session.get("http://sep.ucas.ac.cn/changePic")
    # 转换为base64格式
    pic_base64 = base64.b64encode(BytesIO(response.content).read())
    # 验证识别：网络方式，此处用的3023数据的验证码识别API，官网为https://www.3023data.com/
    url = 'http://api.3023data.com/ocr/captcha'
    headers = {'key': ''}  # 在此处设置个人key
    data = {
        'type': 2003,
        'minlength': 4,
        'maxlength': 4,
        'image': pic_base64,
    }
    res = json.loads(requests.post(url, headers=headers, data=data).text)["data"]["captcha"]
    # 保存图片文件，来查看输出是否正确
    imgdata = base64.b64decode(pic_base64)
    file = open('cercode_data.jfif', 'wb')
    file.write(imgdata)
    file.close()
    with open("cercode_label.txt", "w", encoding='utf-8') as f:
        f.write(res)
    return res