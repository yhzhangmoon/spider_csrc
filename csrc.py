#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : csrc.py
# @Author: zhangyueheng
# @Date  : 2017/11/29 0029
# @Desc  : 
# @Contact : yhzhang.moon@126.com

import requests
from bs4 import BeautifulSoup
import re
import datetime
from time import sleep

items = []

def analyze_2th_web(url):
    session = requests.Session()
    f = ""
    try:
        f = session.get(url=url)
    except Exception as e:
        print(e)
    data = f.content.decode()
    return data

def branch_1th(data, tmp):

    soup = BeautifulSoup(data, "lxml")

    try:
        custom = soup.find("div", class_="Custom_UnionStyle")
        ps = custom.find_all("p")
        company = ps[0].find("span").get_text()[:-1]
        money_tmp = ps[2].get_text()
        money = re.search(r'[0-9]+[\.,0-9]*', money_tmp).group()

        tmp["company"] = company
        tmp["money"] = money

        return tmp

    except Exception as e:
        tmp["remark"] = url
        return tmp

def branch_2th(data, tmp):

    soup = BeautifulSoup(data, "lxml")

    try:
        ps = soup.find_all("p", class_="Custom_UnionStyle")
        company = ps[0].find("span").get_text()[:-1]
        money_tmp = ps[2].get_text()
        money = re.search(r'[0-9]+[\.,0-9]*', money_tmp).group()

        tmp["company"] = company
        tmp["money"] = money

        return tmp

    except Exception as e:
        tmp["remark"] = url
        return tmp


def analyze_2th_content(url, data):
    tmp = {}
    tmp["company"] = ""
    tmp["money"] = ""

    soup = BeautifulSoup(data, "lxml")
    title = soup.find("head").find("title").get_text()
    tmp["title"] = title

    isBranch_1th = soup.find("div", class_="Custom_UnionStyle")
    if isBranch_1th is not None:
        return branch_1th(data, tmp)

    isBranch_2th = soup.find("p", class_="Custom_UnionStyle")
    if isBranch_2th is not None:
        return branch_2th(data, tmp)

    try:
        ps = soup.find_all("p", class_="p0")

        test_tmp = ps[0].find_all("span")[0].get_text()

        if "：" in test_tmp:
            company = ps[0].find_all("span")[0].get_text()[:-1]
        elif "：" in ps[1].find_all("span")[0].get_text():
            company = ps[1].find_all("span")[0].get_text()[:-1]
        else:
            company = ps[1].find_all("span")[1].get_text()[:-1]

        money_tmp = ps[2].find_all("span")[0].get_text()
        if "一、" in money_tmp:
            money = re.search(r'[0-9]+[\.,0-9]*', money_tmp).group()
        else:
            money_tmp = ps[3].find_all("span")[0].get_text()
            money = re.search(r'[0-9]+[\.,0-9]*', money_tmp).group()

        tmp["company"] = company
        tmp["money"] = money

        return tmp
    except Exception as e:
        tmp["remark"] = url
        return tmp

def analyze_1th_web(page):
    main_url = "http://www.csrc.gov.cn/wcm/govsearch/simp_gov_list.jsp"
    session = requests.Session()

    headers = {
        "Host": "www.csrc.gov.cn",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cookie": "JSESSIONID=6FFE5A720A6249DB00D51FA7CB05FB1A"
    }

    values = "SType=1&searchColumn=all&searchYear=all&preSWord=&sword=%E5%85%B3%E4%BA%8E%E6%A0%B8%E5%87%86+%E5%85%AC%E5%8F%B8%E5%80%BA%E5%88%B8&searchAgain=&page=" + page + "&res_wenzhong=&res_wenzhonglist=&wenzhong=&pubwebsite=%2Fzjhpublic%2F"
    values = values.encode("utf-8")

    f = ""
    try:
        f = session.post(url=main_url,
                         headers=headers,
                         data=values)
    except Exception as e:
        print(e)

    result = f.content.decode()

    try:
        soup = BeautifulSoup(result, "lxml")
        documentContainer = soup.find("div", id="documentContainer")
        rows = documentContainer.find_all("div", class_="row")
        if rows:
            for row in rows:
                mc = row.find("li", class_="mc").find("a")["href"]
                mc_url = "http://www.csrc.gov.cn" + mc
                print(mc_url)
                data = analyze_2th_web(mc_url)
                tmp = analyze_2th_content(mc_url, data)

                date = row.find("li", class_="fbrq").get_text()

                tmp["date"] = date

                if "remark" not in tmp and (tmp["company"] == "" or tmp["money"] == ""):
                    tmp["remark"] = mc_url

                if tmp not in items:
                    items.append(tmp)

                sleep(0.5)

    except Exception as e:
        print(e)

def main():
    analyze_1th_web(str(19))
    print(items)
    # start = datetime.datetime.now()
    # for i in range(1, 59):
    #     print(i)
    #     analyze_1th_web(str(i))
    #     sleep(3)
    #
    # for i in items:
    #     if "remark" in i:
    #         print(i["remark"])
    #
    # end = datetime.datetime.now()
    # print(end - start)

if __name__ == '__main__':
    main()