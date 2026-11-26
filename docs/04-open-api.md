# Open API

외부 도서 데이터 API의 사용 범위와 약관이다. API 문서·약관은 2026-11-24에 확인했다.

## 사용하는 API

| API | 쓰는 기능 | 용도 | 한도 | 약관 핵심 |
| --- | --- | --- | --- | --- |
| 정보나루 | `loanItemSrch`, `libSrchByBook`, `bookExist` | 후보 목록, 소장 도서관, 대출 가능 여부 | 하루 500건. 서버 IP 등록(최대 3개) 시 30,000건 | 표지(`bookImageURL`)는 영리·AI 이용 금지라 쓰지 않음 |
| 예스24 | `goods/itemDetail`(detail=Y) | 표지, 소개, 목차, 쪽수, 상품 링크 | 기본 키 하루 20,000회·초당 10회 | 출처 표기·상품 상세 링크 의무, 별도 DB 구축 금지 |

- 데이터 시점: 대출 가능 여부는 전날 기준, 소장 정보는 월 단위 갱신. 예스24 `pages`는 빈 값일 수 있다
- 구현 첫 주에 실제 호출로 확인: `loanItemSrch` 조회 기간·JSON 응답 구조·오류 형식(매뉴얼에 없음), HTTPS 지원, 소장·대출 응답 필드, 예스24 `pages` 빈 비율(높으면 NLK 도입)

## 필드 매핑

| 서비스 필드 | 출처 |
| --- | --- |
| 제목·저자·출판사, 표지, 소개·목차, 쪽수 | 예스24 `title`·`cover`·`contentDetail`.bookIntroduction·tableOfContents·`pages` |
| 대출 순위 | 정보나루 `ranking`·`loan_count` |
| KDC | 정보나루 `class_no` |
| 구매 링크 | 예스24 `link` |
| 소장·대출 | 정보나루 `libSrchByBook`·`bookExist` |

## 약관 검토

지금 쓰는 API만 남겼다. 캐시·DB 관련 쟁점은 확장안을 도입할 때 다시 본다.

| 대상 | 이 설계의 방식 | 약관 | 판정 |
| --- | --- | --- | --- |
| 정보나루 조회 | 요청 때 조회만, 저장 안 함 | 이용약관 제12조: 사전 승낙 없이 서비스 이용 외 목적의 복제·제3자 제공 금지 | 조건부: 영리 운영 전 서면 확인 |
| 정보나루 표지 | 쓰지 않음 | 비영리 화면 표시만 허용, 저장·AI 입력 금지 | 준수 |
| 예스24 책 정보 | 요청 때 조회, 저장 안 함 | 제6조③: 일시 저장 허용, **대량·체계적 수집으로 별도 DB 구축 금지** | 준수 |
| 예스24 소개·목차 → LLM | 책 선택·이유의 근거로만 씀 | AI 조항 없음. 내용·의미 왜곡 가공 금지 | 조건부: 이유 검사가 왜곡 방지 장치 |
| 예스24 화면 표시 | 책마다 출처 표기와 상품 링크 | 출처 표기·상품 상세 링크 의무 | 준수 |

## 정보나루 코드표

연령코드

| 코드 | 연령 |
|---|---|
| 0 / 6 / 8 / 14 | 영유아 / 유아 / 초등 / 청소년 |
| 20 / 30 / 40 / 50 | 20대 / 30대 / 40대 / 50대 |
| 60 | 60세 이상 |

KDC 분류체계

| 코드 | 대주제 |
|---|---|
| 0 / 1 / 2 / 3 / 4 | 총류 / 철학 / 종교 / 사회과학 / 자연과학 |
| 5 / 6 / 7 / 8 / 9 | 기술과학 / 예술 / 언어 / 문학 / 역사 |

→ KDC는 3개까지 중복선택 가능

## 제외한 출처

- **네이버 책 검색**: 약관이 검색 결과로 수익을 얻는 것과 AI 입력을 금지
- **카카오 책 검색**: 쪽수·목차·판매지수·평점 없음
- **정보나루 표지(`bookImageURL`)**: 영리 목적 이용·AI 입력 금지

## 출처

- [도서관 정보나루 API 매뉴얼](https://www.data4library.kr/downloadApiManual) · [정보나루 API 활용 안내](https://www.data4library.kr/apiUtilization) · [정보나루 회원가입·약관](https://www.data4library.kr/joinPage) · [정보나루 공지: IP 등록 후 하루 30,000건](https://www.data4library.kr/noticeV?cn=194)
- [예스24 Developers](https://developers.yes24.com) · [예스24 상품 상세 API](https://developers.yes24.com/api-doc/goods-item-detail) · [예스24 호출 한도](https://developers.yes24.com/docs#rate-limit) · [예스24 애드온](https://developers.yes24.com/docs/addon) · [예스24 Open API 약관](https://developers.yes24.com/support/terms) · [예스24 FAQ(상업 이용·DB 축적)](https://developers.yes24.com/support/faq)
- [국립중앙도서관 ISBN 서지정보 API](https://www.nl.go.kr/NL/contents/N31101030500.do) · [국립중앙도서관 사서추천도서 API](https://www.nl.go.kr/NL/contents/N31101030900.do) · [국립중앙도서관 Open API 이용 안내](https://www.nl.go.kr/NL/contents/N31101010000.do) · [국립중앙도서관 ISBN 서지 API(공공데이터포털)](https://www.data.go.kr/data/3078982/openapi.do)
- [네이버 책 검색 API](https://developers.naver.com/docs/serviceapi/search/book/book.md) · [네이버 개발자 약관](https://developers.naver.com/products/terms/) · [카카오 책 검색 API](https://developers.kakao.com/docs/latest/ko/daum-search/dev-guide) · [카카오 쿼터](https://developers.kakao.com/docs/latest/ko/getting-started/quota)
