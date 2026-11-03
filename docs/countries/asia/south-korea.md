# ABIZ로 대한민국에서 에이전틱 비즈니스가 되는 방법

*ABIZ 1.1(제안) 안내서입니다. [사양서(SPEC.md, 영어)](../../../SPEC.md)가 기준 문서이며, 이 안내서와 사양서가 다르면 사양서가 우선합니다.*

## 1. 대한민국의 사업자에게 주는 의미

요즘 AI 어시스턴트는 “이 회사의 진짜 웹사이트는 어디인가요?”, “이 가게는 누가 운영하나요?” 같은 질문을 자주 받습니다. ABIZ(Agentic Business Record)는 대한민국의 사업자가 공개 정보를 한 번만, 이런 도구가 읽을 수 있는 형태로 게시할 수 있게 하는 개방형 표준입니다. 사업자가 관리하는 도메인에 짧은 DNS TXT 레코드를 두고, HTTPS로 제공되는 JSON 사업자 레코드를 가리키게 합니다. 이 포인터가 사업자 자신의 DNS에 있으므로, 도구는 비공식 디렉터리나 추측에 기대지 않고 해당 도메인의 관리자가 레코드를 게시했음을 확인할 수 있습니다.

## 2. ABIZ 레코드 게시 방법

### 필수 항목

모든 사업자 레코드에는 다음 다섯 항목이 필요합니다(SPEC 4.1절).

| 항목 | 예시와 규칙 |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | 고객이 아는 공개 상호. 예: `주식회사 한강소프트` |
| `country` | `kr`, ISO 3166-1 alpha-2 코드, 소문자 |
| `identity_host` | `hangangsoft.kr.to.co`, DNS의 `h`와 정확히 일치해야 합니다 |
| `domains` | `["hangangsoft.example"]`, `_abiz`가 있는 도메인을 포함해야 합니다 |

### 선택 항목인 사업자 키 `k`

`k`는 등기 여부와 관계없이 모든 사업자에게 선택 사항입니다. 게시한다면 레코드의 `business_key`와 같아야 하며, 이때 레코드에 `registration_number`도 있어야 합니다. 대한민국의 형식은 다음과 같습니다.

```text
kr-<registration-number>
```

대한민국에서는 하위 행정구역 코드를 쓰지 않습니다. 시·도 코드를 붙이지 마십시오. SPEC 4.2.2절은 미국, 캐나다 주 법인, 아랍에미리트에만 하위 구역을 요구하며 그 밖의 나라에서는 금지합니다.

**사용할 번호:** 법인등기부에 적힌 13자리 법인등록번호(예: `110111-1234567`)입니다. 사업자등록번호(10자리)는 개인사업자에게도 부여되는 세무 번호입니다. 개인사업자는 법인등록번호가 없으며, 사업자등록번호를 키로 써도 되는지는 SPEC에 정해져 있지 않으므로 확실하지 않으면 `k`를 생략하십시오.

**정규화(SPEC 4.2.3절):** 등록 기관이 발급한 그대로의 번호에서 시작해 Unicode NFKC 정규화를 적용하고, 공백, `-`, `.`, `/`, 각종 대시를 없앤 뒤 영문자를 대문자로 바꿉니다. 앞자리 0과 영문 접두어는 유지합니다. 결과는 ASCII 영문자와 숫자로만 이루어져야 하며, 그렇지 않으면 사업자 키를 게시할 수 없으므로 `k`, `business_key`, `registration_number`를 생략합니다.

**예시(가상):** `110111-1234567`는 `1101111234567`이 되므로 `k=kr-1101111234567`입니다. 레코드에는 `"business_key": "kr-1101111234567"`, `"registration_number": "1101111234567"`로 씁니다. 키는 대소문자를 구분하지 않고 비교하며, 표준 형식은 국가 코드 소문자, 번호 대문자입니다.

**개인사업자:** 가진 번호가 주민등록번호처럼 개인 번호뿐이라면 `k`를 게시하지 마십시오. `k`, `business_key`, `registration_number`를 생략해도 레코드는 유효합니다.

### DNS TXT 레코드

도메인의 `_abiz`에 TXT 레코드를 하나만, 공백 없는 간결한 형식으로, `v=abiz1`을 맨 앞에 두어 게시합니다.

```dns
_abiz.hangangsoft.example. 300 IN TXT "v=abiz1;k=kr-1101111234567;h=hangangsoft.kr.to.co;p=LqkTwDsUcRTOL6UWK7Ar37uYedhwVV/a1llJv4N3sLk="
```

위의 `p` 값은 이 페이지를 위해 생성한 일회용 예시 키입니다. 절대 복사하지 마십시오. 자신의 키를 게시하거나 `p`를 생략하십시오. 이 페이지의 모든 이름, 번호, 도메인은 가상입니다.

선택 태그 `k`와 `p`를 뺀 다음 형식도 유효합니다.

```dns
_abiz.hangangsoft.example. 300 IN TXT "v=abiz1;h=hangangsoft.kr.to.co;p=LqkTwDsUcRTOL6UWK7Ar37uYedhwVV/a1llJv4N3sLk="
```

`https://hangangsoft.kr.to.co`에서 `application/json`으로 제공되는 사업자 레코드:

```json
{
  "record_version": "abiz1",
  "business_name": "주식회사 한강소프트",
  "country": "kr",
  "business_key": "kr-1101111234567",
  "registration_number": "1101111234567",
  "identity_host": "hangangsoft.kr.to.co",
  "domains": [
    "hangangsoft.example"
  ],
  "public_key": "LqkTwDsUcRTOL6UWK7Ar37uYedhwVV/a1llJv4N3sLk=",
  "signature": "sG2cFcV3rn9n9KzrJRbKvh75eelbzQbIjhEXkwIUB8192jba+gnUyvR9QVsxl091vtcNA9ANXgR7mmUJOku3DQ=="
}
```

