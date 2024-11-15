import os
import queue
import sys
import logging
import threading
from .download import *
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QStandardItem
from .helpers import is_valid_link
from .recapcha import *

# Create a lock to synchronize access to the proxy list
proxy_queue = queue.Queue()


class WorkerSignals(QObject):
    download_signal = pyqtSignal(list, str, bool, str, int)
    alert_signal = pyqtSignal(str)
    update_signal = pyqtSignal(list, list)
    unpause_signal = pyqtSignal(list, str, bool, str)


class FilterWorker(QRunnable):
    def __init__(self, actions, cached_download='', password=''):
        super(FilterWorker, self).__init__()
        self.links = actions.gui.links  # QPlainTextEdit 객체여야 함
        self.gui = actions.gui
        self.cached_downloads = actions.cached_downloads
        self.cached_download = cached_download
        self.signals = WorkerSignals()
        self.dl_name = cached_download[1] if self.cached_download else None
        self.password = cached_download[2] if self.cached_download else (
            password if password else None)
        self.progress = cached_download[3] if self.cached_download else None

    @pyqtSlot()
    def run(self):
        self.valid_links = []
        self.invalid_links = []

        try:
            # self.links가 QPlainTextEdit인 경우와 문자열인 경우 모두 처리
            if isinstance(self.links, QPlainTextEdit):
                links = self.links.toPlainText().splitlines()
            elif isinstance(self.links, str):
                links = self.links.splitlines()
            else:
                logging.error("Unexpected type for self.links: " + str(type(self.links)))
                return
            
            for link in links:
                link = link.strip()
                logging.debug('Processing link: ' + str(link))

                # ouo.io 링크 우회 시도
                try:
                    if 'ouo.io' in link:
                        bypassed = ouo_bypass(url=link)
                        link = bypassed['bypassed_link']
                        logging.debug('Bypassed link: ' + str(link))
                except Exception as e:
                    logging.error(f"Failed to bypass ouo.io link {link}: {e}")
                    self.invalid_links.append(link)
                    continue

                # 링크 유효성 검사
                try:
                    if is_valid_link(link):
                        if not (link.startswith('https://') or link.startswith('http://')):
                            link = f'https://{link}'
                        link = link.split('&')[0]
                        self.valid_links.append(link)
                    else:
                        raise ValueError(f'Invalid link format: {link}')
                except ValueError as ve:
                    logging.warning(ve)
                    self.invalid_links.append(link)
                    self.signals.alert_signal.emit(f'Invalid link format: {link}')
                    continue  # 다음 링크로 계속
                   
            if len(self.invalid_links) > 0 :
                self.gui.hide_loading_overlay()
                # 링크 입력창 초기화
                self.gui.add_btn.setEnabled(True)
                self.gui.links.setEnabled(True)
                self.gui.password.setEnabled(True)
                # 링크 추가 문구 원복
                self.gui.add_links_complete()
            else :
                for link in self.valid_links:
                    try:
                        if '/dir/' in link:
                            folder = requests.get(f'{link}?json=1')
                            folder = folder.json()
                            for f in folder:
                                link = f['link']
                                info = [f['파일명'], convert_size(int(f['size']))]
                                info.extend(['대기중', None, '0 B/s', ''])
                                row = []

                                for val in info:
                                    data = QStandardItem(val)
                                    data.setFlags(data.flags() & ~Qt.ItemIsEditable)
                                    row.append(data)

                                if f['password'] == 1:
                                    password = QStandardItem(self.password)
                                    row.append(password)
                                    self.gui.hide_loading_overlay()
                                else:
                                    no_password = QStandardItem('비밀번호 없음')
                                    no_password.setFlags(data.flags() & ~Qt.ItemIsEditable)
                                    row.append(no_password)

                                self.signals.download_signal.emit(
                                    row, link, True, self.dl_name, self.progress)
                                if self.cached_download:
                                    self.cached_downloads.remove(self.cached_download)
                        else:
                            info = get_link_info(link)
                            if info is not None:
                                # parsing 에러는 회피
                                if info[0] == 'Error':
                                    self.signals.alert_signal.emit(f'다운로드를 하기 위한 파일의 실제 정보를 가져올 수 없었습니다.\n{link}')
                                    self.gui.hide_loading_overlay()
                                else:
                                    is_private = True if info[0] == 'Private File' else False
                                    info[0] = self.dl_name if self.dl_name else info[0]
                                    info.extend(['대기중', None, '0 B/s', ''])
                                    row = []

                                    for val in info:
                                        data = QStandardItem(val)
                                        data.setFlags(data.flags() & ~Qt.ItemIsEditable)
                                        row.append(data)

                                    if is_private:
                                        password = QStandardItem(self.password)
                                        row.append(password)
                                        self.gui.hide_loading_overlay()
                                    else:
                                        no_password = QStandardItem('비밀번호 없음')
                                        no_password.setFlags(data.flags() & ~Qt.ItemIsEditable)
                                        row.append(no_password)

                                    self.signals.download_signal.emit(
                                        row, link, True, self.dl_name, self.progress)
                                    if self.cached_download:
                                        self.cached_downloads.remove(self.cached_download)
                    except Exception as e:
                        logging.error(f"Error processing link {link}: {e}")
                        continue
                    
        except Exception as e:
            logging.error(f"Unexpected error in run method: {e}")
            # 예외 상황 후에도 로딩 화면 종료
            self.gui.hide_loading_overlay()



