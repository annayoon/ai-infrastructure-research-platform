# AI Infrastructure Research Portal

> Bilingual README: Korean / English  
> 알래스카 기반 AI 인프라, 데이터센터, 전력, 냉각, 광통신, 서비스 모델, APAC·한국 고객군 리서치를 위한 내부 리서치 포털입니다.

---

## 1. 프로젝트 개요 / Project Overview

### 한국어

**AI Infrastructure Research Portal**은 알래스카 기반 AI 데이터센터 및 Advanced Technology & Manufacturing Campus 사업 검토를 위해 구축한 리서치 포털입니다.

이 포털은 공개 자료(OSINT)를 수집·분류·요약하여 다음과 같은 의사결정을 지원합니다.

- 알래스카 AI 데이터센터 입지 경쟁력 검토
- 전력, 송전, 냉각, 수자원, 광통신, Arctic Fiber 관련 근거자료 정리
- 서비스 모델별 장단점 검토
- APAC 및 한국 고객군 대상 가치 제안 검토
- 보고서 작성용 Evidence Matrix 기반 근거 관리
- Original Source URL 기반 원문 확인

현재 포털은 Streamlit 기반으로 구현되어 있으며, Render를 통해 웹 서비스로 배포됩니다.

### English

**AI Infrastructure Research Portal** is a research portal built to support strategic assessment of an Alaska-based AI data center and Advanced Technology & Manufacturing Campus initiative.

The portal collects, classifies, and organizes public-source research materials to support:

- Alaska AI data center location competitiveness analysis
- Evidence tracking for power, transmission, cooling, water, fiber, and Arctic connectivity
- Service model evaluation
- APAC and Korean customer target analysis
- Evidence Matrix-based report writing
- Original source URL tracking

The portal is built with Streamlit and deployed as a web service on Render.

---

## 2. 주요 기능 / Key Features

### 한국어

- **Overview**
  - 전체 Source 수, Original URL 수, New Sources, Latest Updated 자료 수 확인
- **Source Index**
  - 수집 자료 목록 확인
  - 카테고리별 필터링
  - URL 보유 자료만 보기
  - 신규 자료만 보기
  - 최신 업데이트 자료만 보기
  - Original Source 링크 열기
- **Corpus Search**
  - `corpus_text`에 추출된 텍스트 자료 내부 검색
- **File Preview**
  - 로컬 텍스트 파일 미리보기
- **Data Health Check**
  - Missing URLs, Missing Titles, Missing Categories 확인
  - Update Batch Summary 확인

### English

- **Overview**
  - Shows total sources, original URL count, new sources, and latest updated sources
- **Source Index**
  - Browse collected research sources
  - Filter by category
  - Show only rows with URLs
  - Show only newly added sources
  - Show only latest updated sources
  - Open original source links
- **Corpus Search**
  - Search extracted text files under `corpus_text`
- **File Preview**
  - Preview local extracted text files
- **Data Health Check**
  - Check missing URLs, missing titles, missing categories
  - Review update batch summary

---

## 3. 현재 리서치 범위 / Research Scope

### 한국어

현재 포털은 다음 주제를 중심으로 자료를 관리합니다.

- Alaska AI Data Center
- Alaska Railbelt 전력·송전 인프라
- 알래스카 기후 기반 냉각 이점
- Cold Climate Cooling / Free Cooling / PUE
- 수자원 및 냉각 리스크
- Arctic Fiber / Subsea Cable / Route Diversity
- LNG 및 에너지 투자
- Port MacKenzie 및 산업·제조 캠퍼스
- Hyperscaler / GPU Cloud / Neocloud
- APAC 고객군 분석
- 한국 고객 가치 제안
- 백업·DR·보안 컴퓨트
- 제조 데이터 워크로드
- 클라우드 전용 연결성
- 서비스 모델별 장단점 검토

### English

The current research scope includes:

- Alaska AI data center opportunity
- Alaska Railbelt power and transmission infrastructure
- Alaska climate-based cooling advantage
- Cold climate cooling, free cooling, and PUE
- Water resources and cooling risk
- Arctic fiber, subsea cable, and route diversity
- LNG and energy investment
- Port MacKenzie and industrial/manufacturing campus development
- Hyperscalers, GPU cloud, and neocloud providers
- APAC customer target analysis
- Korean customer value proposition
- Backup, disaster recovery, and secure compute
- Manufacturing data workloads
- Cloud interconnect
- Service model evaluation

---

## 4. 주요 카테고리 / Key Categories

