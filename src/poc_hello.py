"""
Day 1 PoC: Magentic-One Orchestrator + 1エージェントの最小動作確認
実行: python src/poc_hello.py
"""
import asyncio
import os
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

load_dotenv()


async def main():
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-10-21",
        model="gpt-4o",
    )

    agent = AssistantAgent(
        name="ContentAgent",
        model_client=model_client,
        system_message="あなたはSNS投稿の専門家です。与えられたテーマで簡潔な投稿文を生成してください。",
    )

    team = MagenticOneGroupChat([agent], model_client=model_client)

    task = "「AIを使って副業を始める方法」をテーマにX（Twitter）投稿文を1つ生成してください。140文字以内で。"
    print(f"タスク: {task}\n")
    print("=" * 60)

    await Console(team.run_stream(task=task))

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
