# WeMeet Sigma to Kibana Detection Rules Converter

Sigma CLI를 사용하여 Sigma 규칙을 Elasticsearch Lucene 쿼리 및 Kibana Detection Rules로 변환하고 관리하는 Python 도구입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [설치 및 설정](#설치-및-설정)
- [명령어 사용법](#명령어-사용법)
- [명령어 예시](#명령어-예시)
- [프로젝트 구조](#프로젝트-구조)

## 🎯 개요

이 프로젝트는 Sigma 규칙을 Kibana Detection Rules로 변환하여 Elastic Stack 환경에서 보안 모니터링을 쉽게 구현할 수 있도록 도와줍니다. Sigma CLI를 완전히 통합하여 안정적이고 정확한 변환을 제공하며, 디렉터리 구조를 유지하면서 대량의 Sigma 규칙을 처리할 수 있습니다.

### 주요 특징

- ✅ **Sigma CLI 완전 통합**: 공식 Sigma CLI 도구를 직접 활용
- ✅ **모듈화된 설계**: 각 기능이 명확히 분리된 클래스 구조
- ✅ **CLI 인터페이스**: Click을 사용한 직관적인 명령어 인터페이스
- ✅ **유연한 설정**: 환경변수와 CLI 옵션을 통한 설정 관리
- ✅ **배치 처리**: 디렉터리 내 모든 Sigma 규칙을 일괄 처리
- ✅ **구조 유지**: 원본 디렉터리 구조를 유지하면서 변환
- ✅ **자동 파이프라인 선택**: Sigma 규칙의 로그소스에 따라 적절한 파이프라인 자동 선택
- ✅ **에러 처리**: 각 단계별 상세한 에러 메시지와 로깅

## 🚀 주요 기능

### Sigma CLI 관리
- Sigma CLI 설치 상태 확인
- 환경 설정 및 플러그인 관리
- 사용 가능한 대상 및 파이프라인 조회

### 규칙 변환
- Sigma 규칙 → Lucene 쿼리 변환
- Sigma 규칙 → Kibana Detection Rule JSON 변환
- 규칙 유효성 검사
- 자동 파이프라인 선택 (ecs_windows, sysmon, ecs_windows_old 등)
- 추가 필드 지원: Detection Rule 생성 시 커스텀 필드 추가

### Kibana Detection Rules 관리
- Detection Rule 생성/수정/삭제
- 규칙 목록 조회 (페이지네이션, 정렬, 필터링 지원)
- 규칙 활성화/비활성화
- Failed 상태 규칙 일괄 삭제
- 연결 테스트

### 배치 처리
- 디렉터리 내 모든 Sigma 규칙 일괄 변환
- 디렉터리 구조 유지하면서 변환
- 변환과 Kibana 등록을 한 번에 처리
- 변환만 수행하는 옵션 제공

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

## 🛠️ 명령어 사용법

### 기본 명령어 구조

```bash
python src/main.py [명령어] [옵션]
```

### Sigma CLI 관리 명령어

| 명령어 | 설명 | 옵션 |
|--------|------|------|
| `check-sigma-cli` | Sigma CLI 설치 상태 확인 | `--sigma-cli-path` |
| `setup-sigma-cli` | Sigma CLI 환경 설정 | `--sigma-cli-path`, `--required-plugins` |
| `list-sigma-cli-info` | Sigma CLI 정보 조회 | `--sigma-cli-path` |

### 규칙 변환 명령어

| 명령어 | 설명 | 주요 옵션 |
|--------|------|-----------|
| `convert-to-lucene` | Sigma 규칙을 Lucene 쿼리로 변환 | `-i`, `--pipeline`, `--sigma-cli-path` |
| `convert-to-detection-rule` | Sigma 규칙을 Detection Rule JSON으로 변환 | `-i`, `-o`, `--pipeline`, `--additional-fields` |
| `validate-rule` | Sigma 규칙 유효성 검사 | `-i`, `--sigma-cli-path` |

### Kibana Detection Rules 관리 명령어

| 명령어 | 설명 | 주요 옵션 |
|--------|------|-----------|
| `create-rule` | Detection Rule 생성 | `-i`, `--kibana-url`, `--username`, `--password` |
| `update-rule` | Detection Rule 업데이트 | `--rule-id`, `-i`, `--kibana-url` |
| `delete-rule` | Detection Rule 삭제 | `--rule-id`, `--kibana-url` |
| `list-rules` | Detection Rules 목록 조회 | `--page`, `--per-page`, `--sort-field`, `--filter` |
| `get-rule` | 특정 Detection Rule 조회 | `--rule-id`, `--kibana-url` |
| `delete-failed-rules` | Failed 상태 규칙 일괄 삭제 | `--force`, `--kibana-url` |

### 통합 및 배치 처리 명령어

| 명령어 | 설명 | 주요 옵션 |
|--------|------|-----------|
| `convert-and-create` | 단일 파일 변환 및 생성 | `-i`, `--pipeline`, `--additional-fields` |
| `convert-and-create-batch` | 배치 변환 및 생성 | `-i`, `-o`, `--pipeline`, `--additional-fields` |
| `create-rules-batch` | JSON 파일들 일괄 등록 | `-i`, `--kibana-url` |
| `convert-and-create-batch-structure` | 구조 유지하며 변환 및 생성 | `-i`, `-o`, `--skip-kibana` |

## 📝 명령어 예시

### Sigma CLI 확인 및 설정

```bash
# Sigma CLI 설치 상태 확인
python src/main.py check-sigma-cli

# Sigma CLI 환경 설정
python src/main.py setup-sigma-cli

# Sigma CLI 정보 조회
python src/main.py list-sigma-cli-info
```

### 단일 규칙 변환

```bash
# Sigma 규칙을 Lucene 쿼리로 변환
python src/main.py convert-to-lucene -i sigma_all_rules/rules/windows/builtin/security/win_security_susp_lsass_dump.yml

# Sigma 규칙을 Detection Rule JSON으로 변환
python src/main.py convert-to-detection-rule \
    -i sigma_all_rules/rules/windows/builtin/security/win_security_susp_lsass_dump.yml \
    -o detection_rules/lsass_dump.json

# 추가 필드와 함께 변환
python src/main.py convert-to-detection-rule \
    -i sigma_all_rules/rules/windows/builtin/security/win_security_susp_lsass_dump.yml \
    -o detection_rules/lsass_dump.json \
    --additional-fields '{"interval": "5m", "max_signals": 100, "enabled": true}'
```

### 규칙 유효성 검사

```bash
# 단일 파일 유효성 검사
python src/main.py validate-rule -i sigma_all_rules/rules/windows/builtin/security/win_security_susp_lsass_dump.yml

# 디렉터리 내 모든 파일 유효성 검사
python src/main.py validate-rule -i sigma_all_rules/rules/windows/builtin/security/
```

### Kibana Detection Rules 관리

```bash
# Detection Rule 생성
python src/main.py create-rule -i detection_rules/lsass_dump.json

# Detection Rules 목록 조회
python src/main.py list-rules

# 페이지네이션을 사용한 목록 조회
python src/main.py list-rules --page 1 --per-page 20 --sort-field name --sort-order asc

# 필터링을 사용한 목록 조회
python src/main.py list-rules --filter "alert.attributes.name:windows"

# 특정 규칙 조회
python src/main.py get-rule --rule-id aa1697b7-d611-4f9a-9cb2-5125b4ccfd5c

# 규칙 업데이트
python src/main.py update-rule --rule-id aa1697b7-d611-4f9a-9cb2-5125b4ccfd5c -i updated_rule.json

# 규칙 삭제
python src/main.py delete-rule --rule-id aa1697b7-d611-4f9a-9cb2-5125b4ccfd5c

# Failed 상태 규칙 일괄 삭제
python src/main.py delete-failed-rules

# 확인 없이 강제 삭제
python src/main.py delete-failed-rules --force
```

### 통합 작업

```bash
# 단일 파일 변환 및 생성
python src/main.py convert-and-create \
    -i sigma_all_rules/rules/windows/builtin/security/win_security_susp_lsass_dump.yml \
    --additional-fields '{"interval": "5m", "max_signals": 100}'
```

### 배치 처리

```bash
# 디렉터리 내 모든 Sigma 규칙을 Detection Rule로 변환
python src/main.py convert-to-detection-rule \
    -i sigma_all_rules/rules/windows/builtin/security/ \
    -o detection_rules/security/

# 배치 변환 및 Kibana 등록
python src/main.py convert-and-create-batch \
    -i sigma_all_rules/rules/windows/builtin/security/ \
    -o detection_rules/security/ \
    --additional-fields '{"interval": "10m", "max_signals": 200}'

# JSON 파일들 일괄 등록
python src/main.py create-rules-batch -i detection_rules/security/

# 구조 유지하며 변환 (Kibana 등록 없이)
python src/main.py convert-and-create-batch-structure \
    -i sigma_all_rules/rules/windows/builtin/ \
    -o detection_rules/windows_builtin/ \
    --skip-kibana

# 구조 유지하며 변환 및 Kibana 등록
python src/main.py convert-and-create-batch-structure \
    -i sigma_all_rules/rules/windows/builtin/ \
    -o detection_rules/windows_builtin/ \
    --additional-fields '{"interval": "15m", "max_signals": 300}'
```

## 📁 프로젝트 구조

```
WeMeet_Project/
├── src/                          # 소스 코드
│   ├── __init__.py
│   ├── main.py                   # CLI 메인 모듈
│   ├── sigma_cli_manager.py      # Sigma CLI 관리자
│   ├── sigma_cli_converter.py    # Sigma CLI 변환기
│   └── kibana_client.py          # Kibana API 클라이언트
├── detection_rules/              # 변환된 Detection Rules (생성됨)
│   └── windows/
│       └── builtin/
│           └── system/
│               └── *.detection_rule.json
├── sigma_all_rules/              # Sigma 규칙 라이브러리
│   └── rules/
│       └── windows/
│           └── builtin/
│               ├── security/
│               ├── system/
│               ├── application/
│               └── ...
├── examples/                     # 예제 파일들
│   ├── and_or_condition_test.yml
│   ├── batch_rules/
│   ├── network_anomaly.yml
│   └── simple_and_condition.yml
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   ├── converted_files/
│   ├── test_additional_fields.py
│   └── test_batch_processing.py
├── requirements.txt              # Python 의존성
├── .env                         # 환경 설정 (생성됨)
└── README.md                    # 프로젝트 문서
```

### 주요 모듈 설명

#### `src/main.py`
- CLI 명령어 정의 및 실행
- Click 프레임워크를 사용한 명령어 인터페이스
- 환경변수 로드 및 기본값 설정

#### `src/sigma_cli_manager.py`
- Sigma CLI 설치 상태 확인
- 환경 설정 및 플러그인 관리
- 사용 가능한 대상 및 파이프라인 조회

#### `src/sigma_cli_converter.py`
- Sigma 규칙을 Lucene 쿼리로 변환
- Sigma 규칙을 Kibana Detection Rule JSON으로 변환
- 자동 파이프라인 선택 로직
- 규칙 유효성 검사

#### `src/kibana_client.py`
- Kibana Detection Rules API 클라이언트
- 규칙 생성/수정/삭제/조회
- 연결 테스트 및 에러 처리

### 자동 파이프라인 선택 로직

변환기는 Sigma 규칙의 로그소스에 따라 적절한 파이프라인을 자동으로 선택합니다:

- **ecs_windows**: Windows 이벤트 (security, system, application 등)
- **sysmon**: PowerShell 관련 이벤트
- **ecs_windows_old**: WMI 이벤트
- **ecs_kubernetes**: Kubernetes 이벤트
- **ecs_zeek_beats**: Zeek 네트워크 로그

### 지원하는 Windows 이벤트 카테고리

- **서비스**: sysmon, windefend, terminalservices*, taskscheduler
- **카테고리**: pipe_created, network_connection, image_load, file_*, driver_load, dns_query, create_stream_hash, create_remote_thread

이 도구를 사용하면 대량의 Sigma 규칙을 효율적으로 Kibana Detection Rules로 변환하고 관리할 수 있습니다. 