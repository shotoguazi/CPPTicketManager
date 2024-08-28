# For personal use only, author @shotoguazi

import os
import time
import json
import ntplib
import string
import secrets
import hashlib
import requests
from loguru import logger
from datetime import datetime


logger.add("CPP.log")
ticket_id = ""
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'origin': 'https://cp.allcpp.cn',
    'priority': 'u=1, i',
    'referer': 'https://cp.allcpp.cn/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
}


def init_cookies(cookies_dict):
    try:
        if cookies_dict:
            cookies_json = {"JSESSIONID": cookies_dict["JSESSIONID"], "token": cookies_dict["token"]}
            logger.debug(f"格式化Cookies：{cookies_json}")
            return cookies_json
    except Exception as e:
        logger.error(e)


def get_cookies():
    try:
        while True:
            print("0 | 手机号+密码登录")
            print("1 | 手机号+验证码登录")
            mode = input("请选择登录模式：")
            if mode == "0":  # 密码登录
                while True:
                    phone = input("请输入手机号：")
                    password = input("请输入密码：")
                    login_url = "https://user.allcpp.cn/api/login/normal"
                    payload = f"account={phone}&password={password}&phoneAccountBindToken=undefined&thirdAccountBindToken=undefined"
                    response = requests.request("POST", login_url, headers=headers, data=payload)
                    res_json = response.json()
                    logger.info(f"登录返回内容： {res_json}")
                    if "token" in res_json:
                        cookies_dict = response.cookies.get_dict()
                        logger.info(f"cookies：{cookies_dict}")
                        cookies_json = init_cookies(cookies_dict)
                        with open('cookies.json', mode='w', encoding='UTF-8') as f:
                            json.dump(cookies_json, f)
                        logger.info("写入Cookies文件！")
                        return response.cookies
                    else:
                        logger.error(f"未知错误！返回值{response}，返回内容{response.text}")
            elif mode == "1":  # 验证码登录
                while True:
                    phone = input("请输入手机号：")
                    response = requests.get(f"https://user.allcpp.cn/api/code/phone?country=86&phone={phone}", headers=headers)
                    if response.text == "SUCCESS:提交成功！":
                        logger.info("验证码发送成功！")
                        time.sleep(0.02)
                        while True:
                            code = input("请输入验证码：")
                            payload = f"country=86&phone={phone}&phoneCode={code}"
                            response = requests.get(
                                f"https://user.allcpp.cn/api/code/valid/phone?country=86&phone={phone}&phoneCode={code}")
                            if response.text:
                                login_url = "https://user.allcpp.cn/api/login/phone/code"
                                response = requests.request("POST", login_url, headers=headers, data=payload)
                                res_json = response.json()
                                logger.info(f"登录返回内容： {res_json}")
                                if "token" in res_json:
                                    cookies_dict = response.cookies.get_dict()
                                    logger.info(f"cookies：{cookies_dict}")
                                    cookies_json = init_cookies(cookies_dict)
                                    with open('cookies.json', mode='w', encoding='UTF-8') as f:
                                        json.dump(cookies_json, f)
                                    logger.info("写入Cookies文件！")
                                    return response.cookies
                            else:
                                logger.warning("验证码错误！")
                    else:
                        logger.error(f"未知错误！返回值{response}，返回内容{response.text}")
            else:
                logger.error("输入内容不合法！")
    except Exception as e:
        logger.error(e)


