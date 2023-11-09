import requests
import os
import time
import lxml.html
import logging
import PyQt5.sip
import queue
from .helpers import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxy_queue = queue.Queue()


def wait_for_password(worker, password=''):
    status = '잘못된 비밀번호' if password else '비밀번호 입력 대기 중'
    while True:
        if not PyQt5.sip.isdeleted(worker.data[6]):
            if worker.data[6].text() == password:
                update_data = [None, None, status, None]
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
    i = 0

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
            update_data = [None, None, f'우회 시도 ({i})', '프록시 변경'] if i != 0 else [
                None, None, f'불러오는 중', '조회 중']
            worker.signals.update_signal.emit(worker.data, update_data)
            time.sleep(1)

        p = worker.proxies.get()

        try:
            if not p:
                p = worker.proxies.get()
            proxy_ip = str(p['https']) if isinstance(p['https'], str) else ''
            if (isinstance(worker.data, list)):
                update_data = [
                    None, None, f'우회 시도 ({i})', str(proxy_ip)] if i != 0 else [
                    None, None, f'프록시 갱신', '조회 중']
                if isinstance(worker.data, list):
                    worker.signals.update_signal.emit(
                        worker.data, update_data)

            # 다운로드 링크 획득
            r = requests.post(url, payload, headers=headers_opt,
                              proxies=p, timeout=worker.timeout, verify=False)
            time.sleep(1)
            html = lxml.html.fromstring(r.content)
            if html.xpath('//*[@id="pass"]'):
                payload['pass'] = worker.data[6].text()
                r = requests.post(url, payload, proxies=p,
                                  timeout=worker.timeout, verify=False)
        except Exception as e:
            logging.debug('Proxy failed. \n'+f'{e}')
            i += 1
            continue
        else:
            logging.debug('Proxy worked.')
            if worker.stopped or worker.paused:
                return None if not worker.dl_name else worker.dl_name

            if (isinstance(worker.data, list)):
                update_data = [None, None, '우회 성공', None]
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
                logging.debug(f'파일명: {name}')

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
                        update_data = [None, None, '다운로드 중', None]
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
                            update_data = [None, None, '다운로드 중', None,
                                           dl_speed, round(total_per, 1)]
                            worker.signals.update_signal.emit(
                                worker.data, update_data)
                os.rename(worker.dl_directory + '/' + name,
                          worker.dl_directory + '/' + name[:-11])

                update_data = [None, None, '다운로드 완료', None]
                if isinstance(worker.data, list):
                    worker.signals.update_signal.emit(
                        worker.data, update_data)
                downloading = False
            else:
                logging.debug(
                    'No Content-Disposition header. Restarting download.')
    return
