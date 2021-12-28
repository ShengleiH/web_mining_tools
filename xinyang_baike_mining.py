from bs4 import BeautifulSoup
import requests
from bs4.element import NavigableString
import re
from collections import Counter
import os
from tqdm import tqdm
father_path = os.path.abspath(os.path.dirname(os.getcwd()))
import sys
sys.path.append(father_path)
import time
import pandas as pd
import numpy as np


def generate_seed_url():
    seed_url_pattern_dict = {
        "item": [f"https://www.soyoung.com/itemk/ts{i}" for i in range(1, 1237 + 1, 1)],
        "drug_brand": [f"https://www.soyoung.com/itemk/drug/pp{i}" for i in range(1, 47 + 1, 1)],
        "drug": [f"https://www.soyoung.com/itemk/drug/yp{i}" for i in range(1, 1399 + 1, 1)],
        "device": [f"https://www.soyoung.com/itemk/instrument/yq{i}" for i in range(1, 1412 + 1, 1)],
        "material": [f"https://www.soyoung.com/itemk/material/cl{i}" for i in range(1, 1412 + 1, 1)]
    }
    return seed_url_pattern_dict


def baike_from_xinyang():
    seed_url_pattern_dict = generate_seed_url()
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    f_failed_out = open("data/failed_list.txt", "w", encoding="utf-8")
    out_dir = "data/yimei"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for k, v_list in seed_url_pattern_dict.items():
        for url in tqdm(v_list):
            f_out_path = os.path.join(out_dir, url.split('/')[-1] + ".html")
            try:
                html = requests.get(url, headers=headers, timeout=20).text
            except:
                f_failed_out.writelines(url + '\n')
                continue
            with open(f_out_path, 'w', encoding='utf-8') as fout:
                fout.write(html)
            time.sleep(2)


def parsing_item_html(data_dir, out_path):
    seed_url_pattern_dict = generate_seed_url()
    item_urls = seed_url_pattern_dict["item"]

    processed_results = []
    for url in tqdm(item_urls):
        file_path = os.path.join(data_dir, url.split('/')[-1]) + ".html"
        if not os.path.exists(file_path):
            processed_results.append([url])
            continue
        lines = open(file_path, 'r', encoding='utf-8').readlines()
        soup = BeautifulSoup(''.join(lines), "html.parser")
        box_info = soup.findAll(name="div", attrs={"class": "box info"})
        box_info = box_info[0] if len(box_info) == 1 else None
        if box_info is None:
            processed_results.append([url])
            continue

        # 1. 项目名，别称，简介
        try:
            introduction = box_info.findAll(name="div", attrs={"class": "item-pannel introduce"})[0]
            item_name = introduction.findAll(name="h1", attrs={"class": "name v-bl"})[0].text.strip()
        except:
            # 不允许连项目名都没有
            processed_results.append([url])
            continue

        try:
            item_aliases = introduction.findAll(name="span", attrs={"class": "alias"})[0].text.strip().replace("别名：", "").split("、")
        except:
            item_aliases = []

        try:
            item_desc = introduction.findAll(name="p", attrs={"class": "desc"})[0].text.strip()
        except:
            item_desc = ""

        # 2. 项目概览
        try:
            summary_box = box_info.findAll(name="section", attrs={"class": "fixed-list", "id": "summary"})[0]
            effects_div = summary_box.findAll(name="div", attrs={"class": "labels"})[0]
            effects = [s.text.strip() for s in effects_div.findAll(name="span", attrs={"class": "label"})]
        except:
            effects = []

        try:
            indication_div = box_info.findAll(name="section", attrs={"id": "indications"})[0]
            people_features_div = indication_div.findAll(name="div", attrs={"class": "labels"})[0]
            people_features = [s.text.strip() for s in people_features_div.findAll(name="span", attrs={"class": "label"})]
        except:
            people_features = []

        # 3. 适合人群
        try:
            crowd_div = box_info.findAll(name="section", attrs={"class": "fixed-list", "id": "crowd"})[0]
            crowd = [s.replace("；", "").strip() for s in crowd_div.findAll(name="p", attrs={"class": "p1"})[0].text.strip().split("\n")]
        except:
            crowd = []

        # 4. 项目优点
        try:
            merit_div = box_info.findAll(name="section", attrs={"class": "fixed-list", "id": "merit"})[0]
            merit = [s.replace("；", "").strip() for s in merit_div.findAll(name="p", attrs={"class": "p1"})[0].text.strip().split("\n")]
        except:
            merit = []

        # 5. 项目优点
        try:
            defect_div = box_info.findAll(name="section", attrs={"class": "fixed-list", "id": "defect"})[0]
            defect = [s.replace("；", "").strip() for s in defect_div.findAll(name="p", attrs={"class": "p1"})[0].text.strip().split("\n")]
        except:
            defect = []

        # 6. 禁忌人群
        try:
            limit_crowd_div = box_info.findAll(name="section", attrs={"class": "fixed-list", "id": "limit_crowd"})[0]
            limit_crowd = [s.replace("；", "").strip() for s in limit_crowd_div.findAll(name="p", attrs={"class": "p1"})[0].text.strip().split("\n")]
        except:
            limit_crowd = []

        processed_results.append(
            [
                url, item_name, ','.join(item_aliases), item_desc,
                ",".join(effects), ','.join(people_features),
                ",".join(crowd), ','.join(merit),
                ",".join(defect), ','.join(limit_crowd)
            ]
        )

    max_len = max([len(ls) for ls in processed_results])
    processed_results = [ls + [""] * (max_len - len(ls)) for ls in processed_results]
    processed_results_df = pd.DataFrame(processed_results,
                                        columns=['链接', '项目名', '别名', '简介', '功效', '适用人群特征',
                                                 '适用人群', '项目优点', '项目缺点', '禁忌人群'])
    processed_results_df.to_excel(out_path, index=False)


if __name__ == '__main__':
    # baike_from_xinyang()
    parsing_item_html("data/yimei", "data/yimei_processed/item.xlsx")