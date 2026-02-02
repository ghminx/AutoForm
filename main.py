from utils import * 
from config import Config
from hwp_llm_mapper import HwpLLMFieldMapper



hwp = hwp_open(Config.PATH, view=Config.HWP_VIEW)

move_to_table(hwp)

table_dict = {}

move_to_cell(hwp, "A1")

while True:

    current_pos = hwp.KeyIndicator()[-1][1:].split(")")[0]
    get_text(hwp)
    
    
    table_dict[current_pos] = get_text(hwp)
    
    hwp.HAction.Run("TableRightCell")
    
    next_pos = hwp.KeyIndicator()[-1][1:].split(")")[0]
     
    if current_pos == next_pos:
        break
     
    
company_info = {
    "회사명": "(주)에스티이노베이션",
    "대표자": "권민수",
    "사업분야": "인공지능 기반 자동화 시스템 개발 및 데이터 분석",
    "주소": "(48059) 부산광역시 해운대구 센텀북대로 60, 501호",
    "전화번호": "1588-5086",
    "설립년도": "2018년 07월",
    "해당부문": "2021년 01월 ~ 2025년 10월 (4년 9개월)",
    "주요연혁": (
        "2018년 법인 설립\n"
        "2020년 AI 리서치 플랫폼 구축\n"
        "2022년 공공조사 자동화 시스템 개발\n"
        "2024년 스마트서비스 지원사업 참여"
    )
}

llm = HwpLLMFieldMapper()
result = llm.extract_info(table_dict, company_info)

fill_map = result.get("fill_map", {})


fill_map



for cell, text in fill_map.items():
    move_to_cell(hwp, cell)
    hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
    hwp.HParameterSet.HInsertText.Text = text
    hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

