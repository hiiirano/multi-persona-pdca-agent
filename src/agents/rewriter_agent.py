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


def build_rewrite_prompt(content: str, failed_feedbacks: list[dict], platform: str) -> str:
    feedback_text = "\n".join(
        f"- [{fb['persona']}]（{fb['score']}点）: {fb['feedback']}"
        for fb in failed_feedbacks
    )
    return f"""以下のコンテンツを改善してください。

【現在のコンテンツ】
{content}

【不合格だったペルソナからのフィードバック】
{feedback_text}

【プラットフォーム】{platform}

フィードバックを反映した改善版を出力してください。"""
