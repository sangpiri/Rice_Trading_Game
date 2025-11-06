# config/__init__.py
"""게임 설정 및 데이터 모듈"""

from .game_data import (
    NPC_POSITIONS,
    TARGET_NPCS,
    get_player_start_positions,
    get_market_position
)

__all__ = [
    'NPC_POSITIONS',
    'TARGET_NPCS',
    'get_player_start_positions',
    'get_market_position'
]