| Category | Description |
|---|---|
| `power` | Power generation, transmission, grid, electricity demand |
| `data_center` | Data center market, colocation, AI data center |
| `AI` | AI infrastructure and AI compute demand |
| `climate_advantage` | Alaska climate advantage for data center cooling |
| `cold_climate_cooling` | Free cooling and cold-climate data center cooling |
| `energy_efficiency` | PUE, cooling efficiency, data center energy efficiency |
| `fiber` | Fiber network, Arctic cable, subsea cable, connectivity |
| `subsea_telecom_partnership` | Subsea cable and telecom partnership models |
| `hyperscaler_partnership` | Hyperscaler, GPU cloud, long-term infrastructure partnership |
| `cloud_interconnect` | AWS Direct Connect, Azure ExpressRoute, Google Cloud Interconnect |
| `manufacturing_data_workload` | Manufacturing data, IIoT, quality data, industrial analytics |
| `asia_enterprise_na_expansion` | APAC companies expanding into North America |
| `apac_customer_target` | Korea, Japan, Taiwan customer candidates |
| `korea_ai_demand` | Korean AI/GPU infrastructure demand |
| `korea_data_center_constraints` | Korean data center power, land, and concentration constraints |
| `korea_gpu_cloud` | Korean GPU cloud and AI cloud providers |
| `korea_sovereign_ai` | Sovereign AI and public AI infrastructure in Korea |
| `korea_dr_backup` | Backup, DR, and geo-redundant infrastructure for Korean customers |
| `korea_latency_fit` | Workload latency suitability for Korean customers |
| `korea_manufacturing_na_expansion` | Korean manufacturers expanding into North America |
| `regulatory_security` | Data sovereignty, subsea cable security, national security issues |

---

## 5. 데이터 구조 / Data Structure

```text
.
├── app.py
├── requirements.txt
├── metadata/
│   ├── source_index.csv
│   ├── url_candidates.csv
│   ├── url_registry.csv
│   ├── download_manifest.csv
│   ├── summaries.csv
│   ├── insights.csv
│   └── knowledge_graph.csv
├── queries/
│   └── expanded_topic_queries.csv
├── scripts/
│   ├── approve_url_candidates.py
│   ├── download_from_registry.py
│   ├── extract_from_manifest.py
│   ├── update_source_index_from_manifest.py
│   ├── summarize.py
│   ├── insight_extraction.py
│   ├── knowledge_graph.py
│   └── ...
├── downloads/
└── corpus_text/
```

> Note: `downloads/` and `corpus_text/` may be excluded from Git depending on `.gitignore`.  
> 참고: `downloads/`와 `corpus_text/`는 `.gitignore` 설정에 따라 Git에 포함되지 않을 수 있습니다.

---

## 6. 핵심 데이터 파일 / Core Data Files

### `metadata/url_candidates.csv`

수집 후보 URL 목록입니다.

| Column | Description |
|---|---|
| `url` | Candidate source URL |
| `title` | Source title |
| `domain` | Source domain |
| `country` | Country or region |
| `category` | Research category |
| `subcategory` | Subcategory |
| `query` | Search query or source rationale |
| `priority` | Priority level |
| `review_status` | `approved` if selected for ingestion |
| `notes` | Notes |

### `metadata/url_registry.csv`

승인된 URL 목록입니다.  
`approve_url_candidates.py`를 통해 `url_candidates.csv`의 approved 항목이 반영됩니다.

### `metadata/download_manifest.csv`

URL 다운로드 결과를 기록합니다.

| Column | Description |
|---|---|
| `source_id` | Generated source ID |
| `url` | Source URL |
| `status` | Download status |
| `file_type` | html, pdf, etc. |
| `download_path` | Local downloaded file path |
| `corpus_path` | Extracted text file path |
| `extract_status` | Extraction status |

### `metadata/source_index.csv`

포털에서 실제로 표시되는 최종 인덱스 파일입니다.

주요 컬럼:

| Column | Description |
|---|---|
| `source_id` | Source ID |
| `title` | Source title |
| `domain` | Source domain |
| `country` | Country or region |
| `category` | Research category |
| `file_path` | Local corpus path |
| `url` | Original source URL |
| `summary` | Summary |
| `keywords` | Keywords |
| `insights` | Key insights |
| `added_at` | Date added |
| `update_batch` | Update batch name |
| `is_new` | Whether the source is newly added |
| `is_latest_update` | Whether the source belongs to the latest update batch |

---

## 7. 로컬 실행 방법 / Local Run

```bash
cd ~/alaska_aidc_research
source .venv/bin/activate
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 8. 리서치 자료 업데이트 절차 / Source Update Workflow

새 자료를 추가할 때는 아래 순서로 진행합니다.

```bash
# 1. 후보 URL 승인 항목을 Registry에 반영
python3 scripts/approve_url_candidates.py

