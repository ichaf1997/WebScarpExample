import requests
import os
import re
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from contextlib import closing
from concurrent.futures import as_completed, ThreadPoolExecutor

# 妖神记漫画爬虫

# 漫画索引页面
index_url = 'https://www.dmzj.com/info/yaoshenji.html'

def cached():
    if os.path.exists('ysj.tmp') and os.path.getsize('ysj.tmp') > 0:
        try:
            with open('ysj.tmp', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['metadata']
        except:
            return None 
    return None

def download(metadata):
    urls = metadata['img_urls']
    for url in urls:
        file_name = re.findall(r'\d{2,}',metadata['chapter_name'])[0] + '_' + os.path.basename(url)
        path = os.path.join(os.path.dirname(__file__), '妖神记', file_name).replace('\\', '/')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        for n in range(1, 4):
            try:
                with closing(requests.get(url, stream=True)) as resp:
                    content_size = int(resp.headers['content-length'])
                    if resp.status_code == 200:
                        print(f"file name: {os.path.basename(path)} file size: {content_size/1024:.2f}")
                        with open(file=path, mode='wb') as f:
                            for data in resp.iter_content(chunk_size=1024):
                                f.write(data)
                        print(f'download completed. [{url}]')
                        break                    
                    continue
            except Exception as err:
                print(err)

if __name__ == '__main__':
    if not cached():
        r = requests.get(url=index_url)
        r.encoding = 'utf-8'
        bs = BeautifulSoup(markup=r.text, features='lxml')
        chapters = bs.find('ul', class_='list_con_li').find_all('a')
        metadata = []
        for chapter in chapters:
            metadata.append(dict(chapter_name=chapter.text, chapter_url=chapter.get('href')))

        # 图片URL拼接
        pattern_one = re.compile(r'\D\d{4}\D')
        pattern_two = re.compile(r'\D\d{5}\D')
        pattern_three = re.compile(r'\d{13,14}')
        try:
            for i in range(0, len(metadata)):
                data = metadata[i]
                print(data.get('chapter_name'))
                c_url = data.get('chapter_url')
                c_resp = requests.get(c_url, timeout=30)
                c_resp.encoding = 'utf-8'
                scripts_tag = BeautifulSoup(markup=c_resp.text, features='lxml').script
                part_one = re.search(pattern_one, str(scripts_tag)).group(0).strip('|')
                part_two = re.search(pattern_two, str(scripts_tag)).group(0).strip('|')
                imgs_index = re.findall(pattern_three, str(scripts_tag))
                imgs_index.sort()
                img_urls = [ f"https://images.dmzj1.com/img/chapterpic/{part_one}/{part_two}/{index}.jpg" for index in imgs_index ]
                data.update(img_urls=img_urls)
                print(data.get('img_urls'))
                metadata[i] = data 
            try:
                with open('ysj.tmp', 'w', encoding='utf-8') as f:
                    tmp_data = {'metadata': metadata}
                    json.dump(tmp_data, f, ensure_ascii=False)
            except:
                pass
        except:
            raise Exception('URL拼接失败！')
    else:
        metadata = cached()

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = { executor.submit(download, chapter_metadata): chapter_metadata for chapter_metadata in metadata}
        for future in as_completed(future_to_url):
            chapter_metadata = future_to_url[future]
            try:
                res = future.result()
            except Exception as exc:
                print(f"A occur happend when download {chapter_metadata['chapter_url']}")





