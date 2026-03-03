"""
Multi-Persona Content PDCA Agent — メインオーケストレーター
"""
import asyncio
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from agents.generator_agent import create_generator_agent, build_generation_prompt
from agents.persona_agent import create_persona_agents, parse_score_response
from agents.rewriter_agent import create_rewriter_agent, build_rewrite_prompt
from config import MAX_REWRITE_ITERATIONS, PASS_SCORE_THRESHOLD

load_dotenv()


@dataclass
class EvalResult:
    persona: str
    score: int
    verdict: str
    feedback: str


async def evaluate_content(content: str, persona_agents, model_client) -> list[EvalResult]:
    """3ペルソナを並列評価する"""
    async def eval_one(agent):
        response = await agent.on_messages(
            [TextMessage(content=content, source="user")],
            cancellation_token=None,
        )
        parsed = parse_score_response(response.chat_message.content)
        return EvalResult(
            persona=agent.name,
            score=parsed.get("score", 0),
            verdict=parsed.get("verdict", "FAIL"),
            feedback=parsed.get("feedback", ""),
        )

    return list(await asyncio.gather(*[eval_one(a) for a in persona_agents]))


async def run_pdca(theme: str, platform: str = "x") -> dict:
    """PDCAループのメイン処理"""
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-10-21",
        model="gpt-4o",
    )

    generator = create_generator_agent(model_client)
    personas = create_persona_agents(model_client)
    rewriter = create_rewriter_agent(model_client)

    # Step 1: 初稿生成
    print(f"\n[Generator] テーマ「{theme}」({platform}) の初稿を生成中...")
    gen_prompt = build_generation_prompt(theme, platform)
    gen_response = await generator.on_messages(
        [TextMessage(content=gen_prompt, source="user")],
        cancellation_token=None,
    )
    content = gen_response.chat_message.content
    print(f"\n--- 初稿 ---\n{content}\n")

    # Step 2: PDCAループ
    history = []
    for iteration in range(MAX_REWRITE_ITERATIONS + 1):
        print(f"[評価] ループ {iteration + 1}/{MAX_REWRITE_ITERATIONS + 1}")
        results = await evaluate_content(content, personas, model_client)

        for r in results:
            print(f"  {r.persona}: {r.score}点 ({r.verdict}) — {r.feedback}")

        history.append({"iteration": iteration, "content": content, "results": results})

        failed = [r for r in results if r.score < PASS_SCORE_THRESHOLD]
        if not failed:
            print("\n✅ 全ペルソナ合格！")
            break

        if iteration >= MAX_REWRITE_ITERATIONS:
            print(f"\n⚠️ {MAX_REWRITE_ITERATIONS}回リライト後も未達。現在のベストを使用。")
            break

        # Step 3: リライト
        print(f"\n[Rewriter] {len(failed)}ペルソナのFBを元にリライト中...")
        failed_feedbacks = [{"persona": r.persona, "score": r.score, "feedback": r.feedback} for r in failed]
        rewrite_prompt = build_rewrite_prompt(content, failed_feedbacks, platform)
        rw_response = await rewriter.on_messages(
            [TextMessage(content=rewrite_prompt, source="user")],
            cancellation_token=None,
        )
        content = rw_response.chat_message.content
        print(f"\n--- リライト後 ---\n{content}\n")

    await model_client.close()

    final_results = history[-1]["results"]
    return {
        "final_content": content,
        "scores": {r.persona: r.score for r in final_results},
        "iterations": len(history),
        "all_passed": all(r.score >= PASS_SCORE_THRESHOLD for r in final_results),
    }


if __name__ == "__main__":
    result = asyncio.run(run_pdca("AIを使って副業を始める方法", platform="x"))
    print("\n" + "=" * 60)
    print("【最終出力】")
    print(result["final_content"])
    print(f"\nスコア: {result['scores']}")
    print(f"ループ回数: {result['iterations']}")
    print(f"全員合格: {result['all_passed']}")
