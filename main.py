# main.py - 삼국의 미략상

import pygame
import sys

# 코어 모듈 import
from core.player import Player
from core.npc import NPC, NPC_DIALOGUE_DATA # NPC_DIALOGUE_DATA는 이제 {dialogue, info_type} 포함
from core.market import Market
from core.ui import Button, draw_info_panel, draw_betting_ui, draw_results
from core.function import calculate_final_price

# 설정 데이터 import
from config.game_data import (
    NPC_POSITIONS, 
    TARGET_NPCS, 
    get_player_start_positions, 
    get_market_position
)

pygame.init()

# ============================================
# 게임 설정
# ============================================

# 폰트 및 색상 설정
FONT_PATH = 'assets/fonts/SSRockRegular.ttf' 
FONT_SIZE = 32

try:
    FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)
    SMALL_FONT = pygame.font.Font(FONT_PATH, 26)
    TINY_FONT = pygame.font.Font(FONT_PATH, 20)
except Exception as e:
    print(f"Error: {FONT_PATH} 폰트 파일을 찾을 수 없습니다. ({e})")
    try:
        # 기본 폰트 로드 시도
        FONT = pygame.font.Font(None, FONT_SIZE)
        SMALL_FONT = pygame.font.Font(None, 26)
        TINY_FONT = pygame.font.Font(None, 20)
    except:
        print("기본 폰트 로드에도 실패했습니다.")
        pygame.quit()
        sys.exit()

# 색상 설정 
TEXT_COLOR = (250, 240, 200)
GOLD = (218, 165, 32)
DARK_WOOD = (101, 67, 33)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (0, 255, 0)
GRAY = (70, 70, 70)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (40, 40, 40)
RESULT_COLOR = (0, 200, 200)

# UI 함수에 전달할 색상 딕셔너리
COLORS = {
    'TEXT_COLOR': TEXT_COLOR,
    'GOLD': GOLD,
    'DARK_WOOD': DARK_WOOD,
    'WHITE': WHITE,
    'BLACK': BLACK,
    'RED': RED,
    'BLUE': BLUE,
    'LIGHT_GRAY': LIGHT_GRAY,
}

# 파일 경로 설정 
MAP_IMAGE_PATH = 'assets/images/map.png'
DEALER_1_PATH = 'assets/images/dealer_1.png'
DEALER_2_PATH = 'assets/images/dealer_2.png'
DEALER_3_PATH = 'assets/images/dealer_3.png'

# 게임 창 설정
VIRTUAL_WIDTH = 1200
VIRTUAL_HEIGHT = 800

TASKBAR_ADJUST_HEIGHT = 40 
ACTUAL_HEIGHT = VIRTUAL_HEIGHT - TASKBAR_ADJUST_HEIGHT
ACTUAL_WIDTH = int(ACTUAL_HEIGHT / VIRTUAL_HEIGHT * VIRTUAL_WIDTH)

display_screen = pygame.display.set_mode((ACTUAL_WIDTH, ACTUAL_HEIGHT))
pygame.display.set_caption("삼국의 미략상")

screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

SCREEN_WIDTH = VIRTUAL_WIDTH
SCREEN_HEIGHT = VIRTUAL_HEIGHT

PLAYER_SIZE = 50
STEP_SIZE = 50
INFO_PANEL_WIDTH = 400
GAME_AREA_WIDTH = SCREEN_WIDTH - INFO_PANEL_WIDTH
PADDING = 15

# ============================================
# 이미지 로드
# ============================================
try:
    # 💡 이미지 경로 수정 반영
    background_image = pygame.image.load(MAP_IMAGE_PATH).convert() 
    background_image = pygame.transform.scale(
        background_image, (GAME_AREA_WIDTH, SCREEN_HEIGHT)
    )
except pygame.error as e:
    print(f"이미지 로드 오류: {e}. 대체 배경 사용.")
    background_image = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT))
    background_image.fill((100, 100, 100))

