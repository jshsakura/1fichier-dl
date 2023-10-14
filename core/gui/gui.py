import sys
import queue
import logging
import pickle
import os
import time
import qdarktheme
import webbrowser
import PyQt5.sip
from ..download.workers import FilterWorker, DownloadWorker
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon, QStandardItemModel, QPixmap, QFontDatabase, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                             QPushButton, QSpinBox, QWidget, QMessageBox,
                             QTableView, QHBoxLayout,
                             QPlainTextEdit, QVBoxLayout, QAbstractItemView,
                             QAbstractScrollArea, QLabel, QLineEdit,
                             QFileDialog, QProgressBar, QStackedWidget,
                             QFormLayout, QListWidget, QComboBox, QSizePolicy)
import tkinter as tk
proxy_queue = queue.Queue()


def absp(path):
    '''
    Get absolute path.
    '''
    if getattr(sys, "frozen", False):
        # Pyinstaller 컴파일 이후 경로
        resolved_path = resource_path(path)
    else:
        # Python 파일 실행시 경로
        relative_path = os.path.join(os.path.dirname(__file__), '.')
        resolved_path = os.path.join(os.path.abspath(relative_path), path)

    return resolved_path


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def abs_config(path):
    # 프로그램 실행 경로로 고정
    resolved_path = os.path.abspath(path)
    return resolved_path


