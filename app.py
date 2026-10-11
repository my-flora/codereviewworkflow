"""Flask Web 可视化：在浏览器里看 Workflow 执行。

启动：python app.py
然后浏览器打开 http://127.0.0.1:5000
"""
import threading
import webbrowser
from flask import Flask, render_template, jsonify, request

from state import WorkflowState
from engine import WorkflowEngine

app = Flask(__name__)

# 全局唯一 state（作业规模下够用；多用户需要换数据库）
state = WorkflowState()
engine = WorkflowEngine(state)
worker_thread = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def api_start():
    global worker_thread
    req = request.json or {}
    requirements = (req.get("requirements") or "").strip()
    if not requirements:
        return jsonify({"ok": False, "msg": "需求不能为空"}), 400
    if state.status in ("coder", "reviewer", "fixer"):
        return jsonify({"ok": False, "msg": "正在运行中"}), 409

    # 重置状态
    state.__init__()
    state.requirements = requirements

    worker_thread = threading.Thread(target=engine.run, args=(requirements,), daemon=True)
    worker_thread.start()
    return jsonify({"ok": True})


@app.route("/api/state")
def api_state():
    return jsonify(state.snapshot())


if __name__ == "__main__":
    # 自动开浏览器
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
