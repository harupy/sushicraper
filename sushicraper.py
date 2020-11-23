import requests
from bs4 import BeautifulSoup
import re
import shutil
import os
import multiprocessing
from itertools import repeat


"""
Each sushi scraper function takes a soup object and returns image source urls and names
"""


def download_img(img_src, img_name, save_dir):
    print('Downloading', img_src)
    try:
        r = requests.get(img_src, stream=True)
        if r.status_code == 200:
            img_path = os.path.join(save_dir, img_name)
            with open(img_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    except Exception as e:
        print('Could not download the image due to an error:', img_src)
        print(e)


def multi_download(img_srcs, img_names, save_dir):
    num_cpu = multiprocessing.cpu_count()
    with multiprocessing.Pool(num_cpu) as p:
        p.starmap(download_img, zip(img_srcs, img_names, repeat(save_dir)))


def sushibenkei(soup):
    img_srcs = [x['src'] for x in soup.select('div.sushiitem > img')]
    regex = re.compile(r'[0-9]+円')
    def parser(x): return regex.sub(
        '', x.replace('\n', '').replace('\u3000', ''))
    img_names = [x.text + '.png' for x in soup.select('div.sushiitem')]
    img_names = list(map(parser, img_names))
    return img_srcs, img_names


def oshidorizushi(soup):
    img_srcs = [x['src'] for x in soup.select('div.menu-a-item > img')]
    img_names = [x.text + '.jpg' for x in soup.select('p.menu-a-name')]
    return img_srcs, img_names


def nigiri_chojiro(soup):
    uls = soup.select('ul.menu-list')
    img_srcs = ['https:' + li.find('img')['src']
                for ul in uls for li in ul.find_all('li')]
    img_names = [li.find('dt').text for ul in uls for li in ul.find_all('li')]
    def parser(x): return x.split('／')[0].lower().replace(' ', '_') + '.jpg'
    img_names = list(map(parser, img_names))
    return img_srcs, img_names


def nigiri_no_tokubei(soup):
    img_srcs = [x['href'] for x in soup.select('a.item_link')]
    img_names = [x.text + '.jpg' for x in soup.select('dt.item_title')]
    return img_srcs, img_names


def sushi_value(soup):
    img_srcs = [x['src'] for x in soup.select('img.attachment-medium')]
    img_names = [f'{i:03d}.jpg' for i in range(len(img_srcs))]
    return img_srcs, img_names


def daiki_suisan(soup):
    regex = re.compile(r'.+grandmenu/menu.+.jpg')
    img_srcs = [x['src'] for x in soup.find_all('img', {'src': regex})]
    img_names = [x['alt'] +
                 '.jpg' for x in soup.find_all('img', {'src': regex})]
    return img_srcs, img_names


def hamazushi(soup):
    regex = re.compile(r'images/nigiri/.+.png')
    home = 'https://www.hamazushi.com/hamazushi/menu/'
    img_srcs = [home + x['data-echo']
                for x in soup.find_all('img', {'data-echo': regex})]
    img_names = [f'{i:03d}.png' for i in range(len(img_srcs))]
    return img_srcs, img_names


def kappasushi(soup):
    home = 'https://www.kappasushi.jp/master_data/img/bs_products/'
    # naive workaround
    n = 2000
    img_srcs = [home + f'{i:04d}/p{i:04d}_6.png' for i in range(n)]
    img_names = [f'{i:04d}.png' for i in range(n)]
    return img_srcs, img_names


def kurasushi(soup):
    regex = re.compile(r'.+/images_menu/.+.jpg')
    home = 'https://www.kurasushi.co.jp/menu/'
    img_srcs = [home + x['src'][2:]
                for x in soup.find_all('img', {'src': regex})]
    img_names = [x['alt'] +
                 '.jpg' for x in soup.find_all('img', {'src': regex})]
    return img_srcs, img_names


def sushiro(soup):
    regex = re.compile(r'http://cmsimage.akindo-sushiro.co.jp/menu/.+.png')
    img_srcs = [x['src'] for x in soup.find_all('img', {'src': regex})]
    img_names = [f'{i:04d}.png' for i in range(len(img_srcs))]
    return img_srcs, img_names


def main():
    img_dir = 'images'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    funcs_urls = [
        (sushibenkei, 'http://www.sushibenkei.co.jp/sushimenu/'),
        (oshidorizushi, 'http://www.echocom.co.jp/menu'),
        (nigiri_chojiro, 'https://www.chojiro.jp/menu/menu.php?pid=1'),
        (nigiri_no_tokubei, 'http://www.nigirinotokubei.com/menu/551/'),
        (sushi_value, 'https://www.sushi-value.com/menu/'),
        (daiki_suisan, 'http://www.daiki-suisan.co.jp/sushi/grandmenu/'),
        (hamazushi, 'https://www.hamazushi.com/hamazushi/menu/'),
        (kappasushi, 'https://www.kappasushi.jp/menu2'),
        (kurasushi, 'https://www.kurasushi.co.jp/menu/'),
        (sushiro, 'https://www.akindo-sushiro.co.jp/menu/'),
    ]

    for func, url in funcs_urls:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        img_srcs, img_names = func(soup)
        save_dir = os.path.join('images', func.__name__)
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        multi_download(img_srcs, img_names, save_dir)


if __name__ == '__main__':
    main()
