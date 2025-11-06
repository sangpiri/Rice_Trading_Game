"""플레이어 클래스"""
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, start_pos, name, initial_money=2000, player_size=50):
        super().__init__()
        self.player_size = player_size
        
        try:
            self.image_original = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            print(f"이미지 로드 오류: {image_path}. 기본 표면 사용.")
            self.image_original = pygame.Surface([player_size, player_size])
            self.image_original.fill((50, 50, 200))  # BLUE

        self.image = pygame.transform.scale(self.image_original, (player_size, player_size))
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos
        self.name = name
        self.money = initial_money
        self.rice_amount = 0
        self.collected_info = []
        self.npcs_met = 0
        self.trade_done = False
        self.can_bet = False
        self.profit = 0

        self.bet_price = 0
        self.bet_quantity = 0
        self.bet_type = "매수"

    def move(self, dx, dy, game_area_width, screen_height):
        """플레이어 이동 (경계 체크 포함)"""
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        
        if 0 <= new_x <= game_area_width - self.player_size and 0 <= new_y <= screen_height - self.player_size:
            self.rect.x = new_x
            self.rect.y = new_y