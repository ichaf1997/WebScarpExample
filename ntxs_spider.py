import requests
import traceback
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup 

# 逆天邪神小说爬虫示例

def download(metedata):
    req = requests.get(url=metedata.get('url'), timeout=15)
    req.encoding = 'utf-8'
    text_str = req.text
    bs = BeautifulSoup(markup=text_str, features='lxml')
    texts = bs.find('div', id='content')
    content = ''.join(texts.text.strip().split('\xa0'*4))
    os.makedirs(os.path.dirname(metedata.get('path')), exist_ok=True)
    for n in range(1, 4):
        try:
            with open(file=metedata.get('path'), encoding='utf-8', mode='w') as f:
                f.write(content)
                print(f"{datetime.now()} - {metedata.get('path').split('/')[-1]} download successfully.")
                break
        except:
            print(f"{traceback.format_exc()} \n {metedata.get('path').split('/')[-1]} download failed... retry({4-n})...")
            time.sleep(3)

if __name__ == '__main__':

    chapter_url = 'https://www.vbiquge.com/9_9933/'
    req = requests.get(url=chapter_url)
    req.encoding = 'utf-8'
    text_str = req.text
    bs = BeautifulSoup(markup=text_str, features='lxml')
    chapters = bs.find('div', id='list').find_all('a')
    unsupport_char = ('/', '\\', ':', '*', '?', '"', '<', '>', '|')

    metadata = []
    for chapter in chapters:
        file_name = chapter.string
        for c in file_name:
            if c in unsupport_char:
                file_name = file_name.replace(c, '') 
        file_url = chapter_url + chapter.get('href').split('/')[-1]
        file_path = os.path.join(os.path.dirname(__file__), '逆天邪神', file_name + '.txt').replace('\\','/')
        metadata.append(dict(name=file_name, url=file_url, path=file_path))

    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_url = { executor.submit(download, data): data for data in metadata }
        for future in as_completed(future_to_url):
            name = future_to_url[future].get('name')
            try:
                res = future.result()
            except Exception as exec:
                print(f'A occur display when download {name} ...')




