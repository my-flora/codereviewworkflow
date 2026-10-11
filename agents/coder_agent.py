"""编码 Agent：根据需求写出初版代码"""
from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """你是一个专业 Python 编码 Agent。
根据用户给出的需求，写出一份完整、可运行的 Python 代码。

要求：
1. 只输出代码本身，用 ```python ``` 包裹，不要解释。
2. 代码要能直接运行，包含必要的 import 和 __main__ 保护。
3. 命名规范，加必要的注释。
4. 暂时不要过度追求完美——允许有一些可被审查出的小问题（例如边界判断不够、异常处理缺失），
   这样后续审查和修复 Agent 才有东西可做。但不要写出明显语法错误的代码。
"""


class CoderAgent(BaseAgent):
    name = "coder"
    system_prompt = SYSTEM_PROMPT

    def write_code(self, requirements: str) -> str:
        return self.run(requirements, temperature=0.3)
