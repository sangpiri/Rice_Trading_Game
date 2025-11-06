"""UI 컴포넌트 및 렌더링 함수"""
import pygame
from core.function import wrap_text

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface, font, text_color=(250, 240, 200)):
        current_color = self.hover_color if self.is_hovered else self.color
        
        display_rect = self.rect.copy()
        if self.is_hovered:
            scale_factor = 1.05
            new_w = int(self.rect.width * scale_factor)
            new_h = int(self.rect.height * scale_factor)
            display_rect.width = new_w
            display_rect.height = new_h
            display_rect.center = self.rect.center

        pygame.draw.rect(surface, current_color, display_rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), display_rect, 2, border_radius=5)

        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=display_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            if self.action == "START_BETTING":
                return "BETTING_START"
            elif self.action == "FINISH_BETTING":
                return "BETTING_FINISH"
            elif self.action == "TOGGLE_BUY":
                player.bet_type = "매수"
            elif self.action == "TOGGLE_SELL":
                player.bet_type = "매도"
            elif self.action == "SHOW_RESULTS":
                return "SHOW_RESULTS"
        return None

def draw_info_panel(screen, player, game_area_width, screen_height, info_panel_width, 
                    padding, font, tiny_font, gold_color, dark_wood_color, white_color):
    """정보 패널 그리기"""
    panel_rect = pygame.Rect(game_area_width, 0, info_panel_width, screen_height)
    pygame.draw.rect(screen, dark_wood_color, panel_rect) 
    pygame.draw.rect(screen, gold_color, panel_rect, 5) 

    # 제목
    title_text = "획득 정보 (" + player.name + ")"
    title = font.render(title_text, True, gold_color)
    screen.blit(title, (game_area_width + padding, 10))

    max_text_width = info_panel_width - 2 * padding
    y_offset = 50

    info_font = tiny_font
    line_height = info_font.get_height() + 3

    for i, info in enumerate(player.collected_info):
        number_text = f"{i+1}. "
        number_surf = info_font.render(number_text, True, white_color)
        screen.blit(number_surf, (game_area_width + padding, y_offset))

        info_content = info

        wrapped_lines = wrap_text(info_content, info_font, max_text_width - number_surf.get_width() - 5)

        current_y = y_offset
        for line in wrapped_lines:
            text_surf = info_font.render(line, True, white_color)
            x_start = game_area_width + padding + number_surf.get_width() if current_y == y_offset else game_area_width + padding + 15
            screen.blit(text_surf, (x_start, current_y))
            current_y += line_height

        y_offset = current_y + 5

        if y_offset > screen_height - 150:
            break

    status = [
        f"만난 NPC: {player.npcs_met}/{player.npcs_met}",  # TARGET_NPCS 대신 player 속성 사용
    ]
    y_offset = screen_height - 100
    status_font = font
    for s in status:
        text = status_font.render(s, True, gold_color)
        screen.blit(text, (game_area_width + padding, y_offset))
        y_offset += status_font.get_height() + 5

