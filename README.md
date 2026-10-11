# Code Review Multi-Agent Workflow

Homework 2：2-3 个 Agent 协作的代码审查流程。

## Agent 组成
| Agent | 职责 |
|---|---|
| 编码 Agent (Coder) | 根据需求写初版 Python 代码 |
| 审查 Agent (Reviewer) | 复用项目一的审查能力，输出结构化问题 JSON |
| 修复 Agent (Fixer) | 根据问题清单修复代码，送回审查 |

## 流程
```
需求 -> Coder -> Reviewer -> 有问题?
                              ├ 否 -> Done
                              └ 是 -> Fixer -> 回到 Reviewer (最多 3 轮)
```

## 功能覆盖
- [x] 至少 2 个 Agent 协作（实际 3 个）
- [x] Agent 间通过共享 `WorkflowState` 通信
- [x] 顺序执行 + 条件分支（有/无问题）+ 循环（修复后重审）
- [x] Web 可视化编排界面（Flask + 流程图 + 实时日志）
- [x] 执行日志与状态追踪
- [x] 错误处理（异常捕获、失败状态）

## 快速开始
```bash
# 方式一：可视化界面（推荐）
python app.py
# 浏览器自动打开 http://127.0.0.1:5000

# 方式二：命令行
python main.py "写一个函数，接收列表返回偶数平均值"
```

## 项目结构
```
├── app.py            # Flask Web 可视化入口
├── main.py           # 命令行入口
├── engine.py         # Workflow 编排引擎（顺序/分支/循环）
├── state.py          # 共享状态 + 日志
├── config.py         # LLM 配置
├── .env              # API Key
├── agents/
│   ├── base_agent.py    # LLM 调用基类
│   ├── coder_agent.py   # 编码 Agent
│   ├── reviewer_agent.py # 审查 Agent（复用项目一）
│   └── fixer_agent.py   # 修复 Agent
└── templates/index.html # 可视化前端
```

## 虚拟环境
复用项目一的 `codeagent_env`，只需额外装 flask：
```
D:\Software Project Management\CodeReviewAgent\codeagent_env\Scripts\activate
pip install flask
```
