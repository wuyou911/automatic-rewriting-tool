import streamlit as st
from openai import OpenAI

# ============================================================
# 配置区
# ============================================================
api_key = st.secrets["ZHIPU_API_KEY"]

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

MODEL_NAME = "glm-4.7-flash"

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
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            timeout=300
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"出错了：{str(e)}"

# ============================================================
# Streamlit 界面
# ============================================================
st.set_page_config(page_title="长文转口播稿", page_icon="🎙️")

st.title("长文转口播稿工具")
st.caption("粘贴长文，自动改写成分块、口语化、带停顿标记的口播稿。")

# 初始化状态
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

text_input = st.text_area(
    "粘贴长文",
    height=300,
    placeholder="把你的知乎长文、公众号长文、Free Talk 原稿贴在这里……"
)

if st.button("生成口播稿", type="primary", disabled=st.session_state.is_processing):
    if not text_input.strip():
        st.warning("请先粘贴长文。")
    else:
        st.session_state.is_processing = True

        with st.spinner("正在改写，请稍等……"):
            result = to_oral_script(text_input)

        st.session_state.is_processing = False
        st.markdown("---")
        st.markdown(result)