def alert(text):
    '''
    Create and show QMessageBox Alert.
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle('안내')
    msg.setText(text)
    msg.exec_()


def check_selection(table):
    '''
    Get selected rows from table.
    Returns list: [Rows]
    '''
    selection = []
    for index in table.selectionModel().selectedRows():
        selection.append(index.row())
    if not selection:
        alert('다운로드 목록에서 먼저 파일을 선택해주세요.')
    else:
        return selection


def create_file(f):
    '''
    Create empty file.
    [note] Used to create app/settings and app/cache.
    '''
    f = abs_config(f)
    logging.debug(f'Attempting to create file: {f}...')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    f = open(f, 'x')
    f.close()


def getClipboardText():
    root = tk.Tk()
    # keep the window from showing
    root.withdraw()
    return root.clipboard_get()


class GuiBehavior:
    def __init__(self, gui):
        self.filter_thread = QThreadPool()
        self.download_thread = QThreadPool()
        # Limits concurrent downloads to 1.
        self.download_thread.setMaxThreadCount(3)
        self.download_workers = []
        self.gui = gui
        self.handle_init()

    def handle_init(self):
        '''
        Load cached downloads.
        Create file in case it does not exist.
        '''
        try:
            with open(abs_config('app/cache'), 'rb') as f:
                self.cached_downloads = pickle.load(f)
                for download in self.cached_downloads:
                    self.gui.links = download[0]
                    self.add_links(True, download)
        except EOFError:
            self.cached_downloads = []
            logging.debug('No cached downloads.')
        except FileNotFoundError:
            logging.debug('create New cache File.')
            self.cached_downloads = []
            create_file('app/cache')

        '''
        Load settings.
        Create file in case it doesn't exist.
        '''
        try:
            with open(abs_config('app/settings'), 'rb') as f:
                self.settings = pickle.load(f)
                thread_count = self.settings[4]
                self.download_thread.setMaxThreadCount(int(thread_count))
                logging.debug('Now Settings Thread Count:'+str(thread_count))
        except EOFError:
            self.settings = None
            logging.debug('No settings found.')
        except FileNotFoundError:
            self.settings = None
            logging.debug('Create New settings File.')
            create_file('app/settings')
        except IndexError:
            # settings 리스트의 네 번째 요소가 없을 때 기본값 3 사용
            self.settings = None
            thread_count = 3
            self.download_thread.setMaxThreadCount(thread_count)

    def show_loading_overlay(self):
        '''
        Show the loading overlay.
        '''
        if self.gui:
            self.gui.show_loading_overlay()

    def hide_loading_overlay(self):
        '''
        Show the loading overlay.
        '''
        if self.gui:
            self.gui.hide_loading_overlay()

    def resume_download(self):
        '''
        Resume selected downloads.
        '''
        selected_rows = check_selection(self.gui.table)

        if selected_rows:
            for i in selected_rows:
                if i < len(self.download_workers):
                    self.download_workers[i].resume()

    def stop_download(self):
        '''
        Stop selected downloads.
        '''
        selected_rows = check_selection(self.gui.table)

        if selected_rows:
            for i in reversed(selected_rows):
                if i < len(self.download_workers):
                    self.download_workers[i].stop(i)
                    # Remove the download worker from the list
                    del self.download_workers[i]

    def pause_download(self):
        '''
        Pause selected downloads.
        '''
        selected_rows = check_selection(self.gui.table)
        if selected_rows:
            for i in selected_rows:
                if i < len(self.download_workers):
                    update_data = [None, None, '일시정지', None, '0 B/s']
                    # 리스트 타입인 경우에만 update_signal
                    if isinstance(self.download_workers[i].data, list):
                        self.download_workers[i].signals.update_signal.emit(
                            self.download_workers[i].data, update_data)
                        self.download_workers[i].pause()

    def add_links(self, state, cached_download=''):
        '''
        Calls FilterWorker()
        '''
        logging.debug('Call add_links')
        # 로딩 오버레이 표시
        self.show_loading_overlay()
        worker = FilterWorker(
            self, cached_download, (self.gui.password.text() if not cached_download else ''))

        worker.signals.download_signal.connect(self.download_receive_signal)
        worker.signals.alert_signal.connect(alert)

        self.filter_thread.start(worker)

    def download_receive_signal(self, row, link, append_row=True, dl_name='', progress=0):
        '''
        Append download to row and start download.
        '''
        if append_row:
            self.gui.table_model.appendRow(row)
            index = self.gui.table_model.index(
                self.gui.table_model.rowCount()-1, 5)
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            progress_bar.setGeometry(200, 150, 200, 30)
            # setting value of n for 2 decimal values
            n = 100
            # setting maximum value for 2 decimal points
            progress_bar.setMaximum(100 * n)
            self.gui.table.setIndexWidget(index, progress_bar)
            row[5] = progress_bar

        worker = DownloadWorker(
            link, self.gui.table_model, row, self.settings, dl_name)

        worker.signals.update_signal.connect(self.update_receive_signal)
        worker.signals.unpause_signal.connect(self.download_receive_signal)

        self.download_thread.start(worker)
        self.download_workers.append(worker)
        self.hide_loading_overlay()
        # 링크 추가 후 버튼 재활성화
        self.gui.add_links_complete()

    def update_receive_signal(self, data, items):
        '''
        Update download data.
        items = [File Name, Size, Down Speed, Progress, Pass]
        '''
        if data and isinstance(data, list) and isinstance(items, list):
            if not PyQt5.sip.isdeleted(data[2]):
                for i in range(len(items)):
                    if items[i] and isinstance(items[i], str):
                        data[i].setText(str(items[i]))
                    if items[i] and not isinstance(items[i], str):
                        # setting the value by multiplying it to 100
                        n = 100
                        # progress_bar float issue casting fix
                        data[i].setValue(int(items[i]) * n)
                        data[i].setFormat("%.02f %%" % items[i])

    def set_dl_directory(self):
        file_dialog = QFileDialog(self.gui.settings)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.exec_()
        self.gui.dl_directory_input.setText(file_dialog.selectedFiles()[0])

    def change_theme(self, theme=None):
        '''
        Change app palette (theme).
        0 = Light
        1 = Dark
        '''
        if theme:
            self.gui.theme_select.setCurrentIndex(theme)

        if self.gui.theme_select.currentIndex() == 0:
            qdarktheme.setup_theme("light")
            # self.gui.app.setPalette(self.gui.main.style().standardPalette())
        elif self.gui.theme_select.currentIndex() == 1:
            qdarktheme.setup_theme("dark")
            # self.gui.app.setPalette(dark_theme)

    def save_settings(self):
        with open(abs_config('app/settings'), 'wb') as f:
            settings = []
            settings.append(self.gui.dl_directory_input.text())
            # Download Directory - 0
            # Theme              - 1
            settings.append(self.gui.theme_select.currentIndex())
            settings.append(self.gui.timeout_input.value())
            # Timeout            - 2
            # Proxy Settings     - 3
            settings.append(self.gui.proxy_settings_input.text())
            # 멀티 다운로드 갯수
            settings.append(self.gui.thread_input.value())
            pickle.dump(settings, f)
            self.settings = settings
        self.gui.settings.hide()

    def select_settings(self):
        '''
        Select settings page.
        '''
        selection = self.gui.settings_list.selectedIndexes()[0].row()
        self.gui.stacked_settings.setCurrentIndex(selection)

    def handle_exit(self):
        '''
        Save cached downloads data.
        '''
        active_downloads = []
        for w in self.download_workers:
            download = w.return_data()
            if download:
                active_downloads.append(download)
        active_downloads.extend(self.cached_downloads)

        with open(abs_config('app/cache'), 'wb') as f:
            if active_downloads:
                pickle.dump(active_downloads, f)

        os._exit(1)


class Gui:
    def __init__(self):
        # Init GuiBehavior()
        self.app_name = '1Fichier 다운로더'
        self.font = None

        # Create App
        qdarktheme.enable_hi_dpi()
        app = QApplication(sys.argv)
        qdarktheme.setup_theme("light")

        font_database = QFontDatabase()
        font_id = font_database.addApplicationFont(
            absp("res/NanumGothic.ttf"))
        if font_id == -1:
            logging.debug("Font load failed!")
        else:
            font_families = font_database.applicationFontFamilies(font_id)
            self.font = QFont(font_families[0], 10)

        app.setWindowIcon(QIcon(absp('res/ico.ico')))
        app.setStyle('Fusion')
        self.app = app

        # Initialize self.main
        self.main_init()
        self.actions = GuiBehavior(self)
        app.aboutToQuit.connect(self.actions.handle_exit)

        # Create Windows
        self.main_win()
        self.add_links_win()
        # self.add_links_clipboard()
        self.settings_win()

        # Change App Theme to saved one (Palette)
        if self.actions.settings:
            self.actions.change_theme(self.actions.settings[1])

        sys.exit(app.exec_())

    def main_init(self):
        # Define Main Window
        self.main = QMainWindow()
        self.main.setWindowTitle(self.app_name)
        widget = QWidget(self.main)
        self.main.setCentralWidget(widget)

        # Create Grid
        grid = QGridLayout()

        # download_clipboard_btn 생성 및 설정
        download_clipboard_btn = QPushButton(
            QIcon(absp('res/clipboard.svg')), ' 클립보드에서 추가')
        download_clipboard_btn.clicked.connect(self.add_links_clipboard)
        download_clipboard_btn.setFont(self.font)

        # Top Buttons
        download_btn = QPushButton(
            QIcon(absp('res/download.svg')), ' 다운로드 주소 추가')
        download_btn.clicked.connect(lambda: self.add_links.show(
        ) if not self.add_links.isVisible() else self.add_links.raise_())
        download_btn.setFont(self.font)

        settings_btn = QPushButton(
            QIcon(absp('res/settings.svg')), ' 설정')
        settings_btn.clicked.connect(lambda: self.settings.show(
        ) if not self.settings.isVisible() else self.settings.raise_())
        settings_btn.setFont(self.font)

        # Table
        self.table = QTableView()
        headers = ['파일명', '크기', '상태', '프록시 서버',
                   '전송 속도', '진행률', '비밀번호']
        self.table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        if self.font:
            self.table.setFont(self.font)

        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(headers)
        self.table.setModel(self.table_model)

        # Append widgets to grid
        grid.addWidget(download_clipboard_btn, 0, 0)
        grid.addWidget(download_btn, 0, 1)
        # grid.addWidget(download_clipboard_btn, 0, 1)
        grid.addWidget(settings_btn, 0, 2)
        grid.addWidget(self.table, 1, 0, 1, 3)

        # Add buttons to Horizontal Layout
        hbox = QHBoxLayout()
        # Bottom Buttons
        self.main.resume_btn = QPushButton(
            QIcon(absp('res/resume.svg')), ' 선택항목 시작')
        self.main.resume_btn.setFont(self.font)
        self.main.pause_btn = QPushButton(
            QIcon(absp('res/pause.svg')), ' 선택항목 일시정지')
        self.main.pause_btn.setFont(self.font)
        self.main.stop_btn = QPushButton(
            QIcon(absp('res/stop.svg')), ' 목록에서 제거')
        self.main.stop_btn.setFont(self.font)

        hbox.addWidget(self.main.resume_btn)
        hbox.addWidget(self.main.pause_btn)
        hbox.addWidget(self.main.stop_btn)

        self.main.setWindowFlags(self.main.windowFlags()
                                 & Qt.CustomizeWindowHint)

        grid.addLayout(hbox, 2, 0, 1, 3)
        widget.setLayout(grid)
        self.main.resize(730, 415)
        # Set size policies for the table
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 로딩 오버레이 위젯 생성
        self.main.loading_overlay = QWidget(self.main)
        self.main.loading_overlay.setGeometry(
            0, 0, self.main.width(), self.main.height())
        self.main.loading_overlay.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0);")
        self.main.loading_overlay.setVisible(False)

        # SVG 이미지를 로딩 오버레이 위젯에 추가
        svg_widget = QSvgWidget(absp('res/loading_image.svg'))
        svg_widget.setGeometry(0, 0, 100, 100)  # 중앙에 표시하려면 위치와 크기 조정이 필요합니다.
        svg_layout = QVBoxLayout(self.main.loading_overlay)
        svg_layout.addWidget(svg_widget)
        svg_layout.setAlignment(Qt.AlignCenter)

        self.main.show()

    def main_win(self):
        self.main.resume_btn.clicked.connect(self.actions.resume_download)
        self.main.pause_btn.clicked.connect(self.actions.pause_download)
        self.main.stop_btn.clicked.connect(self.actions.stop_download)

    # 클립보드의 주소를 가져와서 add_links로 전달하는 메서드
    def add_links_clipboard(self):
        clipboard_text = getClipboardText()
        if clipboard_text:
            lines = clipboard_text.split('\n')
            if lines:
                self.links.setPlainText(lines[0])
            else:
                self.links.setPlainText(clipboard_text)
            self.add_to_download_list()

    # 로딩 오버레이를 활성화하는 메서드
    def show_loading_overlay(self):
        if self.main:
            self.main.loading_overlay.setVisible(True)

    # 로딩 오버레이를 비활성화하는 메서드
    def hide_loading_overlay(self):
        if self.main:
            self.main.loading_overlay.setVisible(False)

    def add_links_win(self):
        # Define Add Links Win
        self.add_links = QMainWindow(self.main)
        self.add_links.setWindowTitle('다운로드 주소 추가')
        widget = QWidget(self.add_links)
        self.add_links.setCentralWidget(widget)

        # Create Vertical Layout
        layout = QVBoxLayout()

        # Links input
        layout.addWidget(QLabel('링크 목록 (단건 또는 엔터치고 여러건 입력)'))
        self.links = QPlainTextEdit()
        layout.addWidget(self.links)

        # Password input
        layout.addWidget(QLabel('비밀번호 (별도로 설정된 경우에만 입력)'))
        self.password = QLineEdit()
        layout.addWidget(self.password)

        # Add links
        self.add_btn = QPushButton('다운로드 목록에 추가')
        self.add_btn.clicked.connect(self.add_to_download_list)
        layout.addWidget(self.add_btn)

        self.add_links.setMinimumSize(300, 200)
        widget.setLayout(layout)

    def settings_win(self):
        # Define Settings Win
        self.settings = QMainWindow(self.main)
        self.settings.setWindowTitle('설정')

        # Create StackedWidget and Selection List
        self.stacked_settings = QStackedWidget()
        self.settings_list = QListWidget()
        self.settings_list.setFixedWidth(110)
        self.settings_list.addItems(['다운로드 및 테마', '프록시 (Proxy)', '프로그램 정보'])
        self.settings_list.clicked.connect(self.actions.select_settings)

        # Central Widget
        central_widget = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.settings_list)
        hbox.addWidget(self.stacked_settings)
        central_widget.setLayout(hbox)
        self.settings.setCentralWidget(central_widget)

        '''
        Child widget
        Behavior Settings
        '''

        behavior_settings = QWidget()
        self.stacked_settings.addWidget(behavior_settings)

        # Main Layouts
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        form_layout = QFormLayout()

        # Change Directory
        form_layout.addRow(QLabel('기본 다운로드 폴더:'))

        dl_directory_btn = QPushButton('폴더 선택..')
        dl_directory_btn.clicked.connect(self.actions.set_dl_directory)

        self.dl_directory_input = QLineEdit()
        if self.actions.settings is not None:
            self.dl_directory_input.setText(self.actions.settings[0])
        self.dl_directory_input.setDisabled(True)

        form_layout.addRow(dl_directory_btn, self.dl_directory_input)

        # Bottom Buttons
        save_settings = QPushButton('저장')
        save_settings.clicked.connect(self.actions.save_settings)

        # Change theme
        form_layout.addRow(QLabel('테마 변경:'))

        self.theme_select = QComboBox()
        self.theme_select.addItems(['밝은 테마', '어두운 테마'])
        self.theme_select.currentIndexChanged.connect(
            self.actions.change_theme)
        form_layout.addRow(self.theme_select)

        vbox.addLayout(form_layout)
        vbox.addStretch()
        vbox.addWidget(save_settings)
        behavior_settings.setLayout(vbox)

        '''
        Child widget
        Connection Settings
        '''

        connection_settings = QWidget()
        self.stacked_settings.addWidget(connection_settings)

        # Main Layouts
        vbox_c = QVBoxLayout()
        vbox_c.setAlignment(Qt.AlignTop)
        form_layout_c = QFormLayout()

        # Timeout
        form_layout_c.addRow(QLabel('타임아웃 변경(기본 30초):'))
        self.timeout_input = QSpinBox()
        if self.actions.settings is not None:
            self.timeout_input.setValue(self.actions.settings[2])
        else:
            self.timeout_input.setValue(30)

        form_layout_c.addRow(self.timeout_input)

        # Proxy settings
        form_layout_c.addRow(QLabel('프록시(Proxy) 목록 직접 입력:'))
        self.proxy_settings_input = QLineEdit()
        if self.actions.settings is not None:
            self.proxy_settings_input.setText(self.actions.settings[3])

        form_layout_c.addRow(self.proxy_settings_input)

        # Timeout
        form_layout_c.addRow(QLabel('동시 프록시 다운로드 갯수 (재시작 필요):'))
        self.thread_input = QSpinBox()
        if self.actions.settings is not None:
            self.thread_input.setValue(self.actions.settings[4])
        else:
            self.thread_input.setValue(3)

        form_layout_c.addRow(self.thread_input)

        # Bottom buttons
        save_settings_c = QPushButton('저장')
        save_settings_c.clicked.connect(self.actions.save_settings)

        vbox_c.addLayout(form_layout_c)
        vbox_c.addStretch()
        vbox_c.addWidget(save_settings_c)
        connection_settings.setLayout(vbox_c)

        '''
        Child widget
        About
        '''

        about_settings = QWidget()
        self.stacked_settings.addWidget(about_settings)

        about_layout = QGridLayout()
        about_layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo.setPixmap(QPixmap(absp('res/ico.svg')))
        logo.setAlignment(Qt.AlignCenter)

        text = QLabel(self.app_name+' (한글)')
        text.setStyleSheet('font-weight: bold; color: #4256AD')

        github_btn = QPushButton(QIcon(absp('res/github.svg')), '')
        github_btn.setFixedWidth(32)
        github_btn.clicked.connect(lambda: webbrowser.open(
            'https://github.com/jshsakura/1fichier-dl'))

        about_layout.addWidget(logo, 0, 0, 1, 0)
        about_layout.addWidget(github_btn, 1, 0)
        about_layout.addWidget(text, 1, 1)
        about_settings.setLayout(about_layout)

    def add_links_complete(self):
        # 작업이 완료되면 버튼의 상태를 변경합니다.
        self.add_btn.setText("다운로드 목록에 추가")
        self.add_btn.setEnabled(True)
        # 링크 입력창 초기화
        self.links.setEnabled(True)
        self.password.setEnabled(True)
        self.links.clear()

    def add_to_download_list(self):
        # '다운로드 목록에 추가' 버튼을 비활성화합니다.
        self.add_btn.setText("다운로드 목록에 추가 중...")
        self.add_btn.setEnabled(False)

        # 입력된 링크를 가져와서 리스트로 변환합니다.
        links_text = self.links.toPlainText()
        download_links = links_text.split('\n')
        self.links.setDisabled(True)
        self.password.setDisabled(True)

        for link in download_links:
            if link.strip():  # 빈 줄이 아닌 경우에만 추가합니다.
                # 'add_links'를 사용, 다운로드 링크를 추가합니다.
                self.actions.add_links(link)
