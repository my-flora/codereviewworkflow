"""Workflow 共享状态：所有 Agent 读写同一份 state，实现 Agent 间通信。"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import time
import threading


@dataclass
class LogEntry:
    timestamp: str
    agent: str          # coder / reviewer / fixer / system
    phase: str          # 正在做什么
    message: str        # 详细内容

    def to_dict(self):
        return asdict(self)


@dataclass
class Issue:
    severity: str       # 严重 / 中等 / 轻微
    location: str       # 函数名或行号
    description: str    # 问题描述
    suggestion: str     # 修改建议

    def to_dict(self):
        return asdict(self)


@dataclass
class WorkflowState:
    # 输入
    requirements: str = ""

    # 流程数据
    current_code: str = ""
    review_issues: List[Issue] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 3

    # 状态机
    # pending -> coder -> reviewer -> (has_issues? -> fixer -> reviewer : done)
    status: str = "pending"   # pending/coder/reviewer/fixer/done/failed
    status_label: str = "待开始"

    # 日志
    logs: List[LogEntry] = field(default_factory=list)

    # 最终产物
    final_code: str = ""
    final_report: str = ""

    # 线程锁，保证多线程下 Flask 轮询不读到半写状态
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add_log(self, agent: str, phase: str, message: str):
        entry = LogEntry(
            timestamp=time.strftime("%H:%M:%S"),
            agent=agent,
            phase=phase,
            message=message,
        )
        with self._lock:
            self.logs.append(entry)

    def set_status(self, status: str, label: str):
        with self._lock:
            self.status = status
            self.status_label = label

    def snapshot(self) -> Dict[str, Any]:
        """给 Flask UI 轮询用的快照（JSON 可序列化）"""
        with self._lock:
            return {
                "requirements": self.requirements,
                "current_code": self.current_code[:3000],
                "issues": [i.to_dict() for i in self.review_issues],
                "iteration": self.iteration,
                "max_iterations": self.max_iterations,
                "status": self.status,
                "status_label": self.status_label,
                "logs": [l.to_dict() for l in self.logs[-80:]],
                "final_code": self.final_code[:5000],
                "final_report": self.final_report,
            }
