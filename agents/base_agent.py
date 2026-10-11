"""BaseAgent：所有 Agent 的父类，封装一次 LLM 调用。

与项目一的 CodeReviewAgent 区别：
- 项目一是 ReAct 循环（工具调用多轮）；
- 这里每个 Agent 只做"输入一段 -> 输出一段"的单次调用，
  由 WorkflowEngine 决定下一个 Agent 是谁。
"""
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL


class BaseAgent:
    name: str = "base"
    system_prompt: str = ""

    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def run(self, user_message: str, temperature: float = 0.2) -> str:
        resp = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""
