# scene_encoder.py

import numpy as np
from typing import Dict, Any, List

import config
import hdc_utils
from lexicon import Lexicon
from canvas import Canvas, CanvasObject

class SceneEncoder:
    def __init__(self, lexicon: Lexicon):
        """
        Initializes the SceneEncoder.

        Args:
            lexicon: An initialized Lexicon instance.
        """
        self.lexicon = lexicon
        self.hdc_utils = hdc_utils

    def encode_object_properties(self, properties_dict: Dict[str, str]) -> np.ndarray:
        """
        Encodes the conceptual properties of an object (shape, color, size) into a single HV.

        Args:
            properties_dict: A dictionary like {'shape': 'circle', 'color': 'red', 'size': 'large'}.

        Returns:
            A single hypervector representing the bound properties.
        """
        shape_hv = self.lexicon.get_hv(properties_dict.get('shape', 'NONE'))
        color_hv = self.lexicon.get_hv(properties_dict.get('color', 'NONE'))
        size_hv = self.lexicon.get_hv(properties_dict.get('size', 'NONE'))

        bound_hv = self.hdc_utils.bind(shape_hv, color_hv)
        bound_hv = self.hdc_utils.bind(bound_hv, size_hv)
        
        return bound_hv

    def encode_canvas_object(self, canvas_obj: CanvasObject):
        """
        Encodes a single CanvasObject into a full hypervector (properties + position)
        and caches the results on the object itself to avoid recomputation.
        """
        # 1. Encode conceptual properties
        props_dict = canvas_obj.get_properties_dict()
        props_hv = self.encode_object_properties(props_dict)
        canvas_obj.conceptual_properties_hv = props_hv

        # 2. Encode position
        min_dist = float('inf')
        closest_pos_label = 'NONE'
        obj_pos = np.array(canvas_obj.position_xy)

        for label, rel_coords in config.CONCEPTUAL_POSITIONS.items():
            # Relative coords to absolute canvas coords
            abs_coords = (rel_coords[0] * config.CANVAS_WIDTH, rel_coords[1] * config.CANVAS_HEIGHT)
            dist = np.linalg.norm(obj_pos - np.array(abs_coords))
            if dist < min_dist:
                min_dist = dist
                closest_pos_label = label
        
        pos_hv = self.lexicon.get_hv(closest_pos_label)

        # 3. Bind properties and position
        full_obj_hv = self.hdc_utils.bind(props_hv, pos_hv)
        canvas_obj.full_object_hv = full_obj_hv # Cache the full HV

    def encode_canvas_state(self, canvas: Canvas) -> np.ndarray:
        """
        Encodes the entire state of the canvas into a single scene hypervector.

        Args:
            canvas: The Canvas instance to encode.

        Returns:
            A single hypervector representing the bundled state of all objects on the canvas.
        """
        all_object_hvs = []
        for obj in canvas.get_all_objects():
            # Ensure the object's HV is encoded and cached
            if obj.full_object_hv is None:
                self.encode_canvas_object(obj)
            all_object_hvs.append(obj.full_object_hv)

        if not all_object_hvs:
            # Return a specific "empty scene" HV or a zero vector
            return self.lexicon.get_hv("EMPTY_SCENE_ELEMENT")

        # Bundle all individual object HVs into a single scene representation
        current_scene_hv = self.hdc_utils.bundle(all_object_hvs)
        return current_scene_hv

    def encode_target_description(self, parsed_description: List[Dict[str, Any]]) -> np.ndarray:
        """
        Encodes a parsed scene description (from SceneParser) into a target scene hypervector.

        Args:
            parsed_description: A list of dictionaries representing conceptual objects.

        Returns:
            A single target hypervector for the entire scene.
        """
        target_object_hvs = {} # Store HVs for objects that might be referenced by others

        # Encode all objects with absolute positions
        for conceptual_obj in parsed_description:
            obj_id = conceptual_obj['id']
            
            # Encode properties (shape, color, size)
            props_hv = self.encode_object_properties(conceptual_obj)
            
            # If there's an absolute position, bind it now
            if 'position_abs' in conceptual_obj:
                pos_hv = self.lexicon.get_hv(conceptual_obj['position_abs'])
                full_obj_hv = self.hdc_utils.bind(props_hv, pos_hv)
                target_object_hvs[obj_id] = full_obj_hv

        # Second pass: Encode objects with relative positions (this is a simplification)
        
        for conceptual_obj in parsed_description:
            obj_id = conceptual_obj['id']
            if obj_id in target_object_hvs:
                continue

            if 'relation' in conceptual_obj:
                props_hv = self.encode_object_properties(conceptual_obj)
                target_object_hvs[obj_id] = props_hv
            else:
                # Object with no position or relation info
                props_hv = self.encode_object_properties(conceptual_obj)
                target_object_hvs[obj_id] = props_hv


        if not target_object_hvs:
            return self.lexicon.get_hv("EMPTY_SCENE_ELEMENT")

        # Bundle all conceptual object HVs into the final target scene HV
        final_target_hv = self.hdc_utils.bundle(list(target_object_hvs.values()))
        return final_target_hv
