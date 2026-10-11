"""审查 Agent：复用项目一的审查能力，输出结构化 JSON 问题列表"""
import json
import re
from agents.base_agent import BaseAgent


SYSTEM_PROMPT = """你是一个严格的代码审查 Agent。
阅读给出的 Python 代码，从以下维度找问题：
- 正确性：逻辑错误、边界条件、空值/空列表处理、除零
- 安全性：SQL 注入、命令注入、硬编码密钥、pickle 反序列化
- 性能：O(n^2) 重复计算、不必要的循环
- 可维护性：命名不规范、超长函数、可变默认参数、裸 except
- 规范性：资源未关闭、缺少异常处理、缺少 __main__ 保护

输出格式（非常重要）：
只输出一个 JSON 数组，不要输出任何其他文字。每个元素结构如下：
[
  {
    "severity": "严重" | "中等" | "轻微",
    "location": "函数名 或 大致行号",
    "description": "问题是什么",
    "suggestion": "怎么改"
  }
]
如果代码没有任何问题，输出 [] 即可。不要编造问题。
"""


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    system_prompt = SYSTEM_PROMPT

    def review(self, code: str):
        """返回 (issues_list, raw_text)。issues_list 元素是 dict。"""
        raw = self.run(f"请审查以下代码：\n\n```python\n{code}\n```", temperature=0.1)
        issues = self._parse_issues(raw)
        return issues, raw

    @staticmethod
    def _parse_issues(raw: str):
        # 提取 ```json ... ``` 或直接抓 [ ... ]
        m = re.search(r"\[[\s\S]*\]", raw)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            return []
        return []
