"""Workflow 引擎：编排三个 Agent 的执行流程。

流程（顺序执行 + 条件分支 + 循环）：
  1. coder  根据需求写初版代码
  2. reviewer 审查代码 -> 输出问题列表
  3. 分支判断：
       - 没有问题      -> done
       - 有问题且未达上限 -> fixer 修复 -> 回到 2（循环）
       - 有问题但达到上限 -> done（带警告）
"""
import re
import traceback

from state import WorkflowState, Issue
from agents.coder_agent import CoderAgent
from agents.reviewer_agent import ReviewerAgent
from agents.fixer_agent import FixerAgent


def _extract_code_block(text: str) -> str:
    """从 LLM 输出里抠出 ```python ... ``` 代码块；没有就原样返回。"""
    m = re.search(r"```(?:python)?\s*([\s\S]*?)```", text)
    return m.group(1).strip() if m else text.strip()


class WorkflowEngine:
    def __init__(self, state: WorkflowState):
        self.state = state
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.fixer = FixerAgent()

    # ---- 主流程 ----
    def run(self, requirements: str):
        s = self.state
        s.requirements = requirements
        try:
            self._step_coder()
            self._review_fix_loop()
            s.set_status("done", "完成")
            s.add_log("system", "完成", f"全部流程结束，共迭代 {s.iteration} 轮。")
        except Exception as e:
            s.set_status("failed", f"失败：{e}")
            s.add_log("system", "错误", traceback.format_exc())

    # ---- Step 1: 编码 ----
    def _step_coder(self):
        s = self.state
        s.set_status("coder", "编码 Agent 正在生成代码…")
        s.add_log("coder", "开始编码", f"需求：{s.requirements[:200]}")
        raw = self.coder.write_code(s.requirements)
        s.current_code = _extract_code_block(raw)
        s.add_log("coder", "编码完成", f"生成代码 {len(s.current_code)} 字符。")

    # ---- Step 2-3: 审查-修复循环 ----
    def _review_fix_loop(self):
        s = self.state
        while s.iteration < s.max_iterations:
            s.iteration += 1
            s.set_status("reviewer", f"审查 Agent 正在审查（第 {s.iteration} 轮）…")
            s.add_log("reviewer", "开始审查", f"第 {s.iteration} 轮审查。")
            issues, raw = self.reviewer.review(s.current_code)
            s.review_issues = [Issue(**it) for it in issues if isinstance(it, dict)]
            s.add_log(
                "reviewer",
                "审查完成",
                f"发现 {len(s.review_issues)} 个问题："
                + "; ".join(f"[{i.severity}] {i.location} - {i.description[:40]}" for i in s.review_issues),
            )
            s.final_report = raw

            # 条件分支：没有问题就结束
            if not s.review_issues:
                s.add_log("system", "分支判断", "审查通过，无问题，进入完成态。")
                s.final_code = s.current_code
                return

            # 达到最大迭代次数
            if s.iteration >= s.max_iterations:
                s.add_log("system", "分支判断", f"已达最大迭代 {s.max_iterations} 轮，仍有问题，结束。")
                s.final_code = s.current_code
                return

            # 有问题 -> 修复
            s.set_status("fixer", f"修复 Agent 正在修复（第 {s.iteration} 轮）…")
            issues_text = "\n".join(
                f"- [{i.severity}] {i.location}: {i.description} (建议: {i.suggestion})"
                for i in s.review_issues
            )
            s.add_log("fixer", "开始修复", issues_text[:500])
            raw_fix = self.fixer.fix(s.current_code, issues_text)
            s.current_code = _extract_code_block(raw_fix)
            s.add_log("fixer", "修复完成", f"修复后代码 {len(s.current_code)} 字符，送回审查。")
