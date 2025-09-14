
- name: 이름
- description: 설명
- gimmik: 들어가는 기믹
- difficult: 난이도 (1~10)
- equation: 수식 지정
- notes: 노트
- data: 기타 데이터
- 참고로 notes와 data의 시간이 같으면 data 먼저 처리

예시 (튜토리얼)
```json
{
  "name": "튜토리얼",
  "description": "간단한 설명을 합니다",
  "gimmik": "간단한 덧셈",
  "difficult": 1,
  "speed": 5,
  "equation": [
    [
      [
        {
          "type": "text",
          "text": "0"
        }
      ],
      [
        {
          "type": "text",
          "text": "1"
        }
      ],
      [
        {
          "type": "text",
          "text": "2"
        }
      ],
      [
        {
          "type": "text",
          "text": "3"
        }
      ],
      [
        {
          "type": "text",
          "text": "4"
        }
      ],
      [
        {
          "type": "text",
          "text": "5"
        }
      ],
      [
        {
          "type": "text",
          "text": "6"
        }
      ],
      [
        {
          "type": "text",
          "text": "7"
        }
      ],
      [
        {
          "type": "text",
          "text": "8"
        }
      ],
      [
        {
          "type": "text",
          "text": "9"
        }
      ]
    ],
    [
      [
        {
          "type": "text",
          "text": "0"
        }
      ],
      [
        {
          "type": "text",
          "text": "1"
        }
      ],
      [
        {
          "type": "equation",
          "text": "1+1"
        }
      ],
      [
        {
          "type": "equation",
          "text": "1+2"
        }
      ],
      [
        {
          "type": "equation",
          "text": "2+2"
        }
      ],
      [
        {
          "type": "equation",
          "text": "2+3"
        }
      ],
      [
        {
          "type": "equation",
          "text": "3+3"
        }
      ],
      [
        {
          "type": "equation",
          "text": "3+4"
        }
      ],
      [
        {
          "type": "equation",
          "text": "4+4"
        }
      ],
      [
        {
          "type": "equation",
          "text": "4+5"
        }
      ]
    ]
  ],
  "notes": [
    {
      "time": 1000,
      "num": 5
    }
  ],
  "data": [
    {
      "time": 2000,
      "type": "change_phase",
      "phase": 1
    }
  ]
}
```