class DownloadWorker(QRunnable):
    def __init__(self, link, table_model, data, settings, dl_name=''):
        super(DownloadWorker, self).__init__()
        # Args
        self.link = link
        self.table_model = table_model
        self.data = data
        self.signals = WorkerSignals()
        self.paused = self.stopped = self.complete = False
        self.dl_name = dl_name
        self.stop_requested = False  # 종료 요청 플래그 추가

        # Default settings
        self.timeout = 30
        self.proxy_settings = None  # 기본값 설정

        # 사용자 다운로드 폴더 경로 설정
        user_home_directory = os.path.expanduser("~")
        self.dl_directory = os.path.join(user_home_directory, "Downloads")

        # Override defaults from settings
        if settings:
            if settings[0]:
                self.dl_directory = settings[0]
            if settings[2]:
                self.timeout = settings[2]
            if settings[3] is not None:
                self.proxy_settings = settings[3]  # proxy_settings 초기화

        # Proxies 설정
        if proxy_queue.qsize() == 0:
            self.load_proxies()

        # Proxies
        self.proxies = proxy_queue
        

    def load_proxies(self):
        global proxy_queue
        proxies = get_proxies(settings=self.proxy_settings)
        for proxy in proxies:
            proxy_queue.put(proxy)

    # 다운로드 작업을 스레드로 실행
    def run(self):
        download_thread = threading.Thread(target=self.download)
        download_thread.start()

    def stop(self):
        self.stop_requested = True
        
    # QRunnable의 run 메서드 사용
    @pyqtSlot()
    def run(self):
        try:
            # stop_requested 플래그 확인하며 다운로드 실행
            while not self.stop_requested:
                dl_name = download(self)
                self.dl_name = dl_name

                if dl_name and self.stop_requested:
                    logging.debug('Stop Download')
                    if dl_name:
                        os.remove(self.dl_directory + '/' + str(dl_name))
                        logging.debug(f'Temp File Remove: {self.dl_directory}/{dl_name}')
                    break

                if not self.paused:
                    logging.debug('Remove Download')
                    if not dl_name:
                        self.complete = True
                    break
        except Exception as e:
            logging.error(f"Error during download: {e}")

    def stop(self, i):
        self.table_model.removeRow(i)
        self.stopped = True

    def pause(self):
        if not self.complete:
            self.paused = True

    def resume(self):
        if self.paused == True:
            self.paused = False
            if isinstance(self.data, list):
                self.signals.unpause_signal.emit(
                    self.data, self.link, False, self.dl_name)

    def return_data(self):
        if not self.stopped and not self.complete:
            data = []
            data.append(self.link)
            data.append(self.dl_name) if self.dl_name else data.append(None)
            data.append(self.data[6].text()) if self.data[6].text(
            ) != '비밀번호 없음' else data.append(None)
            data.append(self.data[5].value())
            return data
