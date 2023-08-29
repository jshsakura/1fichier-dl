from PyInstaller.utils.hooks import collect_data_files

# Pyinstaller 빌드시 경로에서 누락되는 cacert.pem을 챙겨주는 Hook
datas = collect_data_files('curl_cffi')
