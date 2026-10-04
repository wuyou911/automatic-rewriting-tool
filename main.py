import streamlit as st
import requests

# ============================================================
# 配置区
# ============================================================
# 本地 Ollama 用这个地址
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M"

# 如果以后用智谱 API，把上面两行换成：
# ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
# ZHIPU_API_KEY = "你的API_KEY"

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
                    "temperature": 0.7,
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
# Streamlit 界面
# ============================================================
st.set_page_config(page_title="长文转口播稿", page_icon="🎙️")

st.title("长文转口播稿工具")
st.caption("粘贴长文，自动改写成分块、口语化、带停顿标记的口播稿。")

text_input = st.text_area(
    "粘贴长文",
    height=300,
    placeholder="把你的知乎长文、公众号长文、Free Talk 原稿贴在这里……"
)

if st.button("生成口播稿", type="primary"):
    if not text_input.strip():
        st.warning("请先粘贴长文。")
    else:
        with st.spinner("正在改写，请稍等……"):
            result = to_oral_script(text_input)
        st.markdown("---")
        st.markdown(result)