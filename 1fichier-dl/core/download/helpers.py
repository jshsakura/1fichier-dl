import logging
import requests
import math
import os
import time
import lxml.html
import urllib3
# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIRST_RUN = True
PROXY_TXT_API = 'https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/https_proxy_list.txt'
PLATFORM = os.name


def get_proxies(settings: str) -> list:
    '''
    Get proxies (str) from API.
    '''
    global FIRST_RUN

    if FIRST_RUN:
        FIRST_RUN = False
        return [None]

    r_proxies = []

    '''
    Proxy 설정이 있는 경우 기본 프록시 세팅은 무시하고 진행
    '''
    if settings:
        r_proxies = requests.get(settings).text.splitlines()
    else:
        '''
        배열 형태의 proxy 서버 목록
        '''
        proxy_arr_list = requests.get(PROXY_TXT_API).text.splitlines()
        for p in proxy_arr_list:
            proxy_list = requests.get(p).text.splitlines()
            # 프록시 서버의 중복 제거
            unique_proxy_list = list(set(proxy_list))
            for item in unique_proxy_list:
                r_proxies.append(item)

    proxies = []
    for p in r_proxies:
        # Require SSL error avoidance to bypass proxy
        proxy_item = p
        if not 'http' in proxy_item[0:4]:
            proxy_item = f'http://{proxy_item}'
        proxies.append({'https': proxy_item} if PLATFORM ==
                       'nt' else {'https': f'{proxy_item.replace("http","https")}'})
    return proxies


def convert_size(size_bytes: int) -> str:
    '''
    Convert from bytes to human readable sizes (str).
    '''
    # https://stackoverflow.com/a/14822210
    if size_bytes == 0:
        return '0 B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def download_speed(bytes_read: int, start_time: float) -> str:
    '''
    Convert speed to human readable speed (str).
    '''
    if bytes_read == 0:
        return '0 B/s'
    elif time.time()-start_time == 0:
        return '- B/s'
    size_name = ('B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s')
    bps = bytes_read/(time.time()-start_time)
    i = int(math.floor(math.log(bps, 1024)))
    p = math.pow(1024, i)
    s = round(bps / p, 2)
    return '%s %s' % (s, size_name[i])


def get_link_info(url: str) -> list:
    '''
    Get file name and size. 
    '''
    try:
        r = requests.get(url)
        html = lxml.html.fromstring(r.content)
        if html.xpath('//*[@id="pass"]'):
            return ['Private File', '- MB']
        name = html.xpath('//td[@class=\'normal\']')[0].text
        size = html.xpath('//td[@class=\'normal\']')[2].text
        return [name, size]
    except:
        return None


def is_valid_link(url: str) -> bool:
    '''
    Returns True if `url` is a valid 1fichier domain, else it returns False
    '''
    domains = [
        '1fichier.com/',
        'afterupload.com/',
        'cjoint.net/',
        'desfichiers.com/',
        'megadl.fr/',
        'mesfichiers.org/',
        'piecejointe.net/',
        'pjointe.com/',
        'tenvoi.com/',
        'dl4free.com/',
        'ouo.io/'
    ]

    return any([x in url.lower() for x in domains])