# 2. Registry 기준 URL 다운로드
python3 scripts/download_from_registry.py

# 3. HTML/PDF를 텍스트로 추출
python3 scripts/extract_from_manifest.py

# 4. Source Index 갱신
UPDATE_BATCH="YYYY-MM-DD-topic-name" python3 scripts/update_source_index_from_manifest.py
```

예:

```bash
UPDATE_BATCH="2026-05-26-korea-customer-benefit" python3 scripts/update_source_index_from_manifest.py
```

To add new research sources, follow the same workflow:

```bash
python3 scripts/approve_url_candidates.py
python3 scripts/download_from_registry.py
python3 scripts/extract_from_manifest.py
UPDATE_BATCH="YYYY-MM-DD-topic-name" python3 scripts/update_source_index_from_manifest.py
```

---

## 9. Git 운영 절차 / Git Workflow

```bash
git checkout main
git pull origin main
git checkout -b feature-branch-name
```

작업 후:

```bash
git status
git add queries/expanded_topic_queries.csv
git add metadata/url_candidates.csv
git add metadata/url_registry.csv
git add metadata/download_manifest.csv
git add metadata/source_index.csv
git add app.py
git add scripts/update_source_index_from_manifest.py

git commit -m "Describe update"
git push -u origin feature-branch-name
```

main에 반영:

```bash
git checkout main
git pull origin main
git merge feature-branch-name
git push origin main
```

---

## 10. Render 배포 / Render Deployment

Render는 `main` 브랜치 기준으로 자동 배포됩니다.

배포 후 포털 숫자가 반영되지 않으면 Render에서 다음을 실행합니다.

```text
Manual Deploy → Clear build cache & deploy
```

배포 후 브라우저에서 강력 새로고침합니다.

```text
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + R
```

---

## 11. 보고서 작성 활용 / Report Writing Usage

포털은 보고서 작성 시 다음과 같이 활용합니다.

1. **Source Index**에서 관련 카테고리 필터 적용
2. **Only rows with URL**로 원문 확인 가능한 자료 우선 검토
3. **Only new sources**로 최근 추가 자료 확인
4. **Only latest update**로 최신 배치 자료 확인
5. Evidence Matrix에 주요 근거 매핑
6. 보고서 본문에 주장 → 근거 → 전략적 의미 → 리스크 구조로 반영

For report writing:

1. Filter relevant categories in **Source Index**
2. Use **Only rows with URL** to prioritize verifiable sources
3. Use **Only new sources** to review newly added materials
4. Use **Only latest update** to review the most recent update batch
5. Map key sources into the Evidence Matrix
6. Write report sections using the structure: claim → evidence → strategic meaning → risk/caveat

---

## 12. Current Status

현재 포털은 다음 분석을 지원합니다.

- 알래스카 AI 데이터센터 입지 검토
- 알래스카 기후 기반 냉각 이점 검토
- 전력·송전·Railbelt 인프라 검토
- Arctic Fiber 및 해저케이블 기회 검토
- APAC 타깃 고객군 분석
- 서비스 모델별 장단점 검토
- 한국 고객 가치 제안 검토
- Evidence Matrix 기반 보고서 작성

The portal currently supports:

- Alaska AI data center location assessment
- Climate-based cooling advantage analysis
- Power, transmission, and Railbelt infrastructure review
- Arctic fiber and subsea cable opportunity analysis
- APAC customer target analysis
- Service model evaluation
- Korean customer value proposition analysis
- Evidence Matrix-based report writing

---

## 13. Notes and Limitations

- 일부 자료는 자동 다운로드 시 `403`, `404`, `failed`가 발생할 수 있습니다.
- `Original Source`가 있는 자료를 보고서 근거로 우선 활용하는 것을 권장합니다.
- `downloads/`와 `corpus_text/`는 배포 환경에 포함되지 않을 수 있으므로 Render에서는 Source Index와 Original URL 중심으로 사용하는 것이 안정적입니다.
- 포털은 실시간 검색 엔진이 아니라, 검토된 URL 기반 리서치 아카이브입니다.

- Some sources may return `403`, `404`, or `failed` during automated download.
- Sources with `Original Source` URLs should be prioritized for formal report evidence.
- `downloads/` and `corpus_text/` may not be included in the deployment environment, so the Render version is best used as a source index and original URL portal.
- This portal is not a real-time search engine; it is a curated research archive based on reviewed URLs.

---

## 14. Usage

This project is intended for internal research, market validation, strategic analysis, and report preparation.

Please verify original source materials before using them in formal external reports or proposals.
