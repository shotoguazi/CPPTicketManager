# CPPTicketManager

CPP抢票、CP30抢票、漫展抢票、无差别同人站、CP展、CPGZ

> [!NOTE]
> 本软件禁止作用于任何商业用途！
> 使用本软件所产生的后果请自行承担！

## 使用说明

目前支持手机号+密码或验证码方式登录，登录后会生成cookies.json文件，多开可以共用此cookies，无需二次登录

选择门票和购票人的时候请输入数字序号选择

定时器目前的格式为"年月日 时分秒"， 定时为2024年9月1日 12:00即输入"20240901 120000"，可以在time_convert函数中修改成其他格式

## 运行方法

使用前请确保你已经安装了python3并且pip功能正常
在项目文件夹右键空白处，选择“在终端打开”，输入以下内容：
```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```
随后运行CPPTicketManager 0.1.py文件，即可正常使用

## 兼容性

经过cpgz06的测试，本软件可直接部署在Windows和Linux环境下，由于不同Linux发行版配置不同，请自行进行配置

软件使用Python3.12编写
