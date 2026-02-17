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


# 这里的字典只用于在图片上画数字，不参与核心逻辑计算
display_mapping = {
    '10c': 10, '10d': 10, '10h': 10, '10s': 10,
    'ac': 1, 'ad': 1, 'ah': 1, 'as': 1,
    '2c': 2, '2d': 2, '2h': 2, '2s': 2,
    '3c': 3, '3d': 3, '3h': 3, '3s': 3,
    '4c': 4, '4d': 4, '4h': 4, '4s': 4,
    '5c': 5, '5d': 5, '5h': 5, '5s': 5,
    '6c': 6, '6d': 6, '6h': 6, '6s': 6,
    '7c': 7, '7d': 7, '7h': 7, '7s': 7,
    '8c': 8, '8d': 8, '8h': 8, '8s': 8,
    '9c': 9, '9d': 9, '9h': 9, '9s': 9,
    'jc': 11, 'jd': 11, 'jh': 11, 'js': 11,
    'qc': 12, 'qd': 12, 'qh': 12, 'qs': 12,
    'kc': 13, 'kd': 13, 'kh': 13, 'ks': 13,
    # 兼容大写
    '10C': 10, '10D': 10, '10H': 10, '10S': 10,
    'AC': 1, 'AD': 1, 'AH': 1, 'AS': 1,
    '2C': 2, '2D': 2, '2H': 2, '2S': 2,
    '3C': 3, '3D': 3, '3H': 3, '3S': 3,
    '4C': 4, '4D': 4, '4H': 4, '4S': 4,
    '5C': 5, '5D': 5, '5H': 5, '5S': 5,
    '6C': 6, '6D': 6, '6H': 6, '6S': 6,
    '7C': 7, '7D': 7, '7H': 7, '7S': 7,
    '8C': 8, '8D': 8, '8H': 8, '8S': 8,
    '9C': 9, '9D': 9, '9H': 9, '9S': 9,
    'JC': 11, 'JD': 11, 'JH': 11, 'JS': 11,
    'QC': 12, 'QD': 12, 'QH': 12, 'QS': 12,
    'KC': 13, 'KD': 13, 'KH': 13, 'KS': 13,
}

# === 3. 摄像头输入 ===
img_file = st.camera_input("点击拍照")

if img_file is not None:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    results = model(img)
    
    # ⚠️ 关键修改：我们要存牌的名字(如 '10s')，而不是数字
    detected_cards = [] 
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            name = model.names[cls] # 获取名字，比如 'As', '10h'
            
            # 过滤掉不认识的东西
            if name in display_mapping:
                detected_cards.append(name) # 把名字存进列表
                
                # 画图
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
                
                # 图片上还是显示数字方便看
                display_num = display_mapping[name]
                cv2.putText(img, str(display_num), (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

    st.image(img, channels="BGR", caption="识别结果")

    # === 4. 核心修复：自动去重逻辑 ===
    st.divider()
    
    # 🛠️ 修复步骤 1：去重 (De-duplication)
    # 解释：set() 会自动把 ['10h', '10h', 'As'] 变成 {'10h', 'As'}，就把重复的删掉了
    unique_cards = list(set(detected_cards))
    
    # 🛠️ 修复步骤 2：排序 (可选，为了好看)
    # 这一步是为了让显示的列表顺序稳定，不会跳来跳去
    unique_cards.sort()

    # === 5. 开始判断 ===
    if len(unique_cards) == 5:
        # 成功！只有 5 张不重复的牌
        result_text, multi, color_rgb = calculate_niu(unique_cards)
        
        hex_color = '#%02x%02x%02x' % color_rgb
        st.markdown(f"""
        <div style="text-align: center;">
            <h1 style="color: {hex_color}; font-size: 50px;">{result_text}</h1>
            <h3 style="color: gray;">倍数: x{multi}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if multi > 1:
            st.balloons()
        
        st.success(f"✅ 有效识别: {unique_cards}")

    elif len(unique_cards) > 5:
        # 如果去重后还是超过 5 张（比如真有 6 张牌，或者误识别了别的）
        st.error(f"⚠️ 牌太多了！找到了 {len(unique_cards)} 张牌。")
        st.write(f"识别列表: {unique_cards}")
        st.write("请移走多余的牌，或调整角度。")

    elif len(unique_cards) == 0:
        st.warning("⚠️ 没有检测到扑克牌。")
        
    else:
        # 少于 5 张
        st.warning(f"⚠️ 只找到了 {len(unique_cards)} 张牌，还差 {5 - len(unique_cards)} 张。")
        st.write(f"当前识别: {unique_cards}")
