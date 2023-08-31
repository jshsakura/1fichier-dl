import requests
import socks
import os
import time
import lxml.html
import logging
import PyQt5.sip
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QProgressBar
from .helpers import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def wait_for_password(worker, password=''):
    status = '잘못된 비밀번호' if password else '비밀번호 입력 대기 중'
    while True:
        if not PyQt5.sip.isdeleted(worker.data[5]):
            if worker.data[5].text() == password:
                update_data = [None, None, status]
                # 리스트 타입인 경우에만 update_signal
                if isinstance(worker.data, list):
                    worker.signals.update_signal.emit(
                        worker.data, update_data)
                time.sleep(2)
            else:
                return True
        if worker.stopped or worker.paused:
            return False


def download(worker, payload={'dl_no_ssl': 'on', 'dlinline': 'on'}, downloaded_size=0):
    downloading = True
    url = worker.link
    i = 1

    headers_opt = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Referer': url,
    }

    if worker.dl_name:
        try:
            downloaded_size = os.path.getsize(
                worker.dl_directory + '/' + worker.dl_name)
            logging.debug(
                f'Previous file found. Downloaded size: {downloaded_size}')
        except FileNotFoundError:
            downloaded_size = 0
            logging.debug('Previous file not found.')

    while downloading:
        p = None
        if worker.stopped or worker.paused:
            return None if not worker.dl_name else worker.dl_name
        if not wait_for_password(worker):
            return
        if (isinstance(worker.data, list)):
            update_data = [None, None, '로컬 IP']
            worker.signals.update_signal.emit(worker.data, update_data)

        if worker.proxies:
            logging.debug('Popping proxy Count: ' +
                          str(len(worker.proxies) if worker.proxies else 0))
            p = worker.proxies.pop()
        else:
            logging.debug('Getting proxy.')
            worker.proxies = get_proxies(worker.proxy_settings)
        try:
            if not p:
                p = worker.proxies.pop()
            proxy_ip = str(p['https']).replace(
                'http://', '').replace('https://', '') if isinstance(p['https'], str) else ''
            if (isinstance(worker.data, list)):
                update_data = [
                    None, None, f'우회 시도 ({i}) ' + proxy_ip]
                if isinstance(worker.data, list):
                    worker.signals.update_signal.emit(
                        worker.data, update_data)

            r = requests.post(url, payload, headers=headers_opt,
                              proxies=p, timeout=worker.timeout, verify=False)
            html = lxml.html.fromstring(r.content)
            if html.xpath('//*[@id="pass"]'):
                payload['pass'] = worker.data[5].text()
                r = requests.post(url, payload, proxies=p,
                                  timeout=worker.timeout, verify=False)
        except:
            logging.debug('Proxy failed. proxies:'+str(p))
            i += 1
            continue
        else:
            logging.debug('Proxy worked.')
            if worker.stopped or worker.paused:
                return None if not worker.dl_name else worker.dl_name

            if (isinstance(worker.data, list)):
                update_data = [None, None, '우회 성공']
                worker.signals.update_signal.emit(
                    worker.data, update_data)

        if not html.xpath('/html/body/div[4]/div[2]/a'):
            logging.debug('Failed to parse direct link.')
            if '잘못된 비밀번호' in r.text:
                if not wait_for_password(worker, payload['pass']):
                    return
        else:
            logging.debug('Parsed direct link.')
            old_url = url
            urlx = html.xpath('/html/body/div[4]/div[2]/a')[0].get('href')
            logging.debug('Parsed urlx Check: '+str(urlx))
            headers_opt['Referer'] = old_url
            headers_opt['Range'] = f'bytes={downloaded_size}-'

            rx = requests.get(urlx, stream=True, headers=headers_opt,
                              proxies=p, verify=False)

            if 'Content-Disposition' in rx.headers:
                logging.debug('Starting download.')
                name = rx.headers['Content-Disposition'].split('"')[1]

                if worker.dl_name:
                    name = worker.dl_name
                elif os.path.exists(f'{worker.dl_directory}/{name}'):
                    i = 1
                    while os.path.exists(f'{worker.dl_directory}/({i}) {name}'):
                        i += 1
                    name = f'({i}) {name}'

                name = f'{name}.unfinished' if name[-11:] != '.unfinished' else name
                worker.dl_name = name

                if worker.stopped or worker.paused:
                    return name
                # 비동기시 업데이트 꼬임 방지
                if (isinstance(worker.data, list)):
                    update_data = [
                        name[:-11], convert_size(float(rx.headers['Content-Length'])+downloaded_size)]
                    worker.signals.update_signal.emit(
                        worker.data, update_data)

                with open(worker.dl_directory + '/' + name, 'ab') as f:
                    if (isinstance(worker.data, list)):
                        update_data = [None, None, '다운로드 중']
                        if isinstance(worker.data, list):
                            worker.signals.update_signal.emit(
                                worker.data, update_data)
                    chunk_size = 8192
                    bytes_read = 0
                    start = time.time()
                    for chunk in rx.iter_content(chunk_size):
                        f.write(chunk)
                        bytes_read += len(chunk)
                        total_per = 100 * (float(bytes_read) + downloaded_size)
                        total_per /= float(rx.headers['Content-Length']
                                           ) + downloaded_size
                        dl_speed = download_speed(bytes_read, start)
                        if worker.stopped or worker.paused:
                            return name
                        if (isinstance(worker.data, list)):
                            update_data = [None, None, '다운로드 중',
                                           dl_speed, round(total_per, 1)]
                            worker.signals.update_signal.emit(
                                worker.data, update_data)
                os.rename(worker.dl_directory + '/' + name,
                          worker.dl_directory + '/' + name[:-11])

                update_data = [None, None, '완료']
                if isinstance(worker.data, list):
                    worker.signals.update_signal.emit(
                        worker.data, update_data)
                downloading = False
            else:
                logging.debug(
                    'No Content-Disposition header. Restarting download.')
    return


