import gradio as gr
import requests
import json

# ============================================================
# 配置区
# ============================================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

# ============================================================
# 口播稿改写 Prompt
# ============================================================
PROMPT_TEMPLATE = """
你是口播稿改写专家。请把以下长文改写成适合视频口播的脚本。

改写规则：
1. 不改观点，不改结构，保留原文的逻辑顺序。
2. 口语化，短句优先，长句拆短。
3. 每段 1-2 分钟，约 200-300 字。
4. 保留情绪词和语气，不要抹平。
5. 关键句后加（停顿）或（长停顿）。
6. 用 Markdown 分块输出，每块给小标题。
7. 不写"大家好""今天我们来聊聊"这种套话。
8. 不替原文补充新观点。

原文：
{text}

请直接输出改写后的口播稿，不要解释。
"""

# ============================================================
# 核心函数：长文 → 口播稿
# ============================================================
def to_oral_script(text):
    if not text.strip():
        return "请先粘贴长文。"

    prompt = PROMPT_TEMPLATE.format(text=text)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 16384,   # 上下文窗口，够处理 1 万字
                    "temperature": 0.7, # 稍微有点变化，不呆板
                }
            },
            timeout=300  # 长文处理可能慢，给 5 分钟
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "模型没有返回内容。")

    except requests.exceptions.ConnectionError:
        return "连不上 Ollama。请确认 Ollama 正在运行，并且 qwen2.5:7b 已经拉取。"
    except requests.exceptions.Timeout:
        return "处理超时。文章可能太长，试试分段处理。"
    except Exception as e:
        return f"出错了：{str(e)}"

# ============================================================
# Gradio 界面
# ============================================================
demo = gr.Interface(
    fn=to_oral_script,
    inputs=gr.Textbox(
        lines=20,
        label="粘贴长文",
        placeholder="把你的知乎长文、公众号长文、Free Talk 原稿贴在这里……"
    ),
    outputs=gr.Markdown(label="口播稿"),
    title="长文转口播稿工具",
    description="粘贴长文，自动改写成分块、口语化、带停顿标记的口播稿。本地运行，不联网。",
    allow_flagging="never"
)

# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    demo.launch()
