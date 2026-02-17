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
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: {hex_color}; font-size: 50px;">{result_text}</h1>
            <h3 style="color: gray;">倍数: x{multi}</h3>
        </div>
        """, unsafe_allow_html=True)

        if multi > 1: st.balloons()
        
        # 2. 如果有牛身分组，显示 3+2 布局
        if len(body_cards) == 3 and len(head_cards) == 2:
            st.info("👇 拆牌结果 👇")
            
            # 第一行：牛身 (3张)
            st.markdown("### 牛身 (总和为10的倍数)")
            cols_body = st.columns(3) # 创建3列
            for i, card_code in enumerate(body_cards):
                # 在每一列显示一张牌的大字
                cols_body[i].markdown(f"""
                <div style="
                    border: 2px solid #4CAF50; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;
                    background-color: #fff7e3;">
                    <h2 style="color: #919191">{format_card_name(card_code)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # 第二行：牛尾 (2张)
            st.markdown("### 点数 (决定胜负)")
            cols_head = st.columns(3) # 为了居中，我们还是开3列，只用中间两列，或者开2列
            cols_head = st.columns(2) 
            for i, card_code in enumerate(head_cards):
                cols_head[i].markdown(f"""
                <div style="
                    border: 2px solid #FF5722; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;
                    background-color: #fff7e3;">
                    <h2 style="color: #919191">{format_card_name(card_code)}</h2>
                </div>
                """, unsafe_allow_html=True)

        elif len(body_cards) == 5:
            # 五公或五小的情况
            st.success(f"绝杀牌型！所有牌：{body_cards}")
            
        else:
            # 无牛的情况
            st.warning("没凑成牛，这是一把散牌。")
            st.write(f"手牌: {unique_cards}")

    elif len(unique_cards) == 0:
        st.warning("⚠️ 没有检测到扑克牌。")
    else:
        st.warning(f"⚠️ 找到了 {len(unique_cards)} 张牌，需要 5 张。")
        st.write(f"当前识别: {unique_cards}")
