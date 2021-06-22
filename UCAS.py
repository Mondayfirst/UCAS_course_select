import re
import requests
import certcode

# 来源：Github Mondayfirst的UCAS_course_select项目

timeout = 1  # 设置请求等待时长，单位为秒
ERRORCOUNT = 2

UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApplehtmlKit/537.36 (KHTML, like Gecko)'
UserAgent += ' Chrome/91.0.4472.106 Safari/537.36'


class UCAS:
    def __init__(self, user_name='', password='', cookie='') -> None:
        # 参数预设
        self.cookie = cookie
        self.userName = user_name
        self.password = password

        # 默认参数
        self.s = ''  # 选课界面的个人编号
        self.flag_login = True if len(self.userName) and len(self.password) else False
        self.commenHeader = {
            "User-Agent": UserAgent,  # 必要
            "Host": "jwxk.ucas.ac.cn",
            "Connection": "keep-alive",
            "Origin": "http://jwxk.ucas.ac.cn",
        }
        self.__cookie_error_count__ = ERRORCOUNT
        self.session = requests.session()
        self.session.headers.update(self.commenHeader)

    def __cookie_invalid__(self, cookie_isTrue):
        if cookie_isTrue:
            self.__cookie_error_count__ = ERRORCOUNT
        else:
            if self.__cookie_error_count__ > 0:
                self.__cookie_error_count__ -= 1
                raise ValueError(f"Cookie失效第{ERRORCOUNT-self.__cookie_error_count__}次")
            else:
                self.__cookie_error_count__ = ERRORCOUNT
                raise CookieError("Cookie失效，请重新设置Cookie! 或者重新登录")

    def login(self):
        if self.flag_login:
            if not len(self.userName) or not len(self.password):
                raise LoginError("登录失败，用户名或密码为空!")
            print("重新登录中......")
            data = {
                'userName': self.userName,
                'pwd': self.password,
                'sb': 'sb',
            }
            html = self.session.get("http://sep.ucas.ac.cn/").text
            if "验证码" in html:
                certCode = certcode.certCode(self.session)
                data['certCode'] = certCode
            self.session.post('http://sep.ucas.ac.cn/slogin', data, timeout=10)
            html = self.session.get('http://sep.ucas.ac.cn/portal/site/226/821', timeout=timeout)
            Indentity = re.findall('http://jwxk.ucas.ac.cn/login\?Identity=(.*?)&roleId', html.text, re.S)
            if not len(Indentity):
                raise LoginError("登录失败，用户名或密码错误，或需要验证码！")
            self.session.get('http://jwxk.ucas.ac.cn/login?Identity=' + Indentity[0], timeout=timeout)
            self.session.get('http://jwxk.ucas.ac.cn/subject/humanityLecture', timeout=timeout)
            cookie_dict = {
                cookie.name: cookie.value
                for cookie in self.session.cookies if 'undefined' not in cookie.value
            }
            self.cookie = '; '.join([name + '=' + cookie_dict[name] for name in cookie_dict])
            with open('Cookie.txt', 'w', encoding='utf-8') as f:
                f.write(self.cookie)
            self.flag_login = False
        else:
            if not len(self.cookie):
                raise LoginError("登录失败，未输入用户名和密码，或者Cookie")

    def getMessageFromMainPage(self):
        url = 'http://jwxk.ucas.ac.cn/courseManage/main'
        self.session.headers["Cookie"] = self.cookie
        html = self.session.get(url, timeout=timeout).text
        s = re.findall('selectCourse\?s=(.*?)"', html, re.S)
        self.__cookie_invalid__(len(s))
        s = s[0]
        deptID = re.findall(
            'type="checkbox" name="deptIds" id="id_(.*?)" value="..."/> <label for="id_...">(.*?)</label></div>', html,
            re.S)
        # print(s, deptID)
        return s, deptID

    def getMessageOfCourse(self, deptIds):
        url = "http://jwxk.ucas.ac.cn/courseManage/selectCourse?s=" + self.s
        self.session.headers['Cookie'] = self.cookie
        postdata = {
            'deptIds': deptIds,
            'sb': 0,
        }
        html = self.session.post(url, postdata, timeout=timeout).text
        self.__cookie_invalid__("失效" not in html)
        course_sid = re.findall('"courseCode_(.*?)">', html, re.S)
        course_code = re.findall('"courseCode_.*?">(.*?)</span></a></td>', html, re.S)
        course_index = re.findall('href="/course/courseplan/(.*?)"', html, re.S)
        course_name = re.findall('<td><a href="/course/coursetime/.*?" target="_blank">(.*?)</a></td>', html, re.S)
        course_student_request = re.findall('courseCredit_.*?<td>(.*?)</td>.*?>.*?</td>', html, re.S)
        course_student_already = re.findall('courseCredit_.*?<td>.*?</td>.*?>(.*?)</td>', html, re.S)
        if not (len(course_sid) == len(course_code) == len(course_index) == len(course_name) ==
                len(course_student_request) == len(course_student_already)):
            raise ValueError("读取列表失败")
        course_dict = {}
        for i in range(len(course_sid)):
            course_dict[course_code[i]] = \
                [course_sid[i], course_index[i], course_name[i],
                    course_student_request[i], course_student_already[i]]
        # print(course_dict)
        return course_dict

    def viewResults(self):
        # 查看选课结果
        url = "http://jwxk.ucas.ac.cn/courseManage/main?s=" + self.s
        self.session.headers['Cookie'] = self.cookie
        html = self.session.get(url, timeout=timeout).text
        error = re.findall('<label id="loginError" class="error">(.*?)</label>', html, re.S)[0]
        success = re.findall('<label id="loginSuccess" class="success">(.*?)</label>', html, re.S)[0]
        if len(error):
            error = error.replace('<br/>', '\n')
            print(error.strip())
        if len(success):
            success = success.replace('<br/>', '\n')
            print(success.strip())

    def addCourse(self, deptIds, sids):
        # 发送选课请求
        url = "http://jwxk.ucas.ac.cn/courseManage/saveCourse?s=" + self.s
        self.session.headers['Cookie'] = self.cookie
        postdata = {
            'deptIds': deptIds,
            'sids': sids,
        }
        self.session.post(url, postdata, timeout=timeout)
        self.viewResults()

    def deleteCourse(self, index):
        url = 'http://jwxk.ucas.ac.cn/courseManage/delTemp/' + index + '?s=' + self.s
        self.session.headers['Cookie'] = self.cookie
        self.session.get(url, timeout=timeout)
        self.viewResults()

    def main_selectClass(self, add_class_dict: dict, deptID_list: list = []):
        if not len(self.s) or not len(deptID_list):
            # 从主页面获取url唯一后缀以及院系ID
            self.s, deptID_List_temp = self.getMessageFromMainPage()
            # 院系信息重组织
            if not len(deptID_list):
                deptID_list = {i[0] for i in deptID_List_temp}
        # 获取所有课程的信息
        course_dict = self.getMessageOfCourse(deptID_list)
        # 通过已选和限选人数进行判断，获取现在可以添加的课程及其信息
        new_dict = findAddableCourse(add_class_dict, course_dict)
        if len(new_dict):
            # 获取需要删除的课程编号列表
            delete_class_list = []
            for i in new_dict:
                delete_class_list += add_class_dict[i]

            # 删除课程
            for i in delete_class_list:
                deleteindex = new_dict[i][1]
                print(f"课程：{new_dict[i][2]}拟删除")
                self.deleteCourse(deleteindex)

            # 添加课程
            self.addCourse(deptID_list, [new_dict[i][0] for i in new_dict])


class CookieError(Exception):
    def __init__(self, message):
        self.message = message


class LoginError(Exception):
    def __init__(self, message):
        self.message = message


def findAddableCourse(add_class_list, course_dict):
    for i in add_class_list:
        if i not in course_dict:
            print(f"课程{i}选课成功！或课表已无该课程！")
    filter_course_dict = {i: course_dict[i] for i in add_class_list if i in course_dict}
    find_optional_course_dict = {}
    for ID in filter_course_dict:
        course = filter_course_dict[ID]
        if int(course[3]) > 0 and int(course[3]) <= int(course[4]):
            print(f"选课失败：课程[{course[2]}]，可选人数{course[3]}，已选人数为{course[4]}")
            pass
        else:
            find_optional_course_dict[ID] = course
            print(f"课程{course[2]}可选，拟发送选课请求")
    return find_optional_course_dict