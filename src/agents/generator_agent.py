"""
コンテンツ生成エージェント（初稿生成）
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

PLATFORM_FORMATS = {
    "x": "X（Twitter）投稿文。140文字以内のシングルポストか、3〜5ツイートのスレッド形式。",
    "note": "note記事。見出し（##）+ 本文 + CTA（行動呼びかけ）の構成。800〜1200文字程度。",
    "kdp": "KDP（Amazon電子書籍）の商品説明文。400文字程度。購買を促す表現で。",
}

GENERATOR_SYSTEM_PROMPT = """あなたはSNS・コンテンツマーケティングの専門家です。
与えられたテーマとプラットフォームに合わせて、魅力的なコンテンツの初稿を生成してください。
ペルソナ（一般層・副業志向・技術層）の全員に刺さるような表現を意識してください。
コンテンツのみを出力し、説明文や前置きは不要です。"""


def create_generator_agent(model_client: AzureOpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="GeneratorAgent",
        model_client=model_client,
        system_message=GENERATOR_SYSTEM_PROMPT,
    )


def build_generation_prompt(theme: str, platform: str) -> str:
    fmt = PLATFORM_FORMATS.get(platform, PLATFORM_FORMATS["x"])
    return f"""テーマ：「{theme}」
プラットフォーム：{platform}
形式：{fmt}

上記の条件でコンテンツを生成してください。"""
