"""
リライトエージェント（ペルソナのFBを元に改善）
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

REWRITER_SYSTEM_PROMPT = """あなたはコンテンツ改善の専門家です。
複数のペルソナ評価者からのフィードバックを元に、コンテンツをリライトしてください。
改善後のコンテンツのみを出力してください。説明文は不要です。"""


def create_rewriter_agent(model_client: AzureOpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="RewriterAgent",
        model_client=model_client,
        system_message=REWRITER_SYSTEM_PROMPT,
    )


def build_rewrite_prompt(content: str, failed_feedbacks: list[dict], platform: str, language: str = "ja") -> str:
    feedback_text = "\n".join(
        f"- [{fb['persona']}] ({fb['score']}pts): {fb['feedback']}"
        for fb in failed_feedbacks
    )
    lang_instruction = (
        "Output the improved content in English only."
        if language == "en"
        else "改善後のコンテンツのみを日本語で出力してください。"
    )
    return f"""Rewrite the following content based on the persona feedback.

[Current Content]
{content}

[Feedback from failing personas]
{feedback_text}

[Platform] {platform}
[Language] {lang_instruction}"""