def return_cookies():
    try:
        if 'cookies.json' in os.listdir():
            with open('cookies.json', mode='r', encoding='UTF-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(e)


def get_ntp():
    try:
        ntp = ntplib.NTPClient()
        response = ntp.request("ntp5.aliyun.com")
        return response.tx_time
    except Exception as e:
        logger.error(e)


def get_time_differ():
    local_time = time.time()
    return get_ntp() - local_time  # 大于0则慢了 小于0则快了


def time_convert(str_time):
    try:
        dt_obj = datetime.strptime(str_time, '%Y%m%d %H%M%S')
        timestamp = int(time.mktime(dt_obj.timetuple()))  # 将输入的时间转换为时间戳
        return timestamp
    except ValueError as e:
        logger.error(e)
        logger.info("请按照格式正确输入！")
    except Exception as e:
        logger.error(e)


def get_ticket_info():
    try:
        ticket_num = input("请输入要买的活动id（网页最后面的一串数字）：")
        cookies = return_cookies()
        get_url = f"https://www.allcpp.cn/allcpp/ticket/getTicketTypeList.do?eventMainId={ticket_num}"
        ticket = requests.get(get_url, headers=headers, cookies=cookies)
        logger.info(f"抓取票数据，返回值{ticket}，返回内容{ticket.text}")
        time.sleep(0.02)
        ticket_json = ticket.json()
        main_name = ticket_json["ticketMain"]["eventName"]
        main_id = ticket_json["ticketMain"]["eventMainId"]
        print(f"读取活动门票，活动名称《{main_name}》，活动ID：{main_id}")
        if ticket_json["ticketTypeList"]:
            print("获取到以下票种：")
            for i in range(0, len(ticket_json["ticketTypeList"])):
                ticket_name = ticket_json["ticketTypeList"][i]["ticketName"]
                ticket_price = ticket_json["ticketTypeList"][i]["ticketPrice"] / 100
                print(f"{i} | 门票类型：{ticket_name}  门票价格：{ticket_price}￥")
            while True:
                num = input("请输入要购买的票种序号：")
                try:
                    if int(num) < 0 or int(num) >= len(ticket_json["ticketTypeList"]):
                        logger.error("输入内容不合法！")
                    else:
                        global ticket_id
                        logger.info(f"选定的门票为：{ticket_json["ticketTypeList"][int(num)]}")
                        ticket_id = ticket_json["ticketTypeList"][int(num)]["id"]
                        break
                except ValueError as e:
                    logger.error(e)
                except Exception as e:
                    logger.error(e)
        else:
            logger.error("该活动没有票信息！")
    except Exception as e:
        logger.error(f"解析错误！！！{e}")


def check_ticket(order):
    cookies = return_cookies()
    get_url = "https://www.allcpp.cn/api/tk/getList.do?type=0&sort=0&index=1&size=10"
    ticket_json = requests.get(get_url, headers=headers, cookies=cookies)
    logger.info(f"查询票单待付款内容，返回值{ticket_json}， 返回内容{ticket_json.text}")
    for item in ticket_json.json()['result']['data']:
        if str(item['id']) == order:
            return True


def buyer_list():
    buyer_id = ""
    url = "https://www.allcpp.cn/allcpp/user/purchaser/getList.do"
    cookies = return_cookies()
    buyer = requests.get(url, headers=headers, cookies=cookies)
    logger.info(f"抓取购票人信息，返回值{buyer}，返回内容{buyer.text}")
    time.sleep(0.03)
    print("获取到以下购票人：")
    for i in range(0, len(buyer.json())):
        real_name = buyer.json()[i]["realname"]
        id_card = buyer.json()[i]["idcard"]
        tel = buyer.json()[i]["mobile"]
        print(f"{i} | 姓名：{real_name}  身份证号：{id_card}  手机号：{tel}")
    while True:
        num = input("请输入购票人序号（多个用英文逗号分割）：")
        if num is None:
            logger.warning("你还没填写购票人呢！！！")
        else:
            try:
                for item in num.split(","):
                    buyer_id += f"{buyer.json()[int(item)]["id"]},"
                return buyer_id[:-1]
            except ValueError as e:
                logger.error(e)


def countdown(buyer_id, count):
    while True:
        s_time = input("[定时器]请输入日期和时间（格式：20240813 120000）[不填写为直接开始]：")
        if s_time:
            set_time = time_convert(s_time)  # 将设定时间转换为时间戳
            if set_time:
                remainder = set_time - time.time()
                logger.info("设定时间戳%.2f，还剩%.2fs开始抢票" % (set_time, remainder))
                df_time = get_time_differ()
                if df_time > 0:
                    logger.warning("系统时间比ntp服务器时间慢了%.2fms，已自动修正时间差！" % (df_time * 1000))
                else:
                    logger.warning("系统时间比ntp服务器时间快了%.2fms，已自动修正时间差！" % (df_time * 1000))
                while set_time:
                    if set_time - time.time() > 5:
                        time.sleep(1)
                    else:
                        differ_time = set_time - df_time - time.time()
                        end_time = time.perf_counter() + differ_time
                        current_time = time.perf_counter()
                        while current_time < end_time:
                            current_time = time.perf_counter()
                        break
                break
        else:
            logger.info("跳过定时，直接开始！")
            break
    while True:
        if buy(buyer_id, count):
            input("抢票结束，输入任意键退出程序：")
            break
        time.sleep(0.4)  # 抢票间隔，单位为秒，不建议设置为太低


def buy(buyer_id, count):
    try:
        buy_url = "https://www.allcpp.cn/allcpp/ticket/buyTicketWeixin.do"
        cookies = return_cookies()
        n = string.ascii_letters + string.digits
        nonce = ''.join(secrets.choice(n) for i in range(32))
        timestamp = int(time.time())
        sign = hashlib.md5(f"2x052A0A1u222{timestamp}{nonce}{ticket_id}2sFRs".encode('utf-8')).hexdigest()
        payload = f"ticketTypeId={ticket_id}&count={count}&nonce={nonce}&timeStamp={timestamp}&sign={sign}&payType=0&&purchaserIds={buyer_id}"

        buy_ticket = requests.post(buy_url, headers=headers, cookies=cookies, data=payload)
        logger.info(f"返回值{buy_ticket}, 返回内容{buy_ticket.text}")
        ret = buy_ticket.json()

        if ret['isSuccess']:
            order = ret['result']['orderid']
            logger.info(f"抢票成功！票号{order}")
            if check_ticket(order):
                logger.info("门票验证成功！请立即前往CPP票单-待付款中付款！！！")
                return True
    except requests.exceptions.JSONDecodeError as e:
        logger.error(e)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    if 'cookies.json' not in os.listdir():
        logger.warning("Cookies文件不存在！请登录CPP账户！")
        time.sleep(0.02)
        get_cookies()
    get_ticket_info()
    if ticket_id:
        buyer_re = buyer_list()
        logger.info(f"选择的购票人id为：{buyer_re}")
        time.sleep(0.03)
        countdown(buyer_re, len(buyer_re.split(",")))
    else:
        logger.error("票ID不存在，请重启软件！")
