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
import random


def read_file(path, fillna=""):
    if ".xlsx" in path:
        raw_data = pd.read_excel(path)
        raw_data = raw_data.replace(np.nan, fillna, regex=True)
        columns = raw_data.columns.tolist()
        raw_data = raw_data.values.tolist()
    elif ".csv" in path:
        raw_data = pd.read_csv(path)
        raw_data = raw_data.replace(np.nan, fillna, regex=True)
        columns = raw_data.columns.tolist()
        raw_data = raw_data.values.tolist()
    else:
        raw_data = [line.strip("\n").split("\t") for line in open(path)]
        columns = raw_data[0]
        raw_data = raw_data[1:]
    data = []
    for ls in raw_data:
        if len(ls) != len(columns):
            print("ERROR PARSING: {}".format(ls))
            continue
        data.append(ls)
    print(f"loading {len(data)} from {path}")
    column2idx = {col: idx for idx, col in enumerate(columns)}

    assert len(column2idx) == len(data[0]), f"column2idx: {column2idx}, data[0]: {data[0]}"

    return data, column2idx, columns


def save_file(data, path, columns):
    if ".xlsx" in path:
        data_df = pd.DataFrame(np.asarray(data), columns=columns)
        data_df.to_excel(path, index=False)
    else:
        with open(path, 'w', encoding='utf-8') as fout:
            if columns is not None:
                fout.write("{}\n".format("\t".join(list(map(str, columns)))))
            for item in data:
                if isinstance(item, list):
                    fout.write("{}\n".format("\t".join(list(map(str, item)))))
                else:
                    fout.write('{}\n'.format(str(item)))
    print("Finish saving {} data to file {}".format(len(data), path))


proxy_list = set()
def update_ip_list():
    urlip = 'http://proxy.httpdaili.com/apinew.asp?sl=20&noinfo=true&text=1&ddbh=2287705608927186447'
    ip_list = [ip for ip in requests.get(urlip).text.split('\r\n')]
    proxy_list.clear()
    for ip in ip_list:
        if len(ip.strip()) > 0:
            # proxy_list.add('http://' + ip)
            proxy_list.add(ip)

def get_random_ip():
    proxy_ip = random.choice(list(proxy_list))
    proxies = {'https': proxy_ip}
    return proxies


def synonym_from_baidu(query):
    url = f'https://www.baidu.com/s?wd={query}%20剧本杀'
    # headers = {
    #     "Accept-Language": "zh-CN,zh;q=0.9",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    # }
    # html = requests.get(url, headers=headers, timeout=20).text
    html = requests.get(url, proxies=get_random_ip(), timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    contents = soup.find_all(id='content_left')[0].contents
    max_baidu_cnt = 3
    attr_pattern = re.compile(r'[（【『「《](.*?)[）】』」》]')

    collected_h3 = []
    for idx, cont in enumerate(contents):
        if isinstance(cont, NavigableString):
            continue
        # div_contents = cont.contents
        div_contents = soup.findAll(name="h3", attrs={"class": "t"})
        stoped = False
        for div in div_contents:
            if isinstance(div, NavigableString):
                continue

            if len(collected_h3) > max_baidu_cnt:
                stoped = True
                break
            collected_h3.append(div.text)
        if stoped:
            break
    # print(collected_h3)
    matched_names = []
    for h3 in collected_h3:
        if '剧本杀' not in h3:
            continue
        h3_name = re.findall(attr_pattern, h3)
        if len(h3_name) > 0:
            matched_names.extend(h3_name)
    # print(collected_h3, matched_names)
    matched_name = ''
    if len(matched_names) > 0:
        matched_name = Counter(matched_names).most_common()[0][0]
    return matched_name


def run_baidu_synonym_mining(input_path, output_path):
    data = read_file(input_path)[0]
    # matched_results = []
    fout = open(output_path, 'w', encoding='utf-8')
    fout.writelines('\t'.join(['jbs_ori_name', 'jbs_matched_name', 'is_equal_name', 'in_standard_corpus']) + '\n')
    fout.flush()

    for name, _, label in tqdm(data):
        if len(proxy_list) == 0:
            update_ip_list()
        try:
            matched_name = synonym_from_baidu(name)
        except:
            matched_name = 'ERROR'
            update_ip_list()
        is_equal = int(name == matched_name)
        # matched_results.append([name, matched_name, is_equal, label])
        fout.writelines('\t'.join([str(name), str(matched_name), str(is_equal), str(label)]) + '\n')
        fout.flush()
        time.sleep(2)

    # save_file(matched_results, output_path, columns=['jbs_ori_name', 'jbs_matched_name', 'is_equal_name', 'in_standard_corpus'])


if __name__ == '__main__':
    run_baidu_synonym_mining(
        "data/jbs/jbs_names_cleaned.txt",
        "data/jbs/jbs_synonym_names.txt"
    )
