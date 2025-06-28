# WeMeet Sigma to Kibana Detection Rules Converter

Sigma CLI를 사용하여 Sigma 규칙을 Elasticsearch Lucene 쿼리 및 Kibana Detection Rules로 변환하고 관리하는 Python 도구입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [설치 및 설정](#설치-및-설정)
- [사용법](#사용법)
- [프로젝트 구조](#프로젝트-구조)
- [예제](#예제)
- [테스트](#테스트)
- [문제 해결](#문제-해결)
- [기여하기](#기여하기)

## 🎯 개요

이 프로젝트는 Sigma 규칙을 Kibana Detection Rules로 변환하여 Elastic Stack 환경에서 보안 모니터링을 쉽게 구현할 수 있도록 도와줍니다. Sigma CLI를 완전히 통합하여 안정적이고 정확한 변환을 제공합니다.

### 주요 특징

- ✅ **Sigma CLI 완전 통합**: 공식 Sigma CLI 도구를 직접 활용
- ✅ **모듈화된 설계**: 각 기능이 명확히 분리된 클래스 구조
- ✅ **CLI 인터페이스**: Click을 사용한 직관적인 명령어 인터페이스
- ✅ **유연한 설정**: 환경변수와 CLI 옵션을 통한 설정 관리
- ✅ **에러 처리**: 각 단계별 상세한 에러 메시지와 로깅
- ✅ **테스트 지원**: 완전한 테스트 스위트 제공

## 🚀 주요 기능

### Sigma CLI 관리
- Sigma CLI 설치 상태 확인
- 환경 설정 및 플러그인 관리
- 사용 가능한 대상 및 파이프라인 조회

### 규칙 변환
- Sigma 규칙 → Lucene 쿼리 변환
- Sigma 규칙 → Kibana Detection Rule JSON 변환
- 규칙 유효성 검사

### Kibana Detection Rules 관리
- Detection Rule 생성/수정/삭제
- 규칙 목록 조회 (페이지네이션, 정렬, 필터링 지원)
- 규칙 활성화/비활성화
- 연결 테스트

## 💻 시스템 요구사항

- **Python**: 3.8 이상
- **Sigma CLI**: 최신 버전
- **Kibana**: 7.x 이상 (Detection Rules API 지원)
- **Elasticsearch**: 7.x 이상

## 📦 설치 및 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd WeMeet_Project
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate     # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. Sigma CLI 설치

```bash
# pip를 사용한 설치
pip install sigma-cli

# 또는 pipx를 사용한 설치 (권장)
pipx install sigma-cli
```

### 5. 환경 설정

`.env` 파일을 생성하고 Kibana 연결 정보를 설정합니다:

```bash
# .env 파일 생성
cat > .env << EOF
KIBANA_URL=http://localhost:5601
KIBANA_USERNAME=elastic
KIBANA_PASSWORD=changeme
SIGMA_CLI_PATH=sigma
EOF
```

## 🛠️ 사용법

### 기본 명령어 구조

```bash
python src/main.py [명령어] [옵션]
```

### Sigma CLI 확인 및 설정

```bash
# Sigma CLI 설치 상태 확인
python src/main.py check-sigma-cli

# Sigma CLI 환경 설정
python src/main.py setup-sigma-cli

# Sigma CLI 정보 조회
python src/main.py list-sigma-cli-info
```

### 규칙 변환

```bash
# Sigma 규칙을 Lucene 쿼리로 변환
python src/main.py convert-to-lucene -i examples/suspicious_process_creation.yml

# Sigma 규칙을 Detection Rule JSON으로 변환
python src/main.py convert-to-detection-rule -i examples/suspicious_process_creation.yml -o output.json

# 규칙 유효성 검사
python src/main.py validate-rule -i examples/suspicious_process_creation.yml
```

### Kibana Detection Rules 관리

```bash
# Detection Rule 생성
python src/main.py create-rule -i output.json

# Detection Rules 목록 조회
python src/main.py list-rules

# 페이지네이션, 정렬, 필터링을 사용한 목록 조회
python src/main.py list-rules --page 1 --per-page 10 --sort-field name --sort-order asc --filter "alert.attributes.name:windows"

# 특정 규칙 조회
python src/main.py get-rule --rule-id your-rule-id

# 규칙 업데이트
python src/main.py update-rule --rule-id your-rule-id -i updated_rule.json

# 규칙 삭제
python src/main.py delete-rule --rule-id your-rule-id
```

### 통합 작업

```bash
# Sigma 규칙을 변환하고 바로 Kibana에 생성
python src/main.py convert-and-create -i examples/suspicious_process_creation.yml
```

## 📁 프로젝트 구조

```
WeMeet_Project/
├── src/                          # 소스 코드
│   ├── main.py                   # 메인 CLI 인터페이스
│   ├── sigma_cli_manager.py      # Sigma CLI 관리
│   ├── sigma_cli_converter.py    # Sigma 규칙 변환기
│   ├── sigma_cli_wrapper.py      # Sigma CLI 래퍼
│   └── kibana_client.py          # Kibana API 클라이언트
├── examples/                     # 예제 파일들
│   ├── suspicious_process_creation.yml
│   ├── network_anomaly.yml
│   └── ...
├── tests/                        # 테스트 코드
│   ├── test_kibana_client.py
│   ├── test_converter.py
│   └── ...
├── requirements.txt              # Python 의존성
├── .env                         # 환경 설정 (생성 필요)
├── .gitignore                   # Git 무시 파일
└── README.md                    # 이 파일
```

## 📖 예제

### 1. 기본 변환 예제

```bash
# Sigma 규칙을 Lucene 쿼리로 변환
python src/main.py convert-to-lucene -i examples/suspicious_process_creation.yml

# 출력 예시:
# 생성된 Lucene 쿼리:
# (process.name:cmd.exe OR process.name:cmd) AND (process.args:*powershell* OR process.args:*cmd*)
```

### 2. Detection Rule 생성 예제

```bash
# 1단계: 변환
python src/main.py convert-to-detection-rule -i examples/suspicious_process_creation.yml -o my_rule.json

# 2단계: 생성
python src/main.py create-rule -i my_rule.json

# 또는 한 번에 처리
python src/main.py convert-and-create -i examples/suspicious_process_creation.yml
```

### 3. 규칙 관리 예제

```bash
# 모든 규칙 조회
python src/main.py list-rules

# 특정 조건으로 필터링
python src/main.py list-rules --filter "alert.attributes.severity:high"

# 페이지별 조회
python src/main.py list-rules --page 1 --per-page 5
```

## 🧪 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
python -m unittest discover tests

# 특정 테스트 실행
python -m unittest tests.test_kibana_client.TestKibanaDetectionClient.test_01_create_rule

# 테스트 파일 직접 실행
python tests/test_kibana_client.py
```

### 테스트 환경 설정

테스트를 실행하기 전에 `.env` 파일에 올바른 Kibana 연결 정보가 설정되어 있어야 합니다.

## 🔧 문제 해결

### 일반적인 문제들

#### 1. Sigma CLI 인식 실패

```bash
# Sigma CLI 설치 확인
python src/main.py check-sigma-cli

# 수동 설치
pip install sigma-cli
```

#### 2. Kibana 연결 실패

```bash
# .env 파일 확인
cat .env

# 연결 테스트
python src/main.py list-rules
```

#### 3. 권한 오류

```bash
# Elasticsearch 사용자 권한 확인
# elastic 사용자가 Detection Rules API에 접근 권한이 있어야 함
```

### 로그 확인

각 명령어는 상세한 로그를 출력합니다. 오류 발생 시 로그 메시지를 확인하여 문제를 진단할 수 있습니다.

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 도구는 Sigma CLI를 기반으로 하므로, Sigma CLI의 기능과 제한사항을 따릅니다. 