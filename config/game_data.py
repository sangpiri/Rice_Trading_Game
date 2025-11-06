"""게임 데이터 (NPC 위치 등)"""

# NPC 위치 정보 (고정 데이터)
NPC_POSITIONS = [
    (50, 650), (150, 700), (250, 700), (50, 500), (150, 550),
    (250, 600), (350, 650), (700, 650), (600, 700), (500, 700),
    (750, 500), (650, 550), (550, 600), (450, 650), (200, 200),
    (350, 150), (450, 200), (600, 250), (100, 300), (500, 350),
    (700, 300),
]

# 플레이어 시작 위치 (화면 크기 기반 계산은 main.py에서)
def get_player_start_positions(screen_height, player_size, game_area_width):
    """플레이어 시작 위치 계산"""
    return [
        (50, screen_height - player_size - 50),
        (game_area_width - player_size - 50, screen_height - player_size - 50),
        (game_area_width // 2 - player_size // 8, 110)
    ]

# 마켓 위치 계산
def get_market_position(game_area_width, screen_height, step_size):
    """마켓 위치 계산"""
    return (game_area_width // 2 - step_size + 10, screen_height // 2 + 20)

# 타겟 NPC 수
TARGET_NPCS = 7