# agent.py

from typing import Dict, Any, Tuple
import config
from canvas import Canvas

class Agent:
    """
    The Agent is responsible for executing actions on the canvas.
    It acts as a simple API between the GuidanceSystem's commands and the Canvas state.
    """
    def __init__(self, canvas: Canvas):
        """
        Initializes the Agent.

        Args:
            canvas: The Canvas instance the agent will act upon.
        """
        self.canvas = canvas

    def execute_action(self, action_command: Dict[str, Any]):
        """
        Parses and executes a structured action command.

        Args:
            action_command: A dictionary specifying the action and its parameters.
                            Example: {'action': 'ADD', 'params': {...}}
        """
        action_type = action_command.get('action')
        params = action_command.get('params', {})

        if config.VERBOSE_LEVEL > 0:
            print(f"Agent executing: {action_command}")

        if action_type == "ADD":
            self._action_add(params)
        elif action_type == "MOVE":
            self._action_move(params)
        elif action_type == "REMOVE":
            self._action_remove(params)
        elif action_type == "CHANGE_COLOR":
            self._action_change_color(params)
        else:
            print(f"Warning: Agent received unknown action type '{action_type}'")

    def _action_add(self, params: Dict[str, Any]):
        """Executes the ADD action."""
        try:
            from canvas import CanvasObject # Late import to avoid circular dependency issues
            
            size_label = params.get('size', 'medium')
            size_map = {'small': 0.5, 'medium': 1.0, 'large': 1.5}
            size_val = config.DEFAULT_SHAPE_SIZE_VISUAL * size_map.get(size_label, 1.0)
            
            new_obj = CanvasObject(
                shape=params['shape'],
                color=params.get('color', 'black'),
                size_label=size_label,
                position_xy=params['position_xy'],
                size_val=size_val
            )
            self.canvas.add_object(new_obj)
        except KeyError as e:
            print(f"Error executing ADD action: Missing parameter {e}")
        except Exception as e:
            print(f"An unexpected error occurred during ADD action: {e}")

    def _action_move(self, params: Dict[str, Any]):
        """Executes the MOVE action."""
        try:
            obj_id = params['object_id']
            new_position = params['new_position_xy']
            self.canvas.move_object(obj_id, new_position)
        except KeyError as e:
            print(f"Error executing MOVE action: Missing parameter {e}")

    def _action_remove(self, params: Dict[str, Any]):
        """Executes the REMOVE action."""
        try:
            obj_id = params['object_id']
            self.canvas.remove_object(obj_id)
        except KeyError as e:
            print(f"Error executing REMOVE action: Missing parameter {e}")
            
    def _action_change_color(self, params: Dict[str, Any]):
        """Executes the CHANGE_COLOR action."""
        try:
            obj_id = params['object_id']
            new_color = params['new_color']
            self.canvas.change_object_color(obj_id, new_color)
        except KeyError as e:
            print(f"Error executing CHANGE_COLOR action: Missing parameter {e}")