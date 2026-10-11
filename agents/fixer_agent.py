"""修复 Agent：根据审查报告，输出修复后的完整代码"""
from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """你是一个代码修复 Agent。
输入是：原始代码 + 一份问题清单。
你的任务是：修复清单里列出的所有问题，输出修复后的完整 Python 代码。

要求：
1. 只输出代码本身，用 ```python ``` 包裹，不要解释。
2. 保持原有功能不变，只修复问题。
3. 如果问题里提到"硬编码密钥"，替换为从环境变量读取。
4. 如果提到"裸 except"，改为具体异常捕获。
5. 如果提到"资源未关闭"，改用 with 语句。
6. 如果提到"可变默认参数"，改为 None + 函数内初始化。
7. 修复要彻底，不要留 TODO。
"""


class FixerAgent(BaseAgent):
    name = "fixer"
    system_prompt = SYSTEM_PROMPT

    def fix(self, code: str, issues_text: str) -> str:
        user_msg = (
            f"### 原始代码\n```python\n{code}\n```\n\n"
            f"### 审查发现的问题\n{issues_text}\n\n"
            f"请修复以上所有问题，输出完整代码。"
        )
        return self.run(user_msg, temperature=0.2)
