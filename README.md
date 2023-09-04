**🧙‍♂️ 1Fichier-dl 프로젝트.**

현재 더 이상 유지보수 되고 있지 않은 **1Fichier-dl** 프로젝트의 한국어 사용자용 포크 버전입니다.

(This is a Korean fork version of the 1Fichier-dl project, which is no longer being maintained.)

<p align="left">
  <img src="https://github.com/jshsakura/1fichier-dl/blob/main/screenshots/ico.png?raw=true"></img>
</p>

# 😺 1Fichier 다운로더 한국어화

간단하게 윈도우에서 설치 없이 `exe` 파일로 실행이 가능한 `1Fichier 다운로드 매니저` 프로그램입니다.
매 다운로드 마다 대기시간을 기다릴 필요 없이 가급적 빠른 속도로 다운로드 작업이 가능하도록 도와드립니다.

<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview-1fichier-site.png"></img>
</p>
<p align="center">
  <b>브라우저에서 1fichier.com 다운로드 링크(URL)를 복사해서 입력할 수 있습니다.</b>
</p>
<br/>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview-ouo-shortlink.png"></img>
</p>
<p align="center">
  <b>브라우저에서 ouo.io 단축 링크(URL)를 바로 복사해서 입력하는 경우, 자동으로 reCAPTCHA 우회 처리</b>
</p>
<br/>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview0.png"></img>
</p>

<p align="center">
  <b>1fichier 다운로더 프로그램에 1fichier 링크 주소를 입력하는 것으로 간단하게 동작.</b>
</p>
<br/>
<br/>

<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview_settings0.png"></img>
</p>

<p align="center">
  <b>클립보드에서 복사하거나 여러개의 프록시 서버를 통해 자동으로 대기시간 우회 다운로드.</b>
</p>
<br/>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview_settings1.png"></img>
</p>

<p align="center">
  <b>여러개의 동시 다운로드를 지원하고 환경에 따라 늘리거나 줄일 수 있습니다.</b>
</p>
<br/>
<br/>

## 😼 주요 기능 소개

<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview2.png"></img>
</p>

⭐ 다운로드 `링크` 주소 입력만으로 다운로드 목록을 관리할 수 있으니 이젠 마음껏 걸어두고 주무셔도 좋습니다.

⭐ 무료 사용자의 연속 다운로드 시 대기시간이 발생하는 불편함을 우회 `Bypass` 합니다.

⭐ 설정 > 연결 메뉴에서 URL을 통해 사용자가 프록시 목록을 직접 입력할 수 있습니다. (기본 프록시 대체)

⭐ `1ficher` 링크 외에도 `ouo.io` 등의 단축 `URL`을 직접 입력시 `reCAPTCHA`를 우회한 자동 링크 추가

⭐ `Threading` 을 이용한 동시 프록시 다운로드 지원 (기본 3개 실험적)

⭐ 기본 다운로드 폴더 경로는 윈도우의 `다운로드` 폴더입니다.

_여러분의 인생은 짧습니다. 더이상 기다리지마세요._

<br/>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/Screenshot_Light.png"></img>
</p>

<p align="center">
  <b>밝은 (라이트) 테마</b>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/Screenshot_Dark.png"></img>
</p>

<p align="center">
  <b>어두운 (다크) 테마</b>
</p>
<br/>
<br/>

## 😻 개선된 사항

- 한국어화 진행 및 GUI 아이콘 컬러의 가독성 개선
- 프로그램이 기본으로 제공하는 기본 프록시 목록의 변경
- `PyInstaller`를 이용해 윈도우용 `exe`로 더욱 쉽게 빌드 (원파일 빌드 적용)
- 프록시 우회의 경우 `상태` 항목에 현재 시도 중인 프록시 서버 `IP:PORT` 표기
- 사용자가 현재 진행 상황을 쉽게 볼 수 있도록 `진행률 %` 소숫점 표기 추가
- 링크 복사 시 번거로운 ouo.io의 `reCAPTCHA` 우회 적용
- 다운로드 링크를 추가시 동작하는 `UX` 의 개선 (로딩 화면 및 중복입력 방지)
- 클립보드에서 바로 다운로드로 이어지는 버튼 추가
- 멀티 쓰레드를 이용한 동시 프록시 다운로드 지원 (기본 3개, 설정에서 변경 가능)
  <br/>
  <br/>

