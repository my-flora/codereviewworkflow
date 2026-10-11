"""CLI 入口（无 UI 模式）：直接跑 workflow，结果打到终端。

用法：
    python main.py "写一个 Python 函数，接收列表返回偶数平均值"
    python main.py        # 交互输入需求
"""
import sys
from state import WorkflowState
from engine import WorkflowEngine


def main():
    if len(sys.argv) > 1:
        requirements = " ".join(sys.argv[1:])
    else:
        requirements = input("请输入需求 > ").strip()

    if not requirements:
        print("需求不能为空")
        return

    state = WorkflowState()
    engine = WorkflowEngine(state)
    engine.run(requirements)

    snap = state.snapshot()
    print("\n" + "=" * 60)
    print(f"状态: {snap['status_label']}  共迭代 {snap['iteration']} 轮")
    print("=" * 60)
    print("\n--- 日志 ---")
    for l in snap["logs"]:
        print(f"[{l['timestamp']}] [{l['agent']}] {l['phase']}: {l['message']}")

    print("\n--- 审查报告 ---")
    print(snap["final_report"] or "(无)")

    print("\n--- 最终代码 ---")
    print(snap["final_code"] or "(无)")


if __name__ == "__main__":
    main()
