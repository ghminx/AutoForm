import json
import re
from textwrap import dedent
from openai import OpenAI

from config import Prompt

class HwpLLMContentGenerator:
    """
    HWP 표 셀 딕셔너리를 입력받아,
    빈칸(C열, E열 등)에만 자연스러운 문장을 자동 생성하는 콘텐츠 생성 AI 모듈
    """

    def __init__(self, model: str = "gpt-5"):
        self.client = OpenAI()
        self.model = model

    def extract_content(self, table: dict, purpose: str = "제안서 작성용") -> dict:
        """
        HWP 표 딕셔너리(table)를 입력받아, 비어 있는 셀에만 내용을 생성.
        purpose(문서 목적)에 따라 문체와 내용이 자동 조정됨.
        """

        system_prompt = Prompt.PROMPT2

        # 유저 입력 구성
        user_prompt = f"""
        목적: {purpose}

        [표 정보]
        {table}
        """

        # GPT-5 Reasoning 모드 호출
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},
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