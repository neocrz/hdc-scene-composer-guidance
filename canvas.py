# canvas.py

import uuid
from typing import Dict, Any, Tuple
import numpy as np
import config

class CanvasObject:
    """Represents a single object placed on the canvas."""
    def __init__(self,
                 shape: str,
                 color: str,
                 size_label: str,
                 position_xy: Tuple[float, float],
                 size_val: float = config.DEFAULT_SHAPE_SIZE_VISUAL):
        """
        Initializes a CanvasObject.

        Args:
            shape: The shape of the object (e.g., 'circle').
            color: The color of the object (e.g., 'red').
            size_label: The conceptual size (e.g., 'medium').
            position_xy: The (x, y) coordinates of the object's center on the canvas.
            size_val: The numerical size (e.g., radius or side length) for visualization.
        """
        self.obj_id: str = f"canvas_{uuid.uuid4().hex[:8]}" # A unique ID for this instance
        self.shape = shape
        self.color = color
        self.size_label = size_label
        self.position_xy = position_xy
        self.size_val = size_val

        # These are populated by the SceneEncoder to cache HDC representations
        self.conceptual_properties_hv: np.ndarray | None = None
        self.full_object_hv: np.ndarray | None = None

    def get_properties_dict(self) -> Dict[str, str]:
        """Returns a dictionary of the object's conceptual properties."""
        return {
            "shape": self.shape,
            "color": self.color,
            "size": self.size_label
        }

    def __repr__(self) -> str:
        return (f"CanvasObject(id={self.obj_id}, shape='{self.shape}', color='{self.color}', "
                f"size='{self.size_label}', pos={self.position_xy})")

class Canvas:
    """
    Manages the state of all objects in the 2D scene.
    It holds the data, not the visualization itself.
    """
    def __init__(self):
        """Initializes an empty canvas."""
        self.objects: Dict[str, CanvasObject] = {}

    def add_object(self, canvas_obj: CanvasObject) -> str:
        """Adds a CanvasObject to the scene."""
        if not isinstance(canvas_obj, CanvasObject):
            raise TypeError("Can only add CanvasObject instances to the canvas.")
        
        self.objects[canvas_obj.obj_id] = canvas_obj
        if config.VERBOSE_LEVEL > 0:
            print(f"Canvas: Added {canvas_obj}")
        return canvas_obj.obj_id

    def remove_object(self, obj_id: str) -> CanvasObject | None:
        """Removes an object from the scene by its ID."""
        removed_obj = self.objects.pop(obj_id, None)
        if removed_obj and config.VERBOSE_LEVEL > 0:
            print(f"Canvas: Removed {removed_obj}")
        return removed_obj
    
    def get_object(self, obj_id: str) -> CanvasObject | None:
        """Retrieves an object by its ID."""
        return self.objects.get(obj_id)

    def move_object(self, obj_id: str, new_position_xy: Tuple[float, float]):
        """Updates the position of an object."""
        obj = self.get_object(obj_id)
        if obj:
            obj.position_xy = new_position_xy
            if config.VERBOSE_LEVEL > 1:
                print(f"Canvas: Moved {obj_id} to {new_position_xy}")
        else:
            print(f"Warning: Attempted to move non-existent object with id {obj_id}")
            
    def change_object_color(self, obj_id: str, new_color: str):
        """Updates the color of an object."""
        obj = self.get_object(obj_id)
        if obj:
            obj.color = new_color
            if config.VERBOSE_LEVEL > 1:
                print(f"Canvas: Changed color of {obj_id} to {new_color}")
        else:
            print(f"Warning: Attempted to change color of non-existent object with id {obj_id}")

    def clear(self):
        """Removes all objects from the canvas."""
        self.objects.clear()
        if config.VERBOSE_LEVEL > 0:
            print("Canvas: Cleared all objects.")

    def get_all_objects(self) -> list[CanvasObject]:
        """Returns a list of all CanvasObject instances on the canvas."""
        return list(self.objects.values())

    def __repr__(self) -> str:
        if not self.objects:
            return "Canvas(empty)"
        obj_reprs = "\n  ".join(repr(obj) for obj in self.get_all_objects())
        return f"Canvas with {len(self.objects)} objects:\n  {obj_reprs}"
