# scnu-oss-advanced-track-example

아주 간단한 FastAPI HTML 응답 예제입니다.

## 구조

```text
requirements.txt       # 앱 의존성
app/
  main.py              # FastAPI 앱
  .env.example         # 앱 실행 설정 예시
deploy/
  supervisord.conf     # 프로세스 운영 설정
  requirements.txt     # 앱 의존성 + Supervisor
  .env.example         # 서버 접속 및 배포 설정 예시
```

실제 설정은 `app/.env`와 `deploy/.env`에 저장하며 Git에 커밋하지 않습니다.
`deploy/.env`의 비밀번호를 포함한 서버 접속 정보는 로컬에서만 보관합니다.
기존 루트의 `.env`는 `app/.env`, `env`는 `deploy/.env`로 이동했습니다.

## 로컬 실행

프로젝트 루트에서 실행합니다.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp app/.env.example app/.env
python app/main.py
```

이미 `.env`를 설정했다면 복사 단계는 생략합니다.
`app/.env`의 `INTERNAL_HOST`와 `INTERNAL_PORT`로 실행 주소와 포트를 설정합니다.
이미 설정된 환경 변수가 있다면 파일보다 우선합니다.
앱은 실행 디렉터리와 관계없이 `app/main.py` 옆의 `.env`를 읽습니다.

기본 주소인 <http://127.0.0.1:8000/>에 접속하면 다음 HTML을 반환합니다.

```html
Hello, <a href="https://scnuoss.net/">https://scnuoss.net/</a>
```

## 배포 설정

처음 설정할 때 로컬에서 실행합니다.

```sh
cp deploy/.env.example deploy/.env
```

예시 값을 실제 서버 정보로 변경합니다. `INTERNAL_PORT`에는 숫자를 입력합니다.

| 변수 | 용도 |
| --- | --- |
| `USER_ID`, `PASSWORD` | SSH 접속 계정과 비밀번호 |
| `HOST` | SSH 서버 주소 |
| `DEPLOY_ADDRESS` | 배포 후 확인할 공개 홈페이지 주소 |
| `WORK_PATH` | 서버의 프로젝트 루트 경로 |
| `INTERNAL_HOST`, `INTERNAL_PORT` | 서버에서 앱이 수신할 주소와 포트 |

`WORK_PATH` 아래에 최상위 `requirements.txt`와 `app/`, `deploy/` 구조를 유지하도록 파일을 전송합니다.
`deploy/requirements.txt`는 `-r ../requirements.txt`로 앱 의존성을 포함하고 Supervisor를 추가합니다.
로컬 가상환경, 로그, Git 디렉터리, 실제 환경 파일은 전송 대상에서 제외합니다.
서버의 `app/.env`에는 배포 설정에서 지정한 `INTERNAL_HOST`, `INTERNAL_PORT`만 기록합니다.
`deploy/.env`는 서버에 복사하지 않습니다. 앱이 이 파일을 직접 읽지는 않습니다.

## 서버에서 계속 실행하기

서버의 프로젝트 루트에서 실행합니다. Supervisor가 백그라운드에서 앱을 실행하고
종료 시 자동으로 재시작합니다. systemd 설정은 변경하지 않습니다.

```sh
python3 -m venv .venv
.venv/bin/pip install -r deploy/requirements.txt
mkdir -p deploy/.run
chmod 700 deploy/.run
chmod 600 app/.env
.venv/bin/supervisord -c deploy/supervisord.conf
```

서버에는 가상환경과 pip를 생성할 수 있는 Python 환경이 필요합니다.
Supervisor가 이미 실행 중이면 중복 실행하지 않고 아래 명령으로 설정을 반영합니다.
코드만 바뀌었을 때도 `restart`로 앱을 재시작합니다.

```sh
.venv/bin/supervisorctl -c deploy/supervisord.conf reread
.venv/bin/supervisorctl -c deploy/supervisord.conf update
.venv/bin/supervisorctl -c deploy/supervisord.conf restart scnu-fastapi
.venv/bin/supervisorctl -c deploy/supervisord.conf status
```

상태가 `RUNNING`인지 확인하고, `DEPLOY_ADDRESS`에서 HTTP 200과 Hello HTML을 확인합니다.
앱 종료 및 로그 확인:

```sh
.venv/bin/supervisorctl -c deploy/supervisord.conf stop scnu-fastapi
tail -f deploy/.run/app.log
```

서버 재부팅 후에도 실행하려면 `crontab -e`로 아래 항목을 추가합니다.
경로는 실제 `WORK_PATH`에 맞게 변경하며, 기존 등록이 있다면 해당 항목을 교체합니다.
다른 서비스의 cron 항목은 유지합니다.

```cron
@reboot cd /home/a0/html && /home/a0/html/.venv/bin/supervisord -c /home/a0/html/deploy/supervisord.conf >> /home/a0/html/deploy/.run/boot.log 2>&1
```

## 기존 배포를 새 폴더 구조로 전환하기

기존 서버가 루트의 `supervisord.conf`를 사용 중이면 새 파일과 가상환경을 먼저 준비하고,
기존 앱 실행 설정을 서버의 `app/.env`에 옮깁니다. 기존 설정 파일을 보존한 상태에서
아래 명령으로 기존 Supervisor를 종료한 뒤 새 설정으로 시작합니다.

```sh
.venv/bin/supervisorctl -c supervisord.conf shutdown
.venv/bin/supervisord -c deploy/supervisord.conf
.venv/bin/supervisorctl -c deploy/supervisord.conf status
```

이 전환 중에는 잠깐 서비스가 중단됩니다. 기존 cron 항목도 새 경로로 교체하고,
공개 주소의 응답을 확인한 후 사용하지 않는 이전 파일을 정리합니다.