## 😹 앞으로 개선할 사항

- `https` 프록시를 적용한 반복 `requests`로 인한 속도저하 개선 (sock5 테스트 중)
- 다운로드 속도가 `100kb` 등으로 느린 프록시 서버에 붙었을 경우 타 프록시로 자동으로 변경
- 동시 다운로드 시 `Threading` 이 아닌 Asyncio를 이용한 비동기 다운로드 지원 (속도 증가)
- 기본사양인 `1ficher` 외에 유사한 타 사이트들의 프로그램 지원 확대
  <br/>
  <br/>

## 🙀 윈도우가 아닌 환경에서 실행

개발을 위해, 또는 리눅스나 맥에서 파이썬을 통해 직접 GUI를 실행하는 경우 프로젝트 폴더에서 아래와 같이 실행이 가능합니다.
현재 종속성은 몇가지 안되지만 파이썬 3.11 버전 기준으로 진행해야 문제가 없습니다.

```
pip install -r requirements.txt
python 1fichier-dl-kr.py
```

<br/>
<br/>

## 😾 PyInstaller를 이용한 윈도우 exe 빌드

`Legacy` 프로젝트를 윈도우 프로그램으로 빌드하기 위해 `Python v3.11` 버전을 이용했습니다.
프로젝트 폴더에서 `requirements.txt` 를 설치하고 직접 빌드도 가능합니다.

```
pyinstaller --windowed --noconsole --onefile --noconfirm --clean --hiddenimport=_cffi_backend --additional-hooks-dir=. --icon=core/gui/res/ico.ico --paths "[파이썬_Lib_경로]" --add-data "core/gui/res/*.*;res/" ./1fichier-dl-kr.py
```

더욱 깔끔한 폴더 구조를 위해 `onefile` 빌드로 수정되었습니다.
윈도우 기준이기 때문에 파일 기본 저장 경로 쪽에 문제가 있는 경우 `onefile`이 아닌, 폴더 구조로 `build` 하셔야합니다.

`PyInstaller`를 이용해 윈도우 프로그램 `exe` 형식으로 빌드하는 경우 위 명령어의 예시를 참고해보세요.
`paths` 항목의 파이썬 `Lib` 경로는 conada 사용시 `env` 경로의 하위가 되겠습니다.

엉뚱하게도 `PyInstaller`의 고질적인 바이러스 오진 문제로 직접 `PyInstaller` 소스를 다운 받아 `python ./waf distclean all` 로 기존 빌드환경을 초기화 한 뒤 `pip install .` 로 폴더 내에서 `setup.py`를 통해 직접 설치해야합니다.

<br/>
<br/>

## 😽 무한한 감사를 드립니다. 🫶

- 모든 아이콘은 멋진 무료 아이콘을 제공하는 [Feather](https://feathericons.com/)를 이용합니다.
- 윈도우 프로그램의 아이콘은 [svgrepo](https://www.svgrepo.com/)에서 무료 아이콘을 제공합니다.
- 무료 `https` 프록시 서버 목록은 `10분`마다 갱신해서 제공하고 있는 [Zaeem20](https://github.com/Zaeem20/FREE_PROXIES_LIST/commits?author=Zaeem20) 이 제작한 [FREE_PROXIES_LIST](https://github.com/Zaeem20/FREE_PROXIES_LIST) 프로젝트 외 다수 사용
- 1Fichier-dl 프로젝트의 제작자는 `manuGMG`이며, 개선판을 만든 [Leinad4Mind](https://github.com/Leinad4Mind/1fichier-dl) 의 `v0.2.0` 버전 프로젝트에서 분기
- 링크 복사시 불편함을 줄이기 위해 `ouo.io` 단축 `URL`의 경우 `reCAPTCHA`를 우회하는 [xcscxr](https://github.com/xcscxr) 의 [ouo-bypass](https://github.com/xcscxr/ouo-bypass) 프로젝트 적용
- 친절한 도우미, 의외로 멍청한 [ChatGPT](https://chat.openai.com/)의 코드 리팩토링 서포트.
