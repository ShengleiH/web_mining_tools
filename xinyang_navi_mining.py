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
        "item": "https://www.soyoung.com/itemk/index",
        "drug": "https://www.soyoung.com/itemk/drug",
        "device": "https://www.soyoung.com/itemk/instrument",
        "material": "https://www.soyoung.com/itemk/material"
    }
    return seed_url_pattern_dict


def navi_from_xinyang():
    seed_url_pattern_dict = generate_seed_url()
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }

    out_dir = "data/yimei_navi_test"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for k, url in seed_url_pattern_dict.items():
        f_out_path = os.path.join(out_dir, url.split('/')[-1] + ".html")
        try:
            html = requests.get(url, headers=headers, timeout=20).text
        except:
            continue
        with open(f_out_path, 'w', encoding='utf-8') as fout:
            fout.write(html)
        time.sleep(2)


def parse_item_html(path, out_path):
    lines = open(path, 'r', encoding='utf-8').readlines()
    soup = BeautifulSoup(''.join(lines), "html.parser")

    big_navi_blocks = soup.findAll(name="div", attrs={"class": "con-1180 item-block"})
    processed_results = []
    for big_navi_block in tqdm(big_navi_blocks):
        level_1_navi_name = big_navi_block.findAll(name="div", attrs={"class": "tab-title"})[0].text.strip()

        level_2_navi_blocks = big_navi_block.findAll(name="a", attrs={"class": "second-item"})
        level_2_navi_names = [b.text.strip() for b in level_2_navi_blocks]

        product_boxes = big_navi_block.findAll(name="div", attrs={"class": "product-box"})
        # print(product_boxes)
        processed_product_boxes = []
        for product_box in product_boxes:
            processed_products = []
            products = product_box.findAll(name="div", attrs={"class": "product"})
            # print("products cnt:", len(products))
            for product in products:
                prod_url = product.attrs["data-url"]
                product_title = product.findAll(name="div", attrs={"class": "product-title"})[0].text.strip().split("\n")[0].strip()
                product_des = product.findAll(name="p", attrs={"class": "product-des"})[0].text.strip()
                processed_products.append(
                    {
                        "prod_url": "https:" + prod_url,
                        "product_title": product_title,
                        "product_des": product_des
                    }
                )
            processed_product_boxes.append(processed_products)

        assert len(level_2_navi_names) == len(processed_product_boxes), \
            f"navigator is not equal to product_boxes: {len(level_2_navi_names)} != {len(processed_product_boxes)}"

        for level_2_navi_name, processed_products in zip(level_2_navi_names, processed_product_boxes):
            for processed_product in processed_products:
                processed_results.append(
                    [
                        level_1_navi_name, level_2_navi_name,
                        processed_product["product_title"], processed_product["prod_url"],
                        processed_product["product_des"]
                    ]
                )

    processed_results_df = pd.DataFrame(processed_results, columns=['level1', 'level2', 'product_title', 'prod_url', 'product_des'])
    processed_results_df.to_excel(out_path, index=False)


def parse_other_html(path, out_path):
    lines = open(path, 'r', encoding='utf-8').readlines()
    soup = BeautifulSoup(''.join(lines), "html.parser")

    big_navi_blocks = soup.findAll(name="div", attrs={"class": "con-1180 product-box"})
    processed_results = []
    for big_navi_block in tqdm(big_navi_blocks):
        level_1_navi_name = big_navi_block.findAll(name="div", attrs={"class": "box-title"})[0].text.strip()

        products = big_navi_block.findAll(name="div", attrs={"class": "product"})
        # print("products cnt:", len(products))
        for product in products:
            prod_url = "https://www.soyoung.com" + product.attrs["data-url"]
            product_title = product.findAll(name="div", attrs={"class": "product-title"})[0].text.strip().split("\n")[0].strip()
            product_des = product.findAll(name="p", attrs={"class": "product-des"})[0].text.strip()
            processed_results.append(
                [
                    level_1_navi_name,
                    product_title, prod_url, product_des
                ]
            )

    processed_results_df = pd.DataFrame(processed_results, columns=['level1', 'product_title', 'prod_url', 'product_des'])
    processed_results_df.to_excel(out_path, index=False)


if __name__ == '__main__':
    # navi_from_xinyang()
    # parse_item_html("data/yimei_navi/index.html", "data/yimei_navi_processed/item.xlsx")
    # parse_other_html("data/yimei_navi/drug.html", "data/yimei_navi_processed/drug.xlsx")
    parse_other_html("data/yimei_navi/instrument.html", "data/yimei_navi_processed/instrument.xlsx")
    # parse_other_html("data/yimei_navi/material.html", "data/yimei_navi_processed/material.xlsx")