게시 전에 레코드를 확인하려면 이 저장소의 사본에서 참조 검증기를 실행하십시오.

```sh
python scripts/validate.py record.json --domain hangangsoft.example --dns-value 'v=abiz1;k=kr-1101111234567;h=hangangsoft.kr.to.co;p=LqkTwDsUcRTOL6UWK7Ar37uYedhwVV/a1llJv4N3sLk='
```

JSON 레코드는 아무 HTTPS 서버에서 직접 호스팅해도 되고, 호환되는 어떤 제공업체를 이용해도 됩니다. ABIZ는 특정 제공업체를 요구하지 않습니다.

## 3. 제공업체와 MCP 이용

모델 컨텍스트 프로토콜(Model Context Protocol, MCP)은 AI 어시스턴트가 외부 서버의 도구를 호출하고 데이터를 읽을 수 있게 하는 표준 개방형 프로토콜입니다. 사업자 레코드에는 선택 항목 `mcp_server_url`(예약이나 상품 정보 등을 위한 사업자 MCP 서버의 HTTPS 주소)을 넣을 수 있습니다. ABIZ는 그 서버를 보증하지 않으며, 도구는 자체 접근 통제를 적용해야 합니다(SPEC 4.2.6절).

제공업체가 레코드를 호스팅하고 DNS 포인터를 대신 게시할 수도 있습니다. 예를 들어 to.co에 레코드를 둔 대한민국의 등기 법인은 호스트 `hangangsoft.kr.to.co`를 쓰고, DNS 값은 `v=abiz1;k=kr-1101111234567;h=hangangsoft.kr.to.co;p=LqkTwDsUcRTOL6UWK7Ar37uYedhwVV/a1llJv4N3sLk=`가 됩니다. 미등기 사업자는 `hangangsoft-seoul.biz.to.co`처럼 지역명을 넣은 호스트를 쓸 수 있습니다. 다른 호환 제공업체나 자체 서버도 같은 방식으로 작동합니다.

## 4. 키와 서명(ABIZ 1.1)

ABIZ 1.1에는 선택 사항인 서명 키가 추가되었습니다. DNS의 `p` 태그에는 Ed25519 공개 키를 표준 base64로 나타낸 44자(끝에 `=` 하나)를 넣을 수 있습니다(SPEC 3.3.2절). 사업자 또는 사업자를 대리하는 제공업체가 대응하는 개인 키를 보관하고, 다른 사람이 게시된 공개 키로 검증할 수 있는 서명을 만들 수 있습니다. 개인 키는 언제나 사업자의 것이며, 호스팅 제공업체는 사업자가 키를 내보낼 수 있게 해야 합니다.

- `p`는 선택 사항입니다. 있다면 유효한 키여야 합니다. ABIZ 1.0의 예전 16진수 토큰이나 base64url 키 같은 다른 값이 있으면 선언 전체가 무효가 됩니다.
- 현재 키만 게시합니다. 교체하려면 새 키를 `p`에 게시하고, 폐기하려면 `p`를 삭제합니다. ABIZ 1.1에서는 퇴역한 키를 DNS에도 사업자 레코드에도 게시하지 않습니다.
- 키는 도메인의 DNS를 누가 관리하는지를 보여 줄 뿐, 법적 신원을 증명하지 않습니다.

## 5. AI 도구가 보게 되는 정보

레코드를 읽는 호환 도구는 예를 들어 다음과 같은 질문에 답할 수 있습니다.

1. 주식회사 한강소프트의 공식 웹사이트는 어디인가요?
2. 이 사업자의 도메인은 무엇인가요?
3. 사업자가 밝힌 등록번호는 무엇이며 어느 나라의 번호인가요?
4. 무엇을 제공하며 영업시간은 언제인가요?

**한계:** ABIZ가 보여 주는 것은 도메인 관리자가 게시한 내용입니다. 사업자가 법적으로 등기되었다는 것, 번호가 진짜라는 것, AI 서비스나 정부 기관, 제공업체가 추천한다는 것을 증명하지 않습니다. 중요한 경우에는 도구와 사람 모두 공식 등기 정보를 확인해야 합니다.

## 6. 현지 실무 참고

- **등록 기관:** 대법원 인터넷등기소(법인등기)와 국세청(사업자등록). 공식 웹사이트: <https://www.iros.go.kr>.
- **TXT 레코드 추가:** 도메인 등록업체나 DNS 호스팅의 DNS 설정에서 이름 `_abiz`(관리 화면에 따라 `_abiz.yourdomain.kr` 같은 전체 이름), 위의 값, TTL 300초로 TXT 레코드를 추가합니다. `.kr` 도메인도 `.com` 등 다른 도메인과 똑같이 작동합니다. 값은 가능한 한 나누지 말고, `p`는 절대 나누지 마십시오.
- **개인정보:** 「개인정보 보호법」. ABIZ 레코드는 공개 정보입니다. 공유해도 되는 사업 정보만 싣고, 자택 주소나 개인 전화번호는 싣지 마십시오(SPEC 4.3절).

## 7. 더 읽을거리

- [ABIZ 사양(SPEC.md, 영어)](../../../SPEC.md)
- [사업자 레코드 JSON 스키마](../../../schemas/abiz-business-record-v1.schema.json)
- [참조 검증기](../../../scripts/validate.py)
- [ABIZ 국가별 안내: 아시아](index.md)
