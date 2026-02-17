import streamlit as st
import cv2
import numpy as np
import os
import pathlib
from ultralytics import YOLO
from logic import calculate_niu

# === 1. 页面配置 ===
st.set_page_config(page_title="斗牛神器", page_icon="🐮")
st.title("牛牛计算器 (含3变6)")
st.write("请拍摄 5 张扑克牌，支持特殊牌型识别！")

# --- 核心修复：解决跨系统路径兼容性问题 ---
temp = pathlib.PosixPath
pathlib.WindowsPath = pathlib.PosixPath
# ---------------------------------------

@st.cache_resource
def load_model():
    # 自动找到当前文件旁边的 playing_cards.pt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "playing_cards.pt")
    
    # 检查文件到底在不在（为了让你放心）
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"文件真的不存在: {model_path}")
        
    return YOLO(model_path)

try:
    model = load_model()
    # st.success("模型加载成功！") # 测试成功后可以把这行删掉
except Exception as e:
    st.error(f"模型加载严重错误！详细原因: {e}")
    st.stop()


# 字典 (用于把牌名翻译成 emoji 或短文字)
# 简单的花色 Emoji 映射
suit_emoji = {'s': '♠️', 'h': '♥️', 'd': '♦️', 'c': '♣️'}

def format_card_name(code):
    """把 '10h' 变成 '♥️ 10' 这样好看的格式"""
    code = code.lower()
    suit = code[-1]
    rank = code[:-1].upper()
    return f"{suit_emoji.get(suit, '')} {rank}"

# === 3. 摄像头输入 ===
img_file = st.camera_input("点击拍照")

# 用于过滤的字典 (必须是合法牌名)
valid_cards = [
    '10c', '10d', '10h', '10s', 'ac', 'ad', 'ah', 'as', 
    '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', 
    '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', 
    '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', 
    '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 
    'jc', 'jd', 'jh', 'js', 'qc', 'qd', 'qh', 'qs', 
    'kc', 'kd', 'kh', 'ks'
]
# 兼容大写
valid_cards += [x.upper() for x in valid_cards]

if img_file is not None:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    results = model(img)
    detected_cards = []
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            name = model.names[cls]
            
            if name in valid_cards:
                detected_cards.append(name)
                # 画图
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(img, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)

    st.image(img, channels="BGR", caption="原始画面")

    # === 4. 去重与计算 ===
    st.divider()
    unique_cards = list(set(detected_cards))
    
    if len(unique_cards) == 5:
        # 🟢 调用新逻辑，接收 5 个返回值
        result_text, multi, color_rgb, body_cards, head_cards = calculate_niu(unique_cards)
        
        # 1. 显示大标题结果
        hex_color = '#%02x%02x%02x' % color_rgb
    st.markdown("""
    <style>
    /* 1. 覆盖所有可能的背景容器 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(180deg, #8B0000 0%, #B22222 60%, #FFD700 100%) !important;
        background-attachment: fixed !important;
        background-size: cover !important;
    }
    
    /* 2. 让顶部工具栏变成透明，不要白色条 */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }

    /* 3. 全局文字变白 (除了我们在卡片里特别指定的) */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {
        color: #FFFFFF !important;
    }
    
    /* 4. 按钮样式优化 (变成金色按钮) */
    .stButton>button {
        background-color: #FFD700 !important;
        color: #8B0000 !important;
        border: 2px solid #FFFFFF !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

    if multi > 1: st.balloons()
    
    # 2. 如果有牛身分组，显示 3+2 布局
    if len(body_cards) == 3 and len(head_cards) == 2:
        st.info("👇 智能拆牌结果 👇")
        
        # --- 第一行：牛身 (3张) ---
        st.markdown("### 牛身 (凑整)")
        cols_body = st.columns(3)
        for i, card_code in enumerate(body_cards):
            cols_body[i].markdown(f"""
            <div style="
                border: 2px solid #FFD700;           /* 金色边框 */
                border-radius: 10px; 
                padding: 15px; 
                text-align: center;
                background-color: rgba(255, 255, 255, 0.9); /* 半透明白色背景 */
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h2 style="color: #333333; margin: 0;">{format_card_name(card_code)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # --- 第二行：牛尾 (2张) ---
        st.markdown("### 🔥 决胜牌")
        # 修正：直接开2列，去掉原本多余的 cols_head = st.columns(3)
        cols_head = st.columns(2) 
        
        for i, card_code in enumerate(head_cards):
            # 获取花色决定颜色 (红桃/方块用红，黑桃/梅花用黑)
            display_text = format_card_name(card_code)
            if "♥" in display_text or "♦" in display_text:
                text_color = "#D32F2F" # 红色
            else:
                text_color = "#000000" # 黑色

            cols_head[i].markdown(f"""
            <div style="
                border: 3px solid #FF5722; 
                border-radius: 10px; 
                padding: 15px; 
                text-align: center;
                background-color: #fff3e0;          /* 浅橙色背景 */
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h2 style="color: {text_color}; margin: 0; font-weight: bold;">{display_text}</h2>
            </div>
            """, unsafe_allow_html=True)

    elif len(body_cards) == 5:
        st.success(f"🧧 恭喜！绝杀牌型！所有牌：{body_cards}")
        
    else:
        st.warning("💨 没凑成牛，这是一把散牌。")
        st.write(f"手牌: {unique_cards}")