def get_next_proxy(worker):
    if worker.proxies:
        proxy = worker.proxies.pop()
        logging.debug('Popping proxy get_next_proxy.')
    else:
        proxy = get_proxies(worker.proxy_settings)
        logging.debug('Getting proxy.')
    return proxy


def send_request_with_retry(url, headers=None, proxy=None, timeout=30, stream=False, max_retries=1):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(
                url, headers=headers, proxies=proxy, timeout=timeout, stream=stream, verify=False)
            response.raise_for_status()  # Check for any HTTP error
            return response
        except requests.RequestException as e:
            logging.debug(f'Failed request: {e}')
            retries += 1
    return None


def finalize_download(worker, name):
    old_path = os.path.join(worker.dl_directory, name)
    new_path = os.path.join(worker.dl_directory, name[:-11])

    os.rename(old_path, new_path)

    update_data = [None, None, '완료']
    if isinstance(worker.data, list):
        worker.signals.update_signal.emit(worker.data, update_data)


def process_parsed_link(worker, url, headers_opt, downloaded_size, html):
    old_url = url
    urlx = html.xpath('/html/body/div[4]/div[2]/a')[0].get('href')
    headers_opt['Referer'] = old_url
    headers_opt['Range'] = f'bytes={downloaded_size}-'

    proxy = get_next_proxy(worker)
    rx = send_request_with_retry(
        urlx, headers=headers_opt, proxy=proxy, timeout=worker.timeout, stream=True)

    if 'Content-Disposition' in rx.headers:
        name = extract_file_name(rx.headers['Content-Disposition'])
        name = process_file_name(worker, name)

        if not name:
            return

        if worker.stopped or worker.paused:
            return name

        worker.dl_name = name
        handle_download_process(worker, rx, downloaded_size)
    else:
        logging.debug('No Content-Disposition header. Restarting download.')


def extract_file_name(content_disposition):
    return content_disposition.split('"')[1]


def process_file_name(worker, name):
    if worker.dl_name:
        name = worker.dl_name
    elif os.path.exists(f'{worker.dl_directory}/{name}'):
        i = 1
        while os.path.exists(f'{worker.dl_directory}/({i}) {name}'):
            i += 1
        name = f'({i}) {name}'

    name = f'{name}.unfinished' if name[-11:] != '.unfinished' else name
    return name


def handle_download_process(worker, rx, downloaded_size):
    name = worker.dl_name

    if worker.stopped or worker.paused:
        return name

    update_data = [None, None, '다운로드 중']
    worker.signals.update_signal.emit(worker.data, update_data)

    chunk_size = 8192
    bytes_read = 0
    start = time.time()

    with open(worker.dl_directory + '/' + name, 'ab') as f:
        for chunk in rx.iter_content(chunk_size):
            f.write(chunk)
            bytes_read += len(chunk)
            total_per = calculate_download_percentage(
                bytes_read, downloaded_size, rx.headers['Content-Length'])
            dl_speed = calculate_download_speed(bytes_read, start)
            update_data = [None, None, '다운로드 중', dl_speed, round(total_per, 1)]
            worker.signals.update_signal.emit(worker.data, update_data)

    finalize_download(worker, name)


def calculate_download_percentage(bytes_read, downloaded_size, content_length):
    total_per = 100 * (float(bytes_read) + downloaded_size)
    total_per /= float(content_length) + downloaded_size
    return total_per


def calculate_download_speed(bytes_read, start):
    elapsed_time = time.time() - start
    dl_speed = bytes_read / (1024 * elapsed_time)
    return f'{dl_speed:.2f} KB/s'
