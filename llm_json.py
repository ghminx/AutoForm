from openai import OpenAI
import json

class LLMExtractor:
    """
    텍스트 마이닝으로 도출된 키워드와 원문을 기반으로
    조사 목적, 대상, 도메인, 주요 변수 등을 구조화된 JSON으로 추출하는 모듈
    """
    def __init__(self, model: str = "gpt-5"):
        self.client = OpenAI()
        self.model = model

    def extract_info(self, table: dict, data: dict) -> dict:
        """
        LLM을 이용한 구조화된 정보 추출
        """
        
        system_prompt = """
            한글(HWP) 표 추출 결과(셀주소-텍스트 딕셔너리)와
            회사 기본정보 딕셔너리를 입력받아,
            각 항목이 들어갈 셀 주소를 자동 매핑하여 fill_map 형태로 반환한다.

            [입력 형식 예시]
            
            [표 정보]
            {
            "table_dict": {
                "A1": "회 사 명", "B1": "", "C1": "대  표  자", "D1": "",
                "A2": "사업분야", "B2": "", "A3": "주    소", "B3": "",
                "A4": "전화번호", "B4": "", "A5": "설립년도", "B5": "",
                "A6": "해당부문", "B6": "", "A7": "주요연혁", "B7": ""
            }
            
            [데이터 정보]
            "company_info": {
                "회사명": "(주)에스티이노베이션",
                "대표자": "권민수",
                "사업분야": "인공지능 기반 자동화 시스템 개발 및 데이터 분석",
                "주소": "(48059) 부산광역시 해운대구 센텀북대로 60, 501호",
                "전화번호": "1588-5086",`
                "설립년도": "2018년 07월",
                "해당부문": "2021년 01월 ~ 2025년 10월 (4년 9개월)",
                "주요연혁": "2018년 법인 설립\n2020년 AI 리서치 플랫폼 구축\n2022년 공공조사 자동화 시스템 개발\n2024년 스마트서비스 지원사업 참여"
            }
            }

            [출력 형식 예시]
            {
            "fill_map": {
                "B1": "(주)에스티이노베이션",
                "D1": "권민수",
                "B2": "인공지능 기반 자동화 시스템 개발 및 데이터 분석",
                "B3": "(48059) 부산광역시 해운대구 센텀북대로 60, 501호",
                "B4": "1588-5086",
                "B5": "2018년 07월",
                "B6": "2021년 01월 ~ 2025년 10월 (4년 9개월)",
                "B7": "2018년 법인 설립\n2020년 AI 리서치 플랫폼 구축\n2022년 공공조사 자동화 시스템 개발\n2024년 스마트서비스 지원사업 참여"
            }
            }

            [지시사항]
            1. table_dict의 셀 텍스트를 기준으로 각 항목이 의미하는 데이터를 추론한다.
            - “회사명”, “대표자”, “사업분야”, “주소”, “전화번호”, “설립년도”, “해당부문”, “주요연혁” 등.
            2. company_info에서 해당 항목의 데이터를 찾아, 비어 있는 셀(B열/D열 등)에 매핑한다.
            3. B열, D열의 빈칸이 모두 채워지도록 구성한다.
            4. 결과는 반드시 JSON 형식으로, "fill_map" 딕셔너리만 출력한다.
            5. 불필요한 설명, 텍스트, 코드블록 표시는 출력하지 않는다.
"""

        user_prompt = f"""
    
        [표 정보]
        {table}
        
        [데이터 정보]
        {data}


        
        """

        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},   # GPT-5 reasoning 모드
            max_output_tokens=1024,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # 모델 출력 파싱
        output_text = response.output_text.strip()

        # JSON 파싱 처리
        try:
            structured_data = json.loads(output_text)
        except json.JSONDecodeError:
            structured_data = {"error": "JSON parsing failed", "raw_output": output_text}

        return structured_data
    
    
    

table_dict =  {
"A1": "회 사 명", "B1": "", "C1": "대  표  자", "D1": "",
"A2": "사업분야", "B2": "", "A3": "주    소", "B3": "",
"A4": "전화번호", "B4": "", "A5": "설립년도", "B5": "",
"A6": "해당부문", "B6": "", "A7": "주요연혁", "B7": "",
}


company_info =  {
"회사명": "(주)에스티이노베이션",
"대표자": "권민수",
"사업분 야": "인공지능 기반 자동화 시스템 개발 및 데이터 분석",
"주소": "(48059) 부산광역시 해운대구 센텀북대로 60, 501호",
"전화번호": "1588-5086",
"설립년도": "2018년 07월",
"해당부문": "2021년 01월 ~ 2025년 10월 (4년 9개월)",
"주요연혁": "2018년 법인 설립\n2020년 AI 리서치 플랫폼 구축\n2022년 공공조사 자동화 시스템 개발\n2024년 스마트서비스 지원사업 참여"
}


llm = LLMExtractor()

res = llm.extract_info(table_dict, company_info)



res['fill_map']