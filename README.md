# 루미와 한국사2

숙명여고 1학년의 한국사2 기말고사 준비를 위한 비공식 학습 웹사이트.

배포 주소: https://lassenai.github.io/korea-history/

## 구성
- 한국사2 3개 영역 / 20개 단원 / 핵심이론 60절, 연표, 혼동 포인트
- 제공된 EBSi 최소성취수준 학습지 원문 160문항 (객관식 130, 단답형 30)
- 자체 제작 빈칸 20문항, 서술형 20문항: 총 200문항
- 핵심이론 내 OX 20개 및 사건 순서 연습 별도 제공 (문제은행 200문항 집계에서 제외)
- 단원당 1문항, 최대 20분의 객관식 모의고사 3회 (문제은행 재사용, 회차 간 중복 없음)
- 한국어 음성 인식, 기기 음성으로 이론 읽기, 답안 저장, 서술형 자기 점검
- 시험 범위 선택, 오답·북마크, JSON 기록 내보내기·가져오기

## 실행 및 수정
빌드 없는 HTML/CSS/JavaScript 사이트입니다. `npm start` 후 http://127.0.0.1:4173/ 에서 확인합니다.
`content/units.json`을 수정한 뒤 `python scripts/build_data.py`로 data.js를 갱신합니다.
제공 PDF에서 원문을 다시 추출하려면 `python scripts/extract_ebs.py`를 실행합니다 (pymupdf, pillow, pypdf 필요). 소스 PDF는 사용자의 Downloads 폴더에서 읽으며 저장소에 포함하지 않습니다.

검증: `npm run check`, `python tests/verify_content.py`, `python tests/browser_test.py` (로컬 서버와 Playwright 브라우저 설치 필요).

## 출처
사용자 제공: 최소성취수준보장지도 한국사2 강의자료(103쪽)·학습지(62쪽), 개념완성 시험대비 한국사2(23쪽), 1등급 한국사 교재(23쪽).
학평 기출 교재는 한국사1 혼합이므로 원문 문제은행에서는 제외했습니다.
문항의 PDF 실제 쪽수와 인쇄 쪽수, 정답 쪽수는 content/ebs.json에 기록합니다. 이미지 원문의 지도, 밑줄, 사진과 선택지를 보존합니다. 이미지 텍스트도 별도 제공하나 시각 사료의 완전한 대체 텍스트는 아닙니다.
핵심이론과 자체 제작 문항은 자료를 참고해 새로 작성했습니다. 학교/학원 기출은 검증·확보되지 않아 현재 0문항이며 학원 이름이나 연도를 추정해 붙이지 않습니다.

학교 로고: https://sm.sen.hs.kr/dggb/module/file/selectImageView.do?atchFileId=2869473&fileSn=0 (공식 홈페이지, 2026-10-14 확인). 학교의 후원이나 공식 운영을 의미하지 않습니다.
루미: 사용자가 승인한 이미지 생성 캐릭터. built-in image_gen으로 승인 시안에서 투명 배경 단독 자산 제작. 프롬프트: assets/lumi-prompt.txt.
Pretendard 폰트 라이선스: assets/fonts/Pretendard-LICENSE.txt.

## 저장·호환성
학습기록은 `lumi.history.v1` 로컬 저장소에만 저장됩니다. 기기 간 자동 동기화와 계정 시스템은 없습니다. 백업 가져오기는 기존 기록을 교체합니다.
음성 인식은 SpeechRecognition/webkitSpeechRecognition의 ko-KR을 사용합니다. HTTPS와 마이크 권한이 필요하며 브라우저·OS·서비스 상태에 따라 지원 여부가 달라집니다. 브라우저 음성 서비스에 오디오가 전송될 수 있습니다. 사이트는 녹음 파일을 저장하지 않습니다.
읽어주기는 speechSynthesis와 기기 한국어 음성을 사용합니다. 음성 입력과 읽어주기는 동시에 실행되지 않습니다. 미지원 환경에서는 키보드 받아쓰기 안내가 표시됩니다.
WebKit 자동화는 실제 iPhone의 마이크 권한·음성 인식 품질을 보증하지 않습니다. 실제 iPhone Safari 음성 입력은 사용자 기기에서 확인이 필요합니다.

## 배포
main 브랜치 push 시 GitHub Actions가 문법 검사 후 공개 파일만 Pages에 배포합니다. 연구 자료, 로컬 테스트 결과와 원본 PDF는 배포하지 않습니다.


