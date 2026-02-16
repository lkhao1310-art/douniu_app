# logic.py
import itertools

def get_card_info(card_code):
    """
    解析牌的代码，返回 (点数列表, 花色, 显示名)
    card_code 例子: 'As', '10h', '6d', 'Kc'
    """
    code = str(card_code).lower() # 确保是字符串并转小写
    
    # 1. 提取花色 (最后一位)
    suit = code[-1] # 's', 'h', 'd', 'c'
    
    # 2. 提取面值 (前面所有位)
    rank = code[:-1] # 'a', '10', 'k'
    
    # 3. 定义点数和规则
    values = []
    is_face = False # 是否是花牌 JQK
    
    if rank in ['j', 'q', 'k']:
        values = [10]
        is_face = True
    elif rank == 'a':
        values = [1]
    elif rank == '3':
        values = [3, 6] # 3 可以当 3 或 6
    elif rank == '6':
        values = [6, 3] # 6 可以当 6 或 3
    else:
        try:
            values = [int(rank)]
        except:
            values = [0] # 防止出错
            
    return {
        "code": card_code,
        "rank": rank,
        "suit": suit,
        "values": values,
        "is_face": is_face
    }

def calculate_niu(card_codes_list):
    """
    主函数：接收 ['As', '10h', '3d', '6c', 'Kh']
    返回 (结果文本, 倍数, 颜色元组)
    """
    # 如果传入的不是列表，或者长度不对，直接返回等待
    if not isinstance(card_codes_list, list) or len(card_codes_list) != 5:
        return "Waiting...", 0, (200, 200, 200)

    # 1. 解析所有牌
    try:
        cards = [get_card_info(c) for c in card_codes_list]
    except Exception as e:
        return f"Error: {str(e)}", 0, (255, 0, 0)
    
    # --- 特殊牌型检测 (直接判断 5 张牌) ---
    
    # A. 五公 (Five Dukes): 全是 J, Q, K
    if all(c['is_face'] for c in cards):
        return "FIVE DUKES! (五公)", 7, (255, 215, 0) # 金色

    # B. 五小 (Five Small): 全是 A, 2, 3, 4 且 总和 <= 10
    if all(c['rank'] in ['a', '2', '3', '4'] for c in cards):
        min_sum = sum(c['values'][0] for c in cards)
        if min_sum <= 10:
            return "FIVE SMALL! (五小)", 6, (0, 255, 255) # 青色

    # --- 牛牛核心计算 (包含 3/6 变身) ---
    possibilities = []
    for c in cards:
        possibilities.append([(c, v) for v in c['values']])
    
    best_result = (-1, "No Niu (无牛)", 1, (128, 128, 128)) # 默认灰色
    
    # 遍历每一种 3/6 的变身情况
    for p_hand in itertools.product(*possibilities):
        # p_hand 是 5 个元组: ((card_obj, value), (card_obj, value)...)
        
        indices = [0, 1, 2, 3, 4]
        
        for combo in itertools.combinations(indices, 3):
            val1 = p_hand[combo[0]][1]
            val2 = p_hand[combo[1]][1]
            val3 = p_hand[combo[2]][1]
            
            if (val1 + val2 + val3) % 10 == 0:
                # 找到了牛基！看剩下两张
                remaining = [i for i in indices if i not in combo]
                
                c4_obj = p_hand[remaining[0]][0]
                v4 = p_hand[remaining[0]][1]
                c5_obj = p_hand[remaining[1]][0]
                v5 = p_hand[remaining[1]][1]
                
                # === 判定剩下两张的牌型 ===
                current_score = 0
                current_text = ""
                current_multi = 1
                current_color = (0, 255, 0)
                
                # 1. 黑杰 (Ngau Tonku): 黑桃A + 花牌
                is_spade_A = (c4_obj['rank'] == 'a' and c4_obj['suit'] == 's') or \
                             (c5_obj['rank'] == 'a' and c5_obj['suit'] == 's')
                has_face = c4_obj['is_face'] or c5_obj['is_face']
                
                if is_spade_A and has_face:
                    current_score = 500
                    current_text = "Ngau Tonku! (黑杰)"
                    current_multi = 5
                    current_color = (138, 43, 226) # 紫色
                    
                # 2. 对子牛 (Double Ox)
                elif v4 == v5: # 点数相同即为对子 (3和6互变后相等也算)
                    pair_val = v4
                    current_score = 300 + pair_val
                    current_text = f"Double Ox {pair_val} (对子牛)"
                    current_multi = 2
                    current_color = (255, 215, 0) # 金色/黄色
                
                # 3. 普通牛 / 牛牛
                else:
                    sum_remain = v4 + v5
                    niu_point = sum_remain % 10
                    
                    if niu_point == 0:
                        current_score = 100
                        current_text = "SUPER NIU! (牛牛)"
                        current_multi = 1 
                        current_color = (255, 0, 0) # 红色
                    else:
                        current_score = 10 + niu_point
                        current_text = f"Niu {niu_point} (牛{niu_point})"
                        current_multi = 1
                        current_color = (0, 255, 0) # 绿色
                
                # 更新最大值
                if current_score > best_result[0]:
                    best_result = (current_score, current_text, current_multi, current_color)
        
    return best_result[1], best_result[2], best_result[3] # 返回 (文本, 倍数, 颜色)

# 测试一下
if __name__ == "__main__":
    # 测试黑杰: 10, 10, 10 + 黑桃A + K
    print(calculate_niu(['10h', '10d', '10c', 'As', 'Kh']))
    # 测试3/6互转: 3, 7, 10 + 3 + 6 (应该是对子牛)
    print(calculate_niu(['3d', '7h', '10c', '3s', '6h']))