"""마켓 클래스"""
import pygame

class Market(pygame.sprite.Sprite):
    def __init__(self, pos, step_size=50):
        super().__init__()
        
        size = step_size * 2
        radius = size // 2
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        
        # 색상 정의 (main.py의 색상 사용)
        DARK_GRAY = (40, 40, 40)
        GOLD = (218, 165, 32)
        
        pygame.draw.circle(self.image, DARK_GRAY, (radius, radius), radius)
        pygame.draw.circle(self.image, GOLD, (radius, radius), radius, 4)
        
        self.image.set_alpha(150) 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos