"""NPC 클래스 및 AI 대사 생성"""
import pygame
import random
import os
import json # 
from openai import OpenAI
from dotenv import load_dotenv
from config.game_data import NPC_POSITIONS, TARGET_NPCS

# .env 파일에서 환경 변수 로드
load_dotenv()

# ============================================
# OpenAI 클라이언트 초기화
# ============================================
try:
    # API KEY가 환경 변수에 설정되어 있어야 함
    openai_client = OpenAI() 
    print("✓ OpenAI 클라이언트 준비 완료!")
except Exception as e:
    print(f"❌ OpenAI 클라이언트 초기화 오류: {e}")
    openai_client = "error"

# ============================================
# NPC 대사 생성 함수 (JSON 응답 요청하도록 수정)
# ============================================
def generate_npc_dialogue_openai(pos):
    """
    NPC 위치 기반 창의적 대사와 가격 영향력 정보를 JSON으로 생성 (OpenAI GPT-4o 사용).
    """
    global openai_client
    
    if openai_client == "error":
        # 💡 오류 시 info_type: 'NONE' 포함하여 반환
        return {
            "dialogue": "API 연결 오류: 시세 정보를 알 수 없습니다.",
            "info_type": "NONE" 
        }
        
    x, y = pos
    
    # 위치 기반 컨텍스트 및 역할 부여 로직
    if y > 600:
        location_hint = "마을 남쪽의 논 근처"
        role = random.choice(["농민", "마을 이장"])
    elif y < 300:
        location_hint = "마을 북쪽의 산길 입구"
        role = random.choice(["떠돌이 상인", "순찰 관리"])
    elif x < 300:
        location_hint = "마을 서쪽의 우물가"
        role = random.choice(["주민", "행상"])
    else:
        location_hint = "마을 동쪽의 장터 입구"
        role = random.choice(["쌀 상인", "군량미 담당 관리"])
        
    # 💡 AI에게 전달할 구체적인 임무 및 가격 영향력 정보 생성 유도
    base_prompt = (
        f"당신은 삼국시대 배경의 **{location_hint}**에 있는 **{role}**입니다. "
        f"최근 쌀 시장 가격에 영향을 줄 수 있는 날씨, 전쟁, 흉년, 세금, 관리의 동향 등에 대한 정보를 바탕으로 짧고 흥미로운 소문이나 정보를 한 문장으로 말해주세요. "
        f"이 정보는 **쌀 가격 상승(UP) 또는 하락(DOWN) 중 하나**에 영향을 미치는 내용이어야 합니다."
    )
    
    # 💡 시스템 지침 : JSON 형식과 필드 명확히 요청
    system_instruction = (
        "당신은 삼국시대 배경의 NPC입니다. 대사는 쌀 시장 정보에 초점을 맞추고, 역할에 맞는 말투로 30자 내외로 간결하게 작성하세요. "
        "응답은 반드시 **JSON 형식**이어야 하며, 두 개의 키('dialogue', 'influence')를 포함해야 합니다. "
        "'influence' 필드의 값은 반드시 **'UP'** 또는 **'DOWN'** 중 하나여야 합니다."
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            # 💡 JSON 응답 형식 요청 추가
            response_format={"type": "json_object"}, 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.8,
            max_tokens=200,
            top_p=1,
        )
        
        raw_json_response = response.choices[0].message.content
        # 💡 JSON 파싱
        parsed_data = json.loads(raw_json_response)

        # 30자로 제한 및 불필요한 문자 정리
        dialogue = parsed_data.get('dialogue', '정보 없음').strip().replace('"', '').replace("'", '')
        if len(dialogue) > 30:
            dialogue = dialogue[:30].strip() + "..."
            
        # 💡 influence 값을 info_type으로 추출
        info_type = parsed_data.get('influence', 'NONE').upper()
        
        return {
            "dialogue": dialogue,
            "info_type": info_type
        }
    
    except Exception as e:
        print(f"⚠️ OpenAI API 호출 또는 JSON 파싱 중 오류 발생: {e}")
        # 오류 발생 시 기본값 반환
        return {
            "dialogue": f"요즘 흉년이라 그런가... 말이 잘 안 나오네. ({role})",
            "info_type": "NONE"
        }

# ============================================
# 모든 NPC 대사 생성 (수정된 반환값 사용)
# ============================================
def generate_all_npc_data():
    """모든 NPC 위치에 대해 대사를 생성하고 리스트로 반환"""
    print("📢 21개 NPC 대사 생성 시작...")
    
    dialogues = []
    for i, pos in enumerate(NPC_POSITIONS):
        # 💡 generate_npc_dialogue_openai에서 딕셔너리 반환
        npc_data = generate_npc_dialogue_openai(pos)
        
        dialogues.append({
            "id": i,
            "position": pos,
            "dialogue": npc_data["dialogue"],
            "info_type": npc_data["info_type"] # 💡 가격 영향력 정보 추가
        })
        
    print("✅ NPC 대사 생성 완료.")
    return dialogues

# 이 스크립트가 로드될 때 모든 NPC 대사가 생성됩니다.
NPC_DIALOGUE_DATA = generate_all_npc_data()

# ============================================
# NPC 클래스
# ============================================
class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, info_message, info_type, step_size=50): 
        super().__init__()
        
        radius = step_size // 2
        size = step_size
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        
        # 색상 정의 (main.py의 색상 사용)
        RED = (200, 50, 50)
        GOLD = (218, 165, 32) 
        color = RED
        
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        pygame.draw.circle(self.image, GOLD, (radius, radius), radius, 2)
        
        self.image.set_alpha(150)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.info = info_message
        self.info_type = info_type # 💡 info_type을 인스턴스 변수로 저장
        self.met = False