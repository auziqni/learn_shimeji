# Animation package for Shimeji Desktop Pets
# Contains animation system components and sprite management

from .animation_manager import AnimationManager
from .action_types.base_action_type import BaseActionType
from .action_types.stay_animation import StayAnimation

__all__ = [
    'AnimationManager',
    'BaseActionType', 
    'StayAnimation'
] 