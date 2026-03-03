"""
3ペルソナ評価エージェント（General / SideBiz / Tech）
"""
import json
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def create_persona_agents(model_client: AzureOpenAIChatCompletionClient) -> list[AssistantAgent]:
    """3つのペルソナ評価エージェントを生成して返す"""
    personas = [
        ("PersonaAgent_General", "persona_general.txt"),
        ("PersonaAgent_SideBiz", "persona_sidebiz.txt"),
        ("PersonaAgent_Tech",    "persona_tech.txt"),
    ]
    return [
        AssistantAgent(
            name=name,
            model_client=model_client,
            system_message=_load_prompt(prompt_file),
        )
        for name, prompt_file in personas
    ]


def parse_score_response(response_text: str) -> dict:
    """エージェントのレスポンスからJSON部分を抽出してパース"""
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"score": 0, "verdict": "FAIL", "feedback": "レスポンスのパースに失敗しました"}
    try:
        return json.loads(response_text[start:end])
    except json.JSONDecodeError:
        return {"score": 0, "verdict": "FAIL", "feedback": "JSONパースエラー"}