# ============================================
# 유틸리티 함수
# ============================================
def show_loading_screen(message):
    """로딩 화면 표시"""
    screen.fill(BLACK)
    loading_text = FONT.render(message, True, GOLD)
    screen.blit(loading_text, (SCREEN_WIDTH // 2 - loading_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    scaled_surface = pygame.transform.scale(screen, (ACTUAL_WIDTH, ACTUAL_HEIGHT))
    display_screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

# ============================================
# 게임 초기화
# ============================================
show_loading_screen("NPC 대사 생성 중...")

# 💡 NPC_DATA 생성 시 info_type 포함
NPC_DATA = [(d['position'], d['dialogue'], d['info_type']) for d in NPC_DIALOGUE_DATA]

show_loading_screen("게임 시작!")
pygame.time.wait(500)

# Player 및 NPC 생성
START_POSITIONS = get_player_start_positions(SCREEN_HEIGHT, PLAYER_SIZE, GAME_AREA_WIDTH)

players = [
    Player(DEALER_1_PATH, START_POSITIONS[0], "백제 상인", player_size=PLAYER_SIZE),
    Player(DEALER_2_PATH, START_POSITIONS[1], "신라 상인", player_size=PLAYER_SIZE),
    Player(DEALER_3_PATH, START_POSITIONS[2], "고구려 상인", player_size=PLAYER_SIZE),
]

# 💡 NPC 객체 생성 시 info_type 인자 추가 (npc.py의 NPC 클래스 정의에 따라)
npcs = pygame.sprite.Group([
    NPC(pos, info, info_type, step_size=STEP_SIZE) for pos, info, info_type in NPC_DATA
])

MARKET_POS = get_market_position(GAME_AREA_WIDTH, SCREEN_HEIGHT, STEP_SIZE)
market = Market(MARKET_POS, step_size=STEP_SIZE)
all_sprites = pygame.sprite.Group(players, npcs, market)

# 버튼 생성
center_x = GAME_AREA_WIDTH // 2
start_bet_button = Button(
    x=center_x - 100, y=SCREEN_HEIGHT // 2 + 250, width=200, height=50,
    text="거래 시작", color=LIGHT_GRAY, hover_color=GOLD, action="START_BETTING"
)
buy_button = Button(
    x=0, y=0, width=120, height=40, text="매수", color=LIGHT_GRAY, hover_color=RED, action="TOGGLE_BUY"
)
sell_button = Button(
    x=0, y=0, width=120, height=40, text="매도", color=LIGHT_GRAY, hover_color=BLUE, action="TOGGLE_SELL"
)
finish_bet_button = Button(
    x=0, y=0, width=200, height=50, text="베팅 완료", color=LIGHT_GRAY, hover_color=GOLD, action="FINISH_BETTING"
)
show_result_button = Button(
    x=center_x - 100, y=0, width=200, height=50, text="게임 종료", color=LIGHT_GRAY, hover_color=GOLD, action="SHOW_RESULTS"
)

# 게임 상태 변수
current_turn = 0
current_player = players[current_turn]
game_message = f"{current_player.name} 님의 턴. 방향키로 이동하세요."
game_state = "MOVING"
input_price = "0"
input_quantity = "0"
active_input = "price"
trade_finished_count = 0
final_rice_price = 0

# 입력 박스 위치 저장용
input_boxes = {'price_box': None, 'quantity_box': None}

# ============================================
# 게임 루프
# ============================================
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "RESULT_VIEW":
            result = show_result_button.handle_event(event, current_player)
            if result == "SHOW_RESULTS":
                running = False
            continue

        if game_state == "BETTING":
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos

                if buy_button.rect.collidepoint(click_pos):
                    current_player.bet_type = "매수"
                elif sell_button.rect.collidepoint(click_pos):
                    current_player.bet_type = "매도"
                
                # 입력 박스 클릭 처리
                if input_boxes['price_box'] and input_boxes['price_box'].collidepoint(click_pos):
                    active_input = "price"
                elif input_boxes['quantity_box'] and input_boxes['quantity_box'].collidepoint(click_pos):
                    active_input = "quantity"

            result = buy_button.handle_event(event, current_player)
            result = sell_button.handle_event(event, current_player) or result
            result = finish_bet_button.handle_event(event, current_player) or result

            if result == "BETTING_FINISH":
                try:
                    price = int(input_price)
                    quantity = int(input_quantity)

                    if price <= 0 or quantity <= 0:
                        game_message = "가격과 수량은 0보다 커야 합니다."
                        continue

                    current_player.bet_price = price
                    current_player.bet_quantity = quantity
                    current_player.bet_status = f"{current_player.bet_type} {quantity}개 ({price}원)"
                    current_player.trade_done = True
                    trade_finished_count += 1

                    game_message = f"{current_player.name} 님 거래 완료! 다음 상인 대기."
                    game_state = "MOVING"

                    if trade_finished_count < len(players):
                        next_turn_found = False
                        for _ in range(len(players)):
                            current_turn = (current_turn + 1) % len(players)
                            current_player = players[current_turn]
                            if not current_player.trade_done:
                                next_turn_found = True
                                break

                        if next_turn_found:
                            game_message = f"{current_player.name} 님의 턴. 방향키로 이동하세요."
                            input_price, input_quantity = "0", "0"
                        else:
                            # 💡 최종 가격 계산 시 NPC_DIALOGUE_DATA 전달
                            final_rice_price = calculate_final_price(players, NPC_DIALOGUE_DATA) 
                            game_state = "RESULT_VIEW"
                            game_message = "모든 상인의 최종 정산이 완료되었습니다. 결과를 확인하세요!"
                    else:
                        # 💡 최종 가격 계산 시 NPC_DIALOGUE_DATA 전달
                        final_rice_price = calculate_final_price(players, NPC_DIALOGUE_DATA) 
                        game_state = "RESULT_VIEW"
                        game_message = "최종 정산이 완료되었습니다. 결과를 확인하세요!"

                except ValueError:
                    game_message = "유효한 숫자(가격/수량)를 입력하세요."

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB: 
                    active_input = "quantity" if active_input == "price" else "price"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "price":
                        input_price = input_price[:-1] if len(input_price) > 1 else "0"
                    else:
                        input_quantity = input_quantity[:-1] if len(input_quantity) > 1 else "0"
                elif event.unicode.isdigit():
                    if active_input == "price":
                        input_price = (input_price if input_price != "0" else "") + event.unicode
                    else:
                        input_quantity = (input_quantity if input_quantity != "0" else "") + event.unicode

            continue

        elif game_state == "MOVING":
            if current_player.trade_done:
                continue

            if current_player.can_bet:
                result = start_bet_button.handle_event(event, current_player)
                if result == "BETTING_START":
                    game_state = "BETTING"
                    game_message = "가격/수량/매수/매도를 결정하세요."
                    continue

            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0

                if event.key == pygame.K_LEFT: dx = -STEP_SIZE
                elif event.key == pygame.K_RIGHT: dx = STEP_SIZE
                elif event.key == pygame.K_UP: dy = -STEP_SIZE
                elif event.key == pygame.K_DOWN: dy = STEP_SIZE

                if dx != 0 or dy != 0:
                    current_player.move(dx, dy, GAME_AREA_WIDTH, SCREEN_HEIGHT)

                    hit_npcs = pygame.sprite.spritecollide(current_player, npcs, False)

                    new_message = f"{current_player.name} 님의 턴. 방향키로 이동하세요."

                    if hit_npcs and current_player.npcs_met < TARGET_NPCS:
                        for npc in hit_npcs:
                            if not npc.met:
                                # 💡 수집 정보 수정: 텍스트와 info_type을 딕셔너리로 저장
                                current_player.collected_info.append({
                                    'dialogue': npc.info,
                                    'type': npc.info_type 
                                })
                                current_player.npcs_met += 1
                                npc.met = True
                                new_message = f"NPC와 만남! ({current_player.npcs_met}/{TARGET_NPCS}) 정보 획득!"
                                if current_player.npcs_met == TARGET_NPCS:
                                    new_message = "모든 정보를 모았습니다! 장터로 향하세요."
                                break
                            else:
                                new_message = "이미 만난 NPC입니다. 이동을 계속하세요."

                    if current_player.npcs_met >= TARGET_NPCS and pygame.sprite.collide_rect(current_player, market):
                        current_player.can_bet = True
                        new_message = f"장터 도착! 마우스로 '거래 시작' 버튼을 누르세요."
                    elif not current_player.trade_done and new_message == f"{current_player.name} 님의 턴. 방향키로 이동하세요." and current_player.can_bet:
                        new_message = f"장터 도착! 마우스로 '거래 시작' 버튼을 누르세요."

                    game_message = new_message

    # 화면 그리기 (기존 유지)
    screen.fill(GRAY)
    screen.blit(background_image, (0, 0))
    
    for npc in npcs:
        if not npc.met:
            screen.blit(npc.image, npc.rect)

    screen.blit(market.image, market.rect)

    for player in players:
        screen.blit(player.image, player.rect)

    draw_info_panel(screen, current_player, GAME_AREA_WIDTH, SCREEN_HEIGHT, 
                    INFO_PANEL_WIDTH, PADDING, FONT, TINY_FONT, GOLD, DARK_WOOD, WHITE)

    message_surface = FONT.render(game_message, True, GOLD)
    message_rect = message_surface.get_rect(center=(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT - 40 + FONT.get_height() // 2))

    padding_x = 20
    padding_y = 10
    background_rect = pygame.Rect(
        message_rect.x - padding_x,
        message_rect.y - padding_y,
        message_rect.width + 2 * padding_x,
        message_rect.height + 2 * padding_y
    )
    pygame.draw.rect(screen, DARK_WOOD, background_rect, border_radius=5) 
    pygame.draw.rect(screen, GOLD, background_rect, 3, border_radius=5)

    screen.blit(message_surface, message_rect.topleft)
    
    if game_state == "BETTING":
        buy_button.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pygame.mouse.get_pos()), current_player)
        sell_button.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pygame.mouse.get_pos()), current_player)
        
        input_boxes = draw_betting_ui(screen, current_player, input_price, input_quantity, 
                                      active_input, buy_button, sell_button, finish_bet_button, 
                                      GAME_AREA_WIDTH, SCREEN_HEIGHT, FONT, PADDING, COLORS)

    elif game_state == "MOVING" and current_player.can_bet:
        start_bet_button.rect.x = MARKET_POS[0] + STEP_SIZE - 100
        start_bet_button.rect.y = MARKET_POS[1] + STEP_SIZE * 2 + 10
        start_bet_button.draw(screen, FONT, TEXT_COLOR)

    elif game_state == "RESULT_VIEW":
        draw_results(screen, players, final_rice_price, show_result_button, 
                     GAME_AREA_WIDTH, SCREEN_HEIGHT, FONT, SMALL_FONT, COLORS)

    scaled_surface = pygame.transform.scale(screen, (ACTUAL_WIDTH, ACTUAL_HEIGHT))
    display_screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