2026-10-14 추가 업데이트: 루미 독서·필기·응원 3종을 화면별로 적용했습니다. 독서 루미는 학교 로고 옆에도 표시합니다. 두각 공식 신청 페이지와 공개 PDF 및 2학기 배포 안내를 출처 화면에 추가했습니다. 확인한 공개 한국사 문항은 한국사1 범위여서 학교·학원 문항을 추가하지 않았습니다(기존 200문항 유지). 자료 주소의 날짜를 출제 연도로 사용하지 않습니다.

AI 이론 듣기: Microsoft ko-KR-SunHiNeural 음성으로 생성한 20개 MP3를 정적으로 제공합니다. 재생·일시정지·탐색·속도 조절을 지원하며 단원 이동 시 중지됩니다. `python scripts/build_audio.py`로 생성합니다(edge-tts 필요). 본문 해시가 같고 파일이 정상인 단원은 재사용하며, 본문이 바뀐 단원은 재생성합니다. assets/audio/manifest.json에는 음성 및 본문 해시를 기록합니다. API 키는 브라우저에 포함하지 않습니다.

전체 객관식 전환: 기존 객관식 130문항을 유지하고 단답형 30·빈칸 20·서술형 20문항을 5지선다로 변형했습니다. content/choice-conversions.json에 검토 가능한 보기와 질문을 기록하고 scripts/build_data.py로 생성합니다. EBSi 원문 이미지와 해설은 보존하며 변형 표시를 함께 제공합니다. 기존 주관식 답안은 학습기록의 legacyWritten에 보존하고, 해당 문항을 새로 풀도록 합니다. 전체 문제 수는 200개입니다. tests/choice_test.py는 전 문항 채점, 기존 기록 이관, 재시도, 북마크, 모의고사 및 모바일 레이아웃을 검증합니다.

카카오톡 링크 미리보기: index.html에 정적 OG 메타데이터를 제공하고 assets/share-kakao-v1.jpg(1200×630 JPEG)를 대표 이미지로 사용합니다. python scripts/build_share_image.py로 재생성할 수 있습니다. 해시 경로는 서버에 전송되지 않으므로 단원별 주소도 공통 사이트 미리보기를 사용합니다. 기존 URL의 카카오 캐시는 카카오 개발자 도구에서 별도로 초기화해야 할 수 있습니다.

상단 교표 개선: 220×42 합성 로고 대신 학교상징 페이지의 219×205 원본 교표와 웹 폰트 학교명을 분리하여 표시합니다. 교표 원본: https://sm.sen.hs.kr/crosseditor/binary/images/2018/05/16/20180516095509850_X2SQ1XV2.png (https://sm.sen.hs.kr/96671/subMenu.do). 화면 교표는 최대 44px로 표시하여 3배율 Retina에서도 원본 픽셀 수가 충분합니다.

핵심이론 시각 강조: content/theory-highlights.json에 단원별 문제풀이 핵심어를 분류하여 관리합니다. 파랑은 인물·단체, 초록은 사건·제도·개념, 주황은 연도·수치입니다. 본문·연표·헷갈리는 포인트에 적용하며 강조 켜기/끄기를 저장합니다. 원문 텍스트와 AI 음원은 변경하지 않습니다. python tests/highlight_test.py로 20개 단원의 텍스트 보존과 표시·재생 호환성을 검증합니다.


## 통합사회2 통합

기본 주소는 통합사회2를 먼저 엽니다. `?subject=social#home` / `?subject=history#home`으로 과목을 전환합니다. 기존 쿼리 없는 `#theory/12`, `#questions` 등의 한국사 링크는 유지됩니다.

- 통합사회2: 3·4·5강, 핵심이론 18주제, 한국어 신경망 음원 3개, 제공 EBSi 자료의 객관식 30문항.
- 문항별 연월·원문 번호를 표시하며, 정답은 제공 PDF 20쪽의 정답표와 대조했습니다. 해설은 별도로 작성했습니다.
- 통합사회 기록은 `lumi.social.v1`, 한국사는 기존 `lumi.history.v1`을 사용합니다. 백업·복원과 초기화는 현재 과목에만 적용됩니다.
- 통합사회 모의고사는 전체 범위 기준 3회 × 10문항으로, 30문항을 중복 없이 나눕니다.
- `content/social-units.json`, `content/social-explanations.json`, `content/social-questions.json`은 검토 가능한 콘텐츠입니다. 원본 PDF는 저장소에 포함하지 않습니다.
- 재생성: `python scripts/prepare_social_units.py`, `python scripts/build_social.py`, `python scripts/build_social_audio.py`. 원본 문제 PDF는 사용자 Downloads 폴더가 필요합니다. `prepare_social_units.py`는 topics JSON에 보완 개념을 합칩니다.
- 검증: 로컬 4173 서버 실행 후 `python tests/social_test.py`, 기존 `tests/choice_test.py`, `tests/highlight_test.py`.
