# UCAS_course_select  

---
#### 国科大抢课脚本2021        
---
#### 使用方式
 
1. 安装Python3，官网链接`https://www.python.org/downloads/`
2. 安装python的requests库（Windows系统CMD内执行`pip install requests`）
3. 在`main.py`文件内添加用户名和密码(或者选择cookie登录)，以及待添加课程（默认为非学位课）
> 当前目录下的`Cookie.txt`文件里的cookie应当包括`sepuser`及`JSESSIONID`关键字，否则无效。
>> 示例: `sepuser="bSlkPWQ4N2M4MzZkLWViNDgtYGEyMC05ZDgwLTI4YzZiYWVhM2I0NQ==  "; JSESSIONID=D0B4FB746594E772D8D4EF442ADD3000`
4. 若登录SEP需要验证码，在`certcode.py`内完善验证码识别方式。  
> 注：作者使用的是`3032数据(https://www.3023data.com/)`的验证码识别API。若也想用这个，只需添加个人key就好。
5. 执行`main.py`脚本，具体方式可百度。


#### 注：
1. 亲测可用，使用前可用非限选课进行测试。
2. 校园网不稳定，远程主机频频强迫关闭连接，可用非校园网进行验证码识别登录，或者选择课程界面的cookie登录（已设置keep-alive但仍有失效风险）。
3. 本项目将于2021年7月停止更新。