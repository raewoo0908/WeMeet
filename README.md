# Sigma CLI to Kibana Detection Rules Converter

Sigma CLI를 사용하여 Sigma rule을 Lucene 쿼리로 변환하고 Kibana Detection Rules로 관리하는 도구입니다.

## 🚀 설치

### 1. Sigma CLI 설치

```bash
# pip로 설치
pip install sigma-cli

# 또는 pipx로 설치 (권장)
pipx install sigma-cli

# mac 환경에서
python3 -m pip install sigma-cli
```

### 2. 필요한 플러그인 설치

```bash
# 사용 가능한 플러그인 조회
sigma plugin list

# Lucene 백엔드 설치
sigma plugin install lucene

# Windows ECS 파이프라인 설치
sigma plugin install ecs_windows
```

### 3. 프로젝트 의존성 설치

```bash
pip install -r requirements.txt
```

## 🔧 사용 방법

### 1. Sigma CLI 설치 상태 확인

```bash
python src/main.py check-sigma-cli
```

### 2. Sigma CLI 환경 설정

```bash
# 기본 플러그인으로 환경 설정
python src/main.py setup-sigma-cli

# 특정 플러그인으로 환경 설정
python src/main.py setup-sigma-cli --required-plugins "lucene,ecs_windows,ecs_linux"
```

### 3. Sigma rule을 Lucene 쿼리로 변환

```bash
python src/main.py convert-to-lucene \
  -i examples/suspicious_process_creation.yml \
  --pipeline ecs_windows
```

### 4. Sigma rule을 Kibana Detection Rule로 변환

```bash
python src/main.py convert-to-detection-rule \
  -i examples/suspicious_process_creation.yml \
  -o suspicious_process_creation.detection_rule.json \
  --pipeline ecs_windows
```

# Below from here is now Progressing...
### 5. Detection Rule 생성

```bash
python src/main.py create-rule \
  -i suspicious_process_creation.detection_rule.json \
  --kibana-url https://your-kibana:5601 \
  --username your-username \
  --password your-password
```

### 6. Detection Rule 업데이트

```bash
python src/main.py update-rule \
  --rule-id suspicious-process-creation \
  -i updated_rule.json \
  --kibana-url https://your-kibana:5601
```

### 7. Detection Rule 삭제

```bash
python src/main.py delete-rule \
  --rule-id suspicious-process-creation \
  --kibana-url https://your-kibana:5601
```

### 8. 모든 Detection Rules 조회

```bash
python src/main.py list-rules \
  --kibana-url https://your-kibana:5601
```

### 9. 특정 Detection Rule 조회

```bash
python src/main.py get-rule \
  --rule-id suspicious-process-creation \
  --kibana-url https://your-kibana:5601
```

### 10. 변환과 생성을 한 번에 수행

```bash
python src/main.py convert-and-create \
  -i examples/suspicious_process_creation.yml \
  --kibana-url https://your-kibana:5601 \
  --pipeline ecs_windows
```

### 11. Sigma CLI 정보 조회

```bash
python src/main.py list-sigma-cli-info
```

### 12. Sigma rule 유효성 검사

```bash
python src/main.py validate-rule \
  -i examples/suspicious_process_creation.yml
```

## 🔧 환경 변수 설정

`.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:

```env
KIBANA_URL=https://your-kibana:5601
KIBANA_USERNAME=your-username
KIBANA_PASSWORD=your-password
```

## 📊 지원하는 기능

### Sigma CLI 관리 기능
- ✅ Sigma CLI 설치 확인
- ✅ Sigma CLI 환경 설정
- ✅ 플러그인 설치/제거
- ✅ 사용 가능한 대상/파이프라인 조회
- ✅ Sigma rule 유효성 검사

### 변환 기능
- ✅ Sigma rule → Lucene 쿼리 변환
- ✅ Sigma rule → Kibana Detection Rule JSON 변환
- ✅ 다양한 파이프라인 지원 (ecs_windows, ecs_linux, sysmon 등)

### 관리 기능
- ✅ Detection Rule 생성
- ✅ Detection Rule 업데이트
- ✅ Detection Rule 삭제
- ✅ Detection Rule 조회 (전체/개별)

## 🏗️ 프로젝트 구조

```
src/
├── sigma_cli_manager.py      # Sigma CLI 관리 (설치 확인, 환경 설정)
├── sigma_cli_converter.py    # Sigma CLI 변환 (순수 변환 기능만)
├── kibana_client.py          # Kibana Detection Rule API 클라이언트
└── main.py                   # CLI 인터페이스
```

## 🎯 사용 예시

### 1. 초기 설정

```bash
# 1. Sigma CLI 설치 상태 확인
python src/main.py check-sigma-cli

# 2. 환경 설정 (필요한 플러그인 자동 설치)
python src/main.py setup-sigma-cli
```

### 2. Windows 프로세스 생성 규칙 처리

```bash
# 1. Lucene 쿼리 확인
python src/main.py convert-to-lucene \
  -i examples/suspicious_process_creation.yml

# 2. Detection Rule 생성
python src/main.py convert-and-create \
  -i examples/suspicious_process_creation.yml \
  --kibana-url https://your-kibana:5601
```

### 3. 네트워크 연결 규칙 처리

```bash
# 네트워크 규칙용 파이프라인 사용
python src/main.py convert-and-create \
  -i examples/network_anomaly.yml \
  --kibana-url https://your-kibana:5601 \
  --pipeline ecs_windows
```

## 🛠️ 문제 해결

### 1. Sigma CLI 설치 실패

```bash
# Python 버전 확인
python --version

# pip 업그레이드
pip install --upgrade pip

# 가상환경 사용 권장
python -m venv sigma_env
source sigma_env/bin/activate  # Linux/Mac
```

### 2. 플러그인 설치 실패

```bash
# 플러그인 목록 확인
python src/main.py check-sigma-cli

# 수동 설치
sigma plugin install lucene
```

### 3. 변환 실패

```bash
# Sigma rule 유효성 검사
python src/main.py validate-rule -i your_rule.yml

# 수동 변환 테스트
sigma convert -t lucene -p ecs_windows your_rule.yml
```

### 4. Kibana 연결 실패

```bash
# 연결 테스트
curl -u username:password https://your-kibana:5601/api/status

# 환경 변수 확인
echo $KIBANA_URL
echo $KIBANA_USERNAME
```

## 📚 참고 자료

- [Sigma CLI GitHub](https://github.com/SigmaHQ/sigma-cli)
- [Sigma 규칙 작성 가이드](https://github.com/SigmaHQ/sigma/wiki/Rule-Creation-Guide)
- [ECS 필드 매핑](https://www.elastic.co/guide/en/ecs/current/ecs-field-reference.html)
- [Kibana Query Language](https://www.elastic.co/guide/en/kibana/current/kuery-query.html) 