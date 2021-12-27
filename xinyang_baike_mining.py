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


if __name__ == '__main__':
    baike_from_xinyang()
