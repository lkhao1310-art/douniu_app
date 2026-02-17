# logic.py (必须是这个返回 5 个值的版本)
import itertools

def get_card_info(card_code):
    """
    解析牌的代码，返回 (点数列表, 花色, 显示名)
    """
    code = str(card_code).lower()
    suit = code[-1]
    rank = code[:-1]
    
    values = []
    is_face = False
    
    if rank in ['j', 'q', 'k']:
        values = [10]
        is_face = True
    elif rank == 'a':
        values = [1]
    elif rank == '3':
        values = [3, 6]
    elif rank == '6':
        values = [6, 3]
    else:
        try:
            values = [int(rank)]
        except:
            values = [0]
            
    return {
        "code": card_code,
        "rank": rank,
        "suit": suit,
        "values": values,
        "is_face": is_face
    }

def calculate_niu(card_codes_list):
    """
    返回: (结果文本, 倍数, 颜色, 牛身3张列表, 牛尾2张列表)
    """
    if not isinstance(card_codes_list, list) or len(card_codes_list) != 5:
        return "Waiting...", 0, (200, 200, 200), [], []

    try:
        cards = [get_card_info(c) for c in card_codes_list]
    except Exception as e:
        return f"Error", 0, (255, 0, 0), [], []
    
    # --- 特殊牌型 (五公/五小) ---
    if all(c['is_face'] for c in cards):
        return "FIVE DUKES! (五公)", 7, (255, 215, 0), card_codes_list, []

    if all(c['rank'] in ['a', '2', '3', '4'] for c in cards):
        min_sum = sum(c['values'][0] for c in cards)
        if min_sum <= 10:
            return "FIVE SMALL! (五小)", 6, (0, 255, 255), card_codes_list, []

    # --- 牛牛核心计算 ---
    possibilities = []
    for c in cards:
        possibilities.append([(c, v) for v in c['values']])
    
    # 默认结果
    best_result = (-1, "No Niu (无牛)", 1, (128, 128, 128), [], card_codes_list)
    
    for p_hand in itertools.product(*possibilities):
        indices = [0, 1, 2, 3, 4]
        
        for combo in itertools.combinations(indices, 3):
            val1 = p_hand[combo[0]][1]
            val2 = p_hand[combo[1]][1]
            val3 = p_hand[combo[2]][1]
            
            if (val1 + val2 + val3) % 10 == 0:
                # === 找到了牛身！===
                body_codes = [p_hand[i][0]['code'] for i in combo]
                
                remaining = [i for i in indices if i not in combo]
                c4_obj = p_hand[remaining[0]][0]
                v4 = p_hand[remaining[0]][1]
                c5_obj = p_hand[remaining[1]][0]
                v5 = p_hand[remaining[1]][1]
                
                head_codes = [c4_obj['code'], c5_obj['code']]
                
                # === 算分逻辑 ===
                current_score = 0
                current_text = ""
                current_multi = 1
                current_color = (0, 255, 0)
                
                # 1. 黑杰
                is_spade_A = (c4_obj['rank'] == 'a' and c4_obj['suit'] == 's') or \
                             (c5_obj['rank'] == 'a' and c5_obj['suit'] == 's')
                has_face = c4_obj['is_face'] or c5_obj['is_face']
                
                if is_spade_A and has_face:
                    current_score = 500
                    current_text = "Ngau Tonku! (黑杰)"
                    current_multi = 5
                    current_color = (138, 43, 226)
                    
                # 2. 对子牛
                elif v4 == v5:
                    pair_val = v4
                    current_score = 300 + pair_val
                    current_text = f"Double Ox {pair_val} (对子牛)"
                    current_multi = 3
                    current_color = (255, 215, 0)
                
                # 3. 普通牛
                else:
                    sum_remain = v4 + v5
                    niu_point = sum_remain % 10
                    
                    if niu_point == 0:
                        current_score = 100
                        current_text = "SUPER NIU! (牛牛)"
                        current_multi = 1 
                        current_color = (79, 7, 0)
                    else:
                        current_score = 10 + niu_point
                        current_text = f"Niu {niu_point} (牛{niu_point})"
                        current_multi = 1
                        current_color = (79, 7, 0)
                
                # 更新最大值
                if current_score > best_result[0]:
                    best_result = (current_score, current_text, current_multi, current_color, body_codes, head_codes)
        
    return best_result[1], best_result[2], best_result[3], best_result[4], best_result[5]
