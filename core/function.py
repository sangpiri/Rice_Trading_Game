"""유틸리티 함수들"""
import random

def wrap_text(text, font, max_width):
    """
    텍스트 줄바꿈 처리.
    입력이 딕셔너리일 경우 'dialogue' 키의 값을 사용하도록 수정.
    """
    
    # 💡 수정된 부분: 입력이 딕셔너리인지 확인하고 문자열을 추출
    if isinstance(text, dict):
        text_to_wrap = text.get('dialogue', '') # 'dialogue' 키의 값을 사용
    else:
        text_to_wrap = str(text) # 문자열이 아닌 경우 안전하게 문자열로 변환 (예: 숫자)
        
    # 빈 문자열 처리
    if not text_to_wrap:
        return []

    # 기존 줄바꿈 로직 (text_to_wrap 변수를 사용하도록 변경)
    words = text_to_wrap.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines

def calculate_final_price(players, npc_dialogue_data):
    """
    최종 쌀 가격 계산 및 플레이어 손익 계산 (NPC 정보 반영)
    
    - players: 플레이어 객체 리스트 (베팅 가격 포함)
    - npc_dialogue_data: info_type('UP', 'DOWN', 'NONE')을 포함하는 NPC 정보 리스트
    """
    if not players:
        return 0

    # 1. 평균 베팅 가격 계산
    total_bet_price = sum(p.bet_price for p in players)
    avg_price = total_bet_price / len(players)

    # 2. NPC 정보 분석 및 영향력 계산
    
    # 'UP' 및 'DOWN' 정보를 가진 NPC 수 카운트
    increase_count = sum(1 for data in npc_dialogue_data if data.get('info_type') == 'UP')
    decrease_count = sum(1 for data in npc_dialogue_data if data.get('info_type') == 'DOWN')

    # NPC 총 영향력 비율 (각 2%씩 반영)
    # 예: 상승 10명, 하락 11명이면 (10 * 0.02) - (11 * 0.02) = -0.02
    npc_influence_factor = (increase_count * 0.02) - (decrease_count * 0.02)
    
    # 3. 최종 가격 변동률 계산
    
    # 3-1. 시장 변동성 (±10%) 반영: 0.9 ~ 1.1 사이의 무작위 값
    market_volatility = random.uniform(0.9, 1.1)
    
    # 3-2. NPC 영향력 반영: (1.0 + NPC 총 영향력 비율)
    npc_factor = 1.0 + npc_influence_factor

    # 최종 변동률 = 시장 변동성 * NPC 영향력
    # 두 요소를 곱하여 최종 가격에 동시에 영향을 미치도록 함
    final_volatility = market_volatility * npc_factor

    # 4. 최종 가격 결정
    final_price = int(avg_price * final_volatility)

    # 각 플레이어 손익 계산
    for player in players:
        profit_or_loss = player.bet_quantity * (final_price - player.bet_price)

        if player.bet_type == "매수":
            player.profit = profit_or_loss
        elif player.bet_type == "매도":
            player.profit = -profit_or_loss

        player.money += player.profit

    return final_price