def draw_betting_ui(screen, player, input_price, input_quantity, active_input, 
                    buy_btn, sell_btn, finish_btn, game_area_width, screen_height,
                    font, padding, colors):
    """베팅 UI 그리기"""
    BLACK = colors['BLACK']
    GOLD = colors['GOLD']
    DARK_WOOD = colors['DARK_WOOD']
    WHITE = colors['WHITE']
    RED = colors['RED']
    BLUE = colors['BLUE']
    LIGHT_GRAY = colors['LIGHT_GRAY']
    TEXT_COLOR = colors['TEXT_COLOR']
    
    overlay = pygame.Surface((game_area_width, screen_height))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    center_x = game_area_width // 2
    y_start = 50
    
    # 좌측 패널: 상인 이미지 및 정보
    IMAGE_SIZE = 200
    player_image_scaled = pygame.transform.scale(player.image_original, (IMAGE_SIZE, IMAGE_SIZE))
    
    LEFT_PANEL_WIDTH = game_area_width // 2 - 50
    LEFT_START_X = padding * 2

    # 과거 쌀 시장 가격 표시
    past_price_text = font.render("과거 쌀 시장 가격: 100 냥", True, GOLD)
    
    padding_x = 25
    padding_y = 12
    text_w, text_h = past_price_text.get_size()
    
    past_price_x = LEFT_START_X + LEFT_PANEL_WIDTH // 2 - text_w // 2
    past_price_y = y_start 

    past_price_bg_rect = pygame.Rect(
        past_price_x - padding_x, past_price_y - padding_y,
        text_w + 2 * padding_x, text_h + 2 * padding_y
    )
    pygame.draw.rect(screen, DARK_WOOD, past_price_bg_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD, past_price_bg_rect, 3, border_radius=5)
    screen.blit(past_price_text, (past_price_x, past_price_y))
    
    # 상인 이미지 및 이름
    image_display_y = past_price_bg_rect.bottom + 50
    image_display_x = LEFT_START_X + LEFT_PANEL_WIDTH // 2 - IMAGE_SIZE // 2

    screen.blit(player_image_scaled, (image_display_x, image_display_y))

    name_surf = font.render(player.name, True, TEXT_COLOR)
    name_x = LEFT_START_X + LEFT_PANEL_WIDTH // 2 - name_surf.get_width() // 2
    screen.blit(name_surf, (name_x, image_display_y + IMAGE_SIZE + 10))
    
    # 우측 패널: 베팅 입력
    RIGHT_START_X = game_area_width // 2 + 50 
    RIGHT_PANEL_WIDTH = game_area_width - RIGHT_START_X - padding
    
    y_current = y_start
    title = font.render(f"[{player.name}] 쌀 거래 베팅", True, GOLD)
    title_x = RIGHT_START_X + RIGHT_PANEL_WIDTH // 2 - title.get_width() // 2 
    screen.blit(title, (title_x, y_current))
    y_current += 50

    # 매수/매도 버튼
    BUTTON_WIDTH = 120
    BUTTON_GAP = 20
    TOTAL_BUTTONS_WIDTH = (BUTTON_WIDTH * 2) + BUTTON_GAP
    buttons_set_start_x = RIGHT_START_X + (RIGHT_PANEL_WIDTH // 2) - (TOTAL_BUTTONS_WIDTH // 2)
    
    buy_btn.rect.x = buttons_set_start_x
    sell_btn.rect.x = buttons_set_start_x + BUTTON_WIDTH + BUTTON_GAP
    buy_btn.rect.y = y_current
    sell_btn.rect.y = y_current
    
    mouse_pos = pygame.mouse.get_pos()
    
    if player.bet_type == "매수":
        buy_btn.color = RED
    elif buy_btn.rect.collidepoint(mouse_pos):
        buy_btn.color = RED
    else:
        buy_btn.color = LIGHT_GRAY

    if player.bet_type == "매도":
        sell_btn.color = BLUE
    elif sell_btn.rect.collidepoint(mouse_pos):
        sell_btn.color = BLUE
    else:
        sell_btn.color = LIGHT_GRAY

    buy_btn.draw(screen, font, TEXT_COLOR)
    sell_btn.draw(screen, font, TEXT_COLOR)
    y_current += 60

    # 예측 가격 입력
    price_text = font.render("예측 가격:", True, WHITE)
    screen.blit(price_text, (RIGHT_START_X - 20, y_current + 10))
    price_box = pygame.Rect(RIGHT_START_X + 130, y_current, 200, 40)
    pygame.draw.rect(screen, WHITE, price_box, 2)
    if active_input == "price": pygame.draw.rect(screen, GOLD, price_box, 4)
    
    price_value = font.render(input_price + " 냥", True, WHITE)
    price_text_y = price_box.y + (price_box.height // 2) - (price_value.get_height() // 2)
    screen.blit(price_value, (price_box.x + 10, price_text_y))
    y_current += 60

    # 수량 입력
    quantity_text = font.render("수량:", True, WHITE)
    screen.blit(quantity_text, (RIGHT_START_X - 20, y_current + 10))
    quantity_box = pygame.Rect(RIGHT_START_X + 130, y_current, 200, 40)
    pygame.draw.rect(screen, WHITE, quantity_box, 2)
    if active_input == "quantity": pygame.draw.rect(screen, GOLD, quantity_box, 4)
    
    quantity_value = font.render(input_quantity + " 가마", True, WHITE)
    quantity_text_y = quantity_box.y + (quantity_box.height // 2) - (quantity_value.get_height() // 2)
    screen.blit(quantity_value, (quantity_box.x + 10, quantity_text_y))
    y_current += 80

    # 베팅 완료 버튼
    FINISH_BUTTON_WIDTH = 200
    finish_btn.rect.x = RIGHT_START_X + (RIGHT_PANEL_WIDTH // 2) - (FINISH_BUTTON_WIDTH // 2) 
    finish_btn.rect.y = y_current
    finish_btn.color = LIGHT_GRAY
    finish_btn.draw(screen, font, TEXT_COLOR)
    
    # 입력 박스 위치 반환 (클릭 감지용)
    return {
        'price_box': price_box,
        'quantity_box': quantity_box
    }

def draw_results(screen, players, final_price, result_btn, game_area_width, 
                 screen_height, font, small_font, colors):
    """결과 화면 그리기"""
    BLACK = colors['BLACK']
    GOLD = colors['GOLD']
    DARK_WOOD = colors['DARK_WOOD']
    WHITE = colors['WHITE']
    RED = colors['RED']
    BLUE = colors['BLUE']
    TEXT_COLOR = colors['TEXT_COLOR']
    
    overlay = pygame.Surface((game_area_width, screen_height))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    center_x = game_area_width // 2
    y_start = 100

    title = font.render("- 최종 정산 결과 -", True, TEXT_COLOR)
    screen.blit(title, (center_x - title.get_width() // 2, y_start))
    y_start += 75

    price_text = font.render(f"금일 최종 쌀 시장 가격: {final_price} 냥", True, GOLD) 
    padding_x = 30
    padding_y = 15
    text_w, text_h = price_text.get_size()
    text_x = center_x - text_w // 2
    text_y = y_start 
    
    background_rect = pygame.Rect(
        text_x - padding_x, text_y - padding_y,
        text_w + 2 * padding_x, text_h + 2 * padding_y
    )
    pygame.draw.rect(screen, DARK_WOOD, background_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD, background_rect, 3, border_radius=5)
    screen.blit(price_text, (text_x, text_y)) 
    y_start += text_h + 2 * padding_y + 10

    header = small_font.render("상인 이름 | 베팅 가격 | 유형 | 수량 | 최종 손익", True, WHITE)
    screen.blit(header, (center_x - header.get_width() // 2, y_start))
    y_start += 30

    sorted_players = sorted(players, key=lambda p: p.profit, reverse=True)

    for player in sorted_players:
        color = RED if player.profit >= 0 else BLUE

        result_line = font.render(
            f"{player.name} | {player.bet_price} 냥 | {player.bet_type} | {player.bet_quantity} 가마 | {player.profit} 냥",
            True, color
        )
        screen.blit(result_line, (center_x - result_line.get_width() // 2, y_start))
        y_start += 40

    winner_text = font.render(f"-승자- : {sorted_players[0].name} (최종 손익: {sorted_players[0].profit} 냥)", True, TEXT_COLOR)
    screen.blit(winner_text, (center_x - winner_text.get_width() // 2, y_start + 40))

    result_btn.rect.y = screen_height - 100
    result_btn.draw(screen, font, TEXT_COLOR)