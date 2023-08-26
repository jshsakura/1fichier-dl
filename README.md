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
  <b>브라우저에서 1fichier 다운로드 링크(URL)를 복사</b>
</p>
<br/>
<p align="center">
  <img src="https://raw.githubusercontent.com/jshsakura/1fichier-dl/main/screenshots/preview.png"></img>
</p>

<p align="center">
  <b>1fichier 다운로더에 주소를 입력하는 것으로 간단하게 동작.</b>
</p>

## 😼 기능 소개

⭐ 다운로드 `링크` 주소 입력만으로 다운로드 목록을 관리할 수 있으니 이젠 마음껏 걸어두고 주무셔도 좋습니다.

⭐ 무료 사용자의 연속 다운로드 시 대기시간이 발생하는 불편함을 우회 `Bypass` 합니다.

⭐ 설정 > 연결 메뉴에서 URL을 통해 사용자가 프록시 목록을 직접 입력할 수 있습니다.

*여러분의 인생은 짧습니다. 더이상 기다리지마세요.*

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

## 😻 개선된 사항

- 영문 GUI 한글화 진행 및 GUI 아이콘 컬러의 가독성 개선
- 프로그램이 기본으로 제공하는 기본 프록시 목록의 변경
- pyinstaller로 쉽게 빌드
(단일 파일의 `exe`로 빌드하도록 개선 중)


## 🙀 윈도우가 아닌 환경에서 실행

개발을 위해, 또는 리눅스나 맥에서 파이썬을 통해 직접 GUI를 실행하는 경우 프로젝트 폴더에서 아래와 같이 실행이 가능합니다.
현재 종속성은 단 3가지 뿐이지만 파이썬 3.7 버전 기준으로 진행해야 문제가 없습니다.

```
python 1fichier-dl/1ficher-dl-kr.py
```

## 😾 PyInstaller를 이용한 윈도우 exe 빌드

`Legacy` 프로젝트를 윈도우 프로그램으로 빌드하기 위해 `Python v3.7` 버전을 이용했습니다.
프로젝트 폴더에서 `requirements.txt` 를 설치하고 직접 빌드도 가능합니다.

```
pyinstaller --windowed --noconsole --clean --icon=./1fichier-dl/res/ico.ico --add-data "1fichier-dl/res/*.*;res/" ./1fichier-dl/1ficher-dl-kr.py
```

`--onefile` 옵션 사용시 캐쉬경로가 망가지기 때문에 폴더 구조로 동일하게 빌드합니다.

`PyInstaller`를 이용해 윈도우 프로그램 `exe` 형식으로 빌드하는 경우 사용하는 위 명령어의 예시를 참고해보세요.

## 😽 무한한 감사를 드립니다. 🫶

- 모든 아이콘은 멋진 무료 아이콘을 제공하는 [Feather](https://feathericons.com/)를 이용하고 있습니다.
- 윈도우 프로그램의 아이콘은 [svgrepo](https://www.svgrepo.com/)에서 무료 아이콘을 사용하고 있습니다.
- 무료 `https` 프록시 서버 목록은 `10분`마다 갱신해서 제공하고 있는 [Zaeem20](https://github.com/Zaeem20/FREE_PROXIES_LIST/commits?author=Zaeem20) 이 제작한 [FREE_PROXIES_LIST](https://github.com/Zaeem20/FREE_PROXIES_LIST) 프로젝트를 사용합니다.
- 1Fichier-dl 프로젝트의 제작자는 `manuGMG`이며, 개선판을 만든 [Leinad4Mind](https://github.com/Leinad4Mind/1fichier-dl) 의 `v0.2.0` 버전 프로젝트에서 분기했습니다.
