# 设计文档

## 1. 目标
Homework 2：搭建 3 个 Agent 协作的代码审查 Workflow，理解编排、通信、状态管理。

## 2. 架构
```
         ┌─────────────┐
需求 ──> │  CoderAgent  │ ──> 初版代码
         └─────────────┘
                │
                v
         ┌─────────────┐
         │ReviewerAgent│ ──> 问题 JSON
         └─────────────┘
                │
       有问题? ─┼─ 无问题 ─> Done
                │
                v
         ┌─────────────┐
         │ FixerAgent  │ ──> 修复后代码 ──> 回到 Reviewer
         └─────────────┘
```

## 3. Agent 间通信
所有 Agent 共享同一个 `WorkflowState` 对象（线程安全）：
- Coder 写 `current_code`
- Reviewer 写 `review_issues`
- Fixer 读 `current_code` + `review_issues`，覆盖 `current_code`
- Engine 根据 `review_issues` 是否为空决定分支

## 4. 流程控制
- **顺序执行**：Coder -> Reviewer -> Fixer
- **条件分支**：Reviewer 输出空数组 -> Done；非空 -> Fixer
- **循环**：Fixer 修完后回到 Reviewer，最多 3 轮（`max_iterations`）
- **错误处理**：engine.run 包 try/except，失败时 state.status=failed

## 5. 可视化
Flask 提供：
- 页面顶部流程图节点高亮（当前执行到哪个 Agent）
- 左侧实时日志（每秒轮询 /api/state）
- 右侧问题列表
- 下方当前代码

## 6. 与项目一的关系
- 项目一的 ReviewerAgent 审查维度（正确性/安全/性能/可维护/规范）直接迁移到这里
- 项目一是单 Agent ReAct 循环；这里拆成三个单轮 Agent，由 engine 编排
- 虚拟环境 `codeagent_env` 直接复用，新增 flask 依赖
