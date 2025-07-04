# WeMeet Sigma to Kibana Detection Rules Converter

Sigma CLI를 사용하여 Sigma 규칙을 Elasticsearch Lucene 쿼리 및 Kibana Detection Rules로 변환하고 관리하는 Python 도구입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [설치 및 설정](#설치-및-설정)
- [사용법](#사용법)
- [추가 필드 기능](#추가-필드-기능)
- [프로젝트 구조](#프로젝트-구조)
- [예제](#예제)
- [테스트](#테스트)
- [문제 해결](#문제-해결)
- [기여하기](#기여하기)

## 🎯 개요

이 프로젝트는 Sigma 규칙을 Kibana Detection Rules로 변환하여 Elastic Stack 환경에서 보안 모니터링을 쉽게 구현할 수 있도록 도와줍니다. Sigma CLI를 완전히 통합하여 안정적이고 정확한 변환을 제공하며, 추가 필드 기능을 통해 Detection Rule을 더욱 세밀하게 커스터마이징할 수 있습니다.

### 주요 특징

- ✅ **Sigma CLI 완전 통합**: 공식 Sigma CLI 도구를 직접 활용
- ✅ **모듈화된 설계**: 각 기능이 명확히 분리된 클래스 구조
- ✅ **CLI 인터페이스**: Click을 사용한 직관적인 명령어 인터페이스
- ✅ **유연한 설정**: 환경변수와 CLI 옵션을 통한 설정 관리
- ✅ **추가 필드 지원**: Detection Rule 생성 시 커스텀 필드 추가 가능
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
- **추가 필드 지원**: Detection Rule 생성 시 커스텀 필드 추가

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

## 🔄 배치 처리 기능

여러 Sigma 규칙을 한 번에 처리할 수 있는 배치 처리 기능을 제공합니다. 단일 파일뿐만 아니라 디렉터리 내의 모든 Sigma 규칙 파일을 처리할 수 있습니다.

### 배치 변환 및 유효성 검사

```bash
# 디렉터리 내 모든 Sigma 규칙을 Detection Rule로 변환
python src/main.py convert-to-detection-rule -i rules_directory/ -o output_directory/

# 디렉터리 내 모든 Sigma 규칙 유효성 검사
python src/main.py validate-rule -i rules_directory/

# 추가 필드와 함께 배치 변환
python src/main.py convert-to-detection-rule \
    -i rules_directory/ \
    -o output_directory/ \
    --additional-fields '{"interval": "10m", "max_signals": 500, "enabled": false}'
```

### 일괄 변환 및 등록

```bash
# 1단계: 변환, 2단계: Kibana에 일괄 등록
python src/main.py convert-and-create-batch \
    -i rules_directory/ \
    -o output_directory/ \
    --pipeline ecs_windows \
    --additional-fields '{"interval": "5m", "max_signals": 1000}'

# 기존 JSON 파일들을 Kibana에 일괄 등록
python src/main.py create-rules-batch -i json_files_directory/
```

### 배치 처리 예제

#### 1. 단일 파일 처리 (기존 방식)
```bash
# 단일 파일 변환
python src/main.py convert-to-detection-rule -i rule.yml -o rule.json

# 단일 파일 유효성 검사
python src/main.py validate-rule -i rule.yml
```

#### 2. 디렉터리 배치 처리 (새로운 방식)
```bash
# 디렉터리 내 모든 .yml 파일 변환
python src/main.py convert-to-detection-rule -i ./sigma_rules/ -o ./detection_rules/

# 디렉터리 내 모든 .yml 파일 유효성 검사
python src/main.py validate-rule -i ./sigma_rules/

# 디렉터리 내 모든 .yml 파일을 변환하고 Kibana에 등록
python src/main.py convert-and-create-batch -i ./sigma_rules/ -o ./temp_output/

# 디렉터리 내 모든 .json 파일을 Kibana에 등록
python src/main.py create-rules-batch -i ./detection_rules/
```

#### 3. 복잡한 배치 처리 예제

```bash
# MITRE ATT&CK 정보와 함께 배치 변환
python src/main.py convert-to-detection-rule \
    -i ./threat_rules/ \
    -o ./output/ \
    --pipeline ecs_windows \
    --additional-fields '{
        "interval": "10m",
        "max_signals": 500,
        "enabled": true,
        "risk_score": 85,
        "threat": [{
            "framework": "MITRE ATT&CK",
            "tactic": {
                "id": "TA0002",
                "name": "Execution"
            },
            "technique": [{
                "id": "T1059.001",
                "name": "PowerShell"
            }]
        }],
        "references": [
            "https://attack.mitre.org/techniques/T1059/001/"
        ]
    }'

# 변환 후 일괄 등록
python src/main.py convert-and-create-batch \
    -i ./threat_rules/ \
    -o ./temp/ \
    --additional-fields '{"interval": "5m", "max_signals": 1000, "enabled": false}'
```

### 배치 처리 기능 상세 설명

#### 지원하는 파일 형식
- **입력**: `.yml`, `.yaml` (Sigma 규칙 파일)
- **출력**: `.json` (Kibana Detection Rule 파일)

#### 디렉터리 처리 규칙
1. **재귀 검색**: 하위 디렉터리까지 모두 검색
2. **파일 필터링**: `.yml`, `.yaml` 확장자만 처리
3. **중복 방지**: 동일한 파일명이 여러 디렉터리에 있어도 한 번만 처리
4. **에러 처리**: 개별 파일 처리 실패 시에도 다른 파일들은 계속 처리

#### 출력 디렉터리 옵션
```bash
# 출력 디렉터리 지정
python src/main.py convert-to-detection-rule -i ./rules/ -o ./output/

# 출력 디렉터리 미지정 (입력 파일과 같은 위치에 생성)
python src/main.py convert-to-detection-rule -i ./rules/
```

#### 배치 처리 진행 상황 표시
```
처리할 Sigma rule 파일 3개 발견:
  • /path/to/rule1.yml
  • /path/to/rule2.yml
  • /path/to/rule3.yml

✅ 변환 완료: rule1.yml → rule1.detection_rule.json
✅ 변환 완료: rule2.yml → rule2.detection_rule.json
✅ 변환 완료: rule3.yml → rule3.detection_rule.json

총 3개 파일 변환 완료
```

#### 일괄 등록 진행 상황 표시
```
등록할 Detection Rule JSON 파일 3개 발견:
  • /path/to/rule1.detection_rule.json
  • /path/to/rule2.detection_rule.json
  • /path/to/rule3.detection_rule.json

✅ 등록 완료: rule1.detection_rule.json → Rule ID: abc123
✅ 등록 완료: rule2.detection_rule.json → Rule ID: def456
✅ 등록 완료: rule3.detection_rule.json → Rule ID: ghi789

📊 일괄 등록 결과:
   - 총 파일 수: 3
   - 성공: 3
   - 실패: 0
```

### 배치 처리 명령어 옵션

#### `convert-to-detection-rule` (배치 변환)
```bash
python src/main.py convert-to-detection-rule [OPTIONS]

Options:
  -i, --input PATH           입력 Sigma rule 파일 또는 디렉터리 경로 [필수]
  -o, --output PATH          출력 JSON 파일 경로 또는 디렉터리 (선택사항)
  --pipeline TEXT            Sigma CLI 파이프라인 (기본값: ecs_windows)
  --sigma-cli-path TEXT      Sigma CLI 명령어 경로
  --additional-fields TEXT   추가 필드를 JSON 형식으로 설정
  --help                     도움말 표시
```

#### `validate-rule` (배치 유효성 검사)
```bash
python src/main.py validate-rule [OPTIONS]

Options:
  -i, --input PATH           입력 Sigma rule 파일 또는 디렉터리 경로 [필수]
  --sigma-cli-path TEXT      Sigma CLI 명령어 경로
  --help                     도움말 표시
```

#### `convert-and-create-batch` (일괄 변환 및 등록)
```bash
python src/main.py convert-and-create-batch [OPTIONS]

Options:
  -i, --input PATH           입력 Sigma rule 파일 또는 디렉터리 경로 [필수]
  -o, --output PATH          출력 디렉터리 (선택사항)
  --pipeline TEXT            Sigma CLI 파이프라인 (기본값: ecs_windows)
  --sigma-cli-path TEXT      Sigma CLI 명령어 경로
  --additional-fields TEXT   추가 필드를 JSON 형식으로 설정
  --kibana-url TEXT          Kibana 서버 URL
  --username TEXT            Kibana 사용자명
  --password TEXT            Kibana 비밀번호
  --help                     도움말 표시
```

#### `create-rules-batch` (JSON 파일 일괄 등록)
```bash
python src/main.py create-rules-batch [OPTIONS]

Options:
  -i, --input PATH           입력 JSON 파일 또는 디렉터리 경로 [필수]
  --kibana-url TEXT          Kibana 서버 URL
  --username TEXT            Kibana 사용자명
  --password TEXT            Kibana 비밀번호
  --help                     도움말 표시
```

## 🔧 추가 필드 기능

추가 필드 기능을 사용하면 Sigma 규칙을 Detection Rule로 변환할 때 기본 필드 외에 추가적인 커스텀 필드를 설정할 수 있습니다.

### 기본 개념

- **기본 필드**: Sigma 규칙에서 자동으로 추출되는 필드들 (title, description, level 등)
- **추가 필드**: 사용자가 직접 설정하는 커스텀 필드들
- **필드 덮어쓰기**: 추가 필드가 기본 필드와 동일한 키를 가질 경우 기본 필드를 덮어씀

### 지원하는 추가 필드

#### 1. 기본 설정 필드
```python
basic_fields = {
    "interval": "10m",           # 규칙 실행 간격
    "max_signals": 500,          # 최대 신호 수
    "enabled": False,            # 규칙 활성화 여부
    "risk_score": 85,            # 위험도 점수 (0-100)
    "from": "now-2h",            # 검색 시작 시간
    "to": "now"                  # 검색 종료 시간
}
```

#### 2. 메타데이터 필드
```python
meta_fields = {
    "meta": {
        "from": "5m",
        "kibana_siem_app_url": "https://kibana.example.com/app/security",
        "custom_field": "custom_value"
    }
}
```

#### 3. MITRE ATT&CK 위협 정보
```python
threat_fields = {
    "threat": [
        {
            "framework": "MITRE ATT&CK",
            "tactic": {
                "id": "TA0002",
                "name": "Execution",
                "reference": "https://attack.mitre.org/tactics/TA0002/"
            },
            "technique": [
                {
                    "id": "T1059.001",
                    "name": "PowerShell",
                    "reference": "https://attack.mitre.org/techniques/T1059/001/"
                }
            ]
        }
    ]
}
```

#### 4. 참조 및 문서화 필드
```python
documentation_fields = {
    "references": [
        "https://docs.microsoft.com/en-us/powershell/scripting/overview",
        "https://attack.mitre.org/techniques/T1059/001/"
    ],
    "false_positives": [
        "Legitimate PowerShell scripts for system administration",
        "Automated deployment tools using PowerShell"
    ],
    "setup": "Enable PowerShell logging and process monitoring",
    "author": ["Security Team", "Threat Intelligence"],
    "license": "DRL"
}
```

### 사용 방법

#### 1. Python 코드에서 사용

```python
from src.sigma_cli_converter import SigmaCLIConverter

# 변환기 초기화
converter = SigmaCLIConverter()

# Sigma 규칙 로드
sigma_rule = {
    "title": "Suspicious PowerShell Execution",
    "id": "12345678-1234-1234-1234-123456789012",
    "description": "Detects suspicious PowerShell execution patterns",
    "logsource": {
        "category": "process_creation",
        "product": "windows"
    },
    "detection": {
        "selection": {
            "CommandLine|contains": "powershell.exe"
        },
        "condition": "selection"
    },
    "level": "high"
}

# 추가 필드 정의
additional_fields = {
    "interval": "10m",
    "max_signals": 500,
    "enabled": False,
    "risk_score": 85,
    "threat": [
        {
            "framework": "MITRE ATT&CK",
            "tactic": {
                "id": "TA0002",
                "name": "Execution",
                "reference": "https://attack.mitre.org/tactics/TA0002/"
            },
            "technique": [
                {
                    "id": "T1059.001",
                    "name": "PowerShell",
                    "reference": "https://attack.mitre.org/techniques/T1059/001/"
                }
            ]
        }
    ],
    "references": [
        "https://attack.mitre.org/techniques/T1059/001/"
    ]
}

# Detection Rule로 변환 (추가 필드 포함)
detection_rule = converter.convert_to_detection_rule(
    sigma_rule, 
    pipeline="ecs_windows",
    additional_fields=additional_fields
)

# 파일로 저장
converter.convert_file(
    "input.yml", 
    output_file="output.json",
    additional_fields=additional_fields
)
```

#### 2. 필드 덮어쓰기 예제

```python
# 기존 필드를 덮어쓰는 추가 필드
override_fields = {
    "name": "Custom Rule Name",           # title 필드 덮어쓰기
    "description": "Custom description",  # description 필드 덮어쓰기
    "severity": "low",                    # level 필드 덮어쓰기
    "rule_id": "custom-rule-id"           # id 필드 덮어쓰기
}

detection_rule = converter.convert_to_detection_rule(
    sigma_rule, 
    additional_fields=override_fields
)
```

#### 3. 복합 추가 필드 예제

```python
# 모든 유형의 추가 필드를 포함한 예제
comprehensive_fields = {
    # 기본 설정
    "interval": "5m",
    "max_signals": 1000,
    "enabled": True,
    "risk_score": 95,
    "from": "now-2h",
    "to": "now",
    
    # 메타데이터
    "meta": {
        "from": "5m",
        "kibana_siem_app_url": "https://kibana.example.com/app/security",
        "custom_field": "custom_value"
    },
    
    # MITRE ATT&CK 정보
    "threat": [
        {
            "framework": "MITRE ATT&CK",
            "tactic": {
                "id": "TA0002",
                "name": "Execution",
                "reference": "https://attack.mitre.org/tactics/TA0002/"
            },
            "technique": [
                {
                    "id": "T1059.001",
                    "name": "PowerShell",
                    "reference": "https://attack.mitre.org/techniques/T1059/001/"
                }
            ]
        }
    ],
    
    # 참조 및 문서화
    "references": [
        "https://docs.microsoft.com/en-us/powershell/scripting/overview",
        "https://attack.mitre.org/techniques/T1059/001/"
    ],
    "false_positives": [
        "Legitimate PowerShell scripts for system administration",
        "Automated deployment tools using PowerShell"
    ],
    "setup": "Enable PowerShell logging and process monitoring",
    "author": ["Security Team", "Threat Intelligence"],
    "license": "DRL"
}
```

### 주의사항

1. **UUID 형식**: Sigma 규칙의 `id` 필드는 반드시 UUID 형식이어야 합니다.
   ```yaml
   id: "12345678-1234-1234-1234-123456789012"  # ✅ 올바른 형식
   id: "suspicious-powershell-execution"        # ❌ 잘못된 형식
   ```

2. **필드 우선순위**: 추가 필드가 기본 필드와 동일한 키를 가질 경우, 추가 필드가 기본 필드를 덮어씁니다.

3. **유효성 검사**: 추가 필드의 값은 Kibana Detection Rules API의 요구사항을 따라야 합니다.

4. **None 값 처리**: `additional_fields=None`으로 설정하면 기본값만 사용됩니다.

### 테스트

추가 필드 기능을 테스트하려면:

```bash
# 추가 필드 테스트 실행
python tests/test_additional_fields.py

# 특정 테스트만 실행
python -m unittest tests.test_additional_fields.TestAdditionalFields.test_01_basic_additional_fields
```

## 📁 프로젝트 구조

```
WeMeet_Project/
├── src/                          # 소스 코드
│   ├── main.py                   # 메인 CLI 인터페이스
│   ├── sigma_cli_manager.py      # Sigma CLI 관리
│   ├── sigma_cli_converter.py    # Sigma 규칙 변환기 (추가 필드 지원)
│   ├── sigma_cli_wrapper.py      # Sigma CLI 래퍼
│   └── kibana_client.py          # Kibana API 클라이언트
├── examples/                     # 예제 파일들
│   ├── suspicious_process_creation.yml
│   ├── network_anomaly.yml
│   └── ...
├── tests/                        # 테스트 코드
│   ├── test_kibana_client.py
│   ├── test_converter.py
│   ├── test_additional_fields.py # 추가 필드 테스트
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

### 3. 추가 필드를 사용한 변환 예제

```python
# Python 스크립트에서 추가 필드 사용
from src.sigma_cli_converter import SigmaCLIConverter

converter = SigmaCLIConverter()

# 추가 필드 정의
additional_fields = {
    "interval": "10m",
    "max_signals": 500,
    "enabled": False,
    "risk_score": 85,
    "threat": [
        {
            "framework": "MITRE ATT&CK",
            "tactic": {
                "id": "TA0002",
                "name": "Execution"
            },
            "technique": [
                {
                    "id": "T1059.001",
                    "name": "PowerShell"
                }
            ]
        }
    ]
}

# 변환 및 저장
converter.convert_file(
    "examples/suspicious_process_creation.yml",
    output_file="custom_rule.json",
    additional_fields=additional_fields
)
```

### 4. 규칙 관리 예제

```bash
# 모든 규칙 조회
python src/main.py list-rules

# 특정 조건으로 필터링
python src/main.py list-rules --filter "alert.attributes.severity:high"

# 페이지별 조회
python src/main.py list-rules --page 1 --per-page 5
```

### 5. 배치 처리 예제

```bash
# 디렉터리 내 모든 Sigma 규칙 변환
python src/main.py convert-to-detection-rule -i ./sigma_rules/ -o ./detection_rules/

# 디렉터리 내 모든 Sigma 규칙 유효성 검사
python src/main.py validate-rule -i ./sigma_rules/

# 추가 필드와 함께 배치 변환
python src/main.py convert-to-detection-rule \
    -i ./threat_rules/ \
    -o ./output/ \
    --additional-fields '{"interval": "10m", "max_signals": 500, "enabled": false}'

# 변환 후 일괄 등록
python src/main.py convert-and-create-batch \
    -i ./sigma_rules/ \
    -o ./temp/ \
    --additional-fields '{"interval": "5m", "max_signals": 1000}'

# 기존 JSON 파일들 일괄 등록
python src/main.py create-rules-batch -i ./detection_rules/
```

### 6. 실제 사용 시나리오 예제

#### 시나리오 1: 새로운 Sigma 규칙 세트 배포
```bash
# 1단계: 규칙 유효성 검사
python src/main.py validate-rule -i ./new_rules/

# 2단계: Detection Rule로 변환
python src/main.py convert-to-detection-rule \
    -i ./new_rules/ \
    -o ./converted_rules/ \
    --additional-fields '{"interval": "10m", "max_signals": 500}'

# 3단계: Kibana에 등록
python src/main.py create-rules-batch -i ./converted_rules/
```

#### 시나리오 2: 한 번에 처리
```bash
# 변환과 등록을 한 번에 처리
python src/main.py convert-and-create-batch \
    -i ./new_rules/ \
    -o ./temp/ \
    --additional-fields '{"interval": "5m", "max_signals": 1000, "enabled": true}'
```

#### 시나리오 3: MITRE ATT&CK 정보 포함
```bash
# 위협 정보와 함께 배치 처리
python src/main.py convert-and-create-batch \
    -i ./attack_rules/ \
    -o ./temp/ \
    --additional-fields '{
        "interval": "10m",
        "max_signals": 500,
        "enabled": true,
        "risk_score": 85,
        "threat": [{
            "framework": "MITRE ATT&CK",
            "tactic": {"id": "TA0002", "name": "Execution"},
            "technique": [{"id": "T1059.001", "name": "PowerShell"}]
        }],
        "references": ["https://attack.mitre.org/techniques/T1059/001/"]
    }'
```

## 🧪 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
python -m unittest discover tests

# 특정 테스트 실행
python -m unittest tests.test_kibana_client.TestKibanaDetectionClient.test_01_create_rule

# 추가 필드 테스트 실행
python tests/test_additional_fields.py

# 배치 처리 기능 테스트 실행
python tests/test_batch_processing.py

# CLI 배치 명령어 테스트 실행
python tests/test_cli_batch_commands.py

# 테스트 파일 직접 실행
python tests/test_kibana_client.py
```

### 배치 처리 테스트

배치 처리 기능은 다음 테스트들을 통해 검증됩니다:

```bash
# 배치 처리 기능 테스트
python tests/test_batch_processing.py

# 테스트 내용:
# - 단일 파일 처리
# - 디렉터리 처리
# - 유효성 검사
# - 일괄 변환
# - 에러 처리
# - 추가 필드 통합

# CLI 배치 명령어 테스트
python tests/test_cli_batch_commands.py

# 테스트 내용:
# - CLI 명령어 실행
# - 디렉터리 배치 처리
# - 일괄 등록 명령어
# - 에러 처리
# - 도움말 명령어
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

#### 4. Sigma 규칙 UUID 오류

```
Error: Sigma rule identifier must be an UUID
```

**해결 방법**: Sigma 규칙의 `id` 필드를 UUID 형식으로 변경
```yaml
# ❌ 잘못된 형식
id: "suspicious-powershell-execution"

# ✅ 올바른 형식
id: "12345678-1234-1234-1234-123456789012"
```

#### 5. 추가 필드 적용 안됨

**확인 사항**:
- `additional_fields` 파라미터가 올바르게 전달되었는지 확인
- 필드 이름이 Kibana Detection Rules API와 호환되는지 확인
- 기본 필드와 동일한 키를 사용할 때 덮어쓰기가 의도된 것인지 확인

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