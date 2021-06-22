import UCAS
import time
import os
from UCAS import CookieError, LoginError, UCAS

# 来源：Github Mondayfirst的UCAS_course_select项目

# 设置cookie，非必选
if os.path.isfile("Cookie.txt"):
    with open("Cookie.txt", 'r', encoding='utf-8') as f:
        cookie = f.read()
else:
    cookie = ''
# 设置用户名和密码
userName = ''  # 用户名
password = ''  # 密码

# 设置拟抢课课程。字典键为添加课程编号，值为冲突课程编号的列表，当要添加该课程时，先自动删除冲突的课程
add_class_dict = {
    '040203MGX002H': [],  # 示例：说谎心理学
}
# 添加院系ID，若列表为空，则默认为全部院系
deptID_list = [
    # '968',  # 心理学系
]

# 进行相关设置
user = UCAS(userName, password, cookie)
user.flag_login = True  # False为先使用cookie，True为先使用用户名和密码登录
while True:
    try:
        print(f"========{time.strftime('%Y-%m-%d %H:%M:%S')}========")
        user.login()
        user.main_selectClass(add_class_dict, deptID_list)
    except CookieError as e:
        print(e.message)
        user.flag_login = True
        user.s = ""
    except LoginError as e:
        print(e.message)
        seconds = 600
        print(f"等待{seconds}秒尝试下次登录")
        time.sleep(seconds)
        user.flag_login = True
    except Exception as e:
        print(e)
    finally:
        time.sleep(1)  # 设置间隔时间,单位为秒
