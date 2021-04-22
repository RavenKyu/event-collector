# Event Collector
1. RestAPI로 이벤트를 수신
1. 수신 받은 이벤트는 미리 설정된 이벤트 목록에 해당되는 것만 비교하여 검사

## Condition
* 요청 받은 데이터는 Condition에 있는 `code` 에서 상태가 평가되어 `boolean` 값 반환 
* 주어진 `code`가 모두 통과 되어야 다음으로 진행
* `_gv` 를 이용하여 글로벌 변수 사용 가능. 

## Actions
* Condition을 모두 통과 이후 실행
* Celery를 이용하여 준비된 함수를 비동기로 실행. (결과는 받지 않음)
* `functions` 실행될 Celery 함수 실행
* `arguments` Celery 에 요청할 함수의 인자값을 생성하기 위한 `code` 리턴 값을 사용



