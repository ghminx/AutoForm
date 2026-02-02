from utils import * 
from config import Config
from hwp_llm_content import HwpLLMContentGenerator


hwp = hwp_open(Config.PATH1, view=Config.HWP_VIEW)



move_to_table(hwp)


# 표 내부 셀 정보 추출 
table_dict = table_extract(hwp)





llm = HwpLLMContentGenerator()

res = llm.extract_content(table_dict, purpose="제안요청서 별지 작성용으로 가상의 데이터를 만들어서 채워줘")

a = {
  "C2": "(주)넥스트웨이브테크 — 데이터 기반 스마트시티·모빌리티 솔루션 전문기업",
  "C3": "이서준 대표이사",
  "C4": "스마트시티 플랫폼, 교통·에너지 데이터 분석, 디지털트윈 구축, 클라우드 운영",
  "C5": "서울특별시 영등포구 여의대로 24, 콘코드타워 17층",
  "C6": "2018년 6월",
  "E6": "02-6210-9300 / contact@nextwavetech.co.kr",
  "C7": "2018년 6월 ~ 2025년 10월 (7년 4개월)",
  "A10": "2018년 6월 — 법인 설립, 스마트시티 데이터 허브 시제품 개발",
  "B10": "2020년 — 서울형 스마트교통 시범사업 수행, 2023년 — 디지털트윈 기반 도시 에너지 최적화 플랫폼 'UrbanTwin' 출시"
}


def insert_cell(hwp, fill_map):
    
    for cell, text in fill_map.items():
        move_to_cell(hwp, cell)
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = text
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        
    
insert_cell(hwp, a)    

