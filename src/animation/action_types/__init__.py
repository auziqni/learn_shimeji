# Action Types package for Shimeji Desktop Pets
# Contains specific animation action type handlers

from .base_action_type import BaseActionType
from .stay_animation import StayAnimation

__all__ = [
    'BaseActionType',
    'StayAnimation'
] 