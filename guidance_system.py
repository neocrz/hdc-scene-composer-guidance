# guidance_system.py

from typing import Dict, Any, List, Tuple
import numpy as np

import config
import hdc_utils
from lexicon import Lexicon
from scene_encoder import SceneEncoder
from canvas import Canvas, CanvasObject

class GuidanceSystem:
    """
    The core logic unit that compares target and current states
    and proposes actions to reconcile them.
    """
    def __init__(self, lexicon: Lexicon, scene_encoder: SceneEncoder, parsed_target_description: List[Dict[str, Any]]):
        """
        Initializes the Guidance System.

        Args:
            lexicon: An initialized Lexicon.
            scene_encoder: An initialized SceneEncoder.
            parsed_target_description: The structured output from SceneParser, representing the goal.
        """
        self.lexicon = lexicon
        self.scene_encoder = scene_encoder
        self.parsed_target_description = parsed_target_description
        self.hdc_utils = hdc_utils

    def _find_best_canvas_match(self,
                                target_props_hv: np.ndarray,
                                canvas: Canvas,
                                exclusion_ids: set) -> Tuple[CanvasObject | None, float]:
        """Finds the best matching object on canvas for a target properties HV, excluding already matched objects."""
        best_match = None
        max_similarity = -1.0

        for canvas_obj in canvas.get_all_objects():
            if canvas_obj.obj_id in exclusion_ids:
                continue

            if canvas_obj.conceptual_properties_hv is None:
                self.scene_encoder.encode_canvas_object(canvas_obj)

            similarity = self.hdc_utils.get_similarity(target_props_hv, canvas_obj.conceptual_properties_hv)

            if similarity > max_similarity:
                max_similarity = similarity
                best_match = canvas_obj

        return best_match, max_similarity

    def propose_action(self, canvas: Canvas) -> Dict[str, Any] | None:
        """
        The main method to generate a single, corrective action command.

        Args:
            canvas: The current state of the canvas.

        Returns:
            An action command dictionary for the Agent, or None if the scene is considered complete.
        """
        target_to_canvas_map: Dict[str, Dict[str, Any]] = {}
        matched_canvas_ids = set()

        for target_obj_desc in self.parsed_target_description:
            target_id = target_obj_desc['id']
            target_props_hv = self.scene_encoder.encode_object_properties(target_obj_desc)
            canvas_match, similarity = self._find_best_canvas_match(target_props_hv, canvas, matched_canvas_ids)

            if canvas_match and similarity > config.OBJECT_MATCH_THRESHOLD:
                target_to_canvas_map[target_id] = {'canvas_obj': canvas_match, 'sim': similarity}
                matched_canvas_ids.add(canvas_match.obj_id)

        # --- Phase 1: Add Missing Core Objects ---
        for target_obj_desc in self.parsed_target_description:
            target_id = target_obj_desc['id']
            if target_id not in target_to_canvas_map:
                action_params = {
                    'shape': target_obj_desc['shape'],
                    'color': target_obj_desc.get('color', 'black'),
                    'size': target_obj_desc.get('size', 'medium'),
                }
                if 'position_abs' in target_obj_desc:
                    pos_label = target_obj_desc['position_abs']
                    rel_pos = config.CONCEPTUAL_POSITIONS.get(pos_label, (0.5, 0.5))
                    action_params['position_xy'] = (rel_pos[0] * config.CANVAS_WIDTH, rel_pos[1] * config.CANVAS_HEIGHT)
                else:
                    margin = 50
                    rand_x = np.random.randint(margin, config.CANVAS_WIDTH - margin)
                    rand_y = np.random.randint(margin, config.CANVAS_HEIGHT - margin)
                    action_params['position_xy'] = (rand_x, rand_y)
                
                return {"action": "ADD", "params": action_params}

        # --- Phase 2: Correct Positions of Existing Matched Objects ---
        for target_obj_desc in self.parsed_target_description:
            target_id = target_obj_desc['id']
            match_info = target_to_canvas_map.get(target_id)
            if not match_info: continue
            
            canvas_obj = match_info['canvas_obj']
            
            if 'position_abs' in target_obj_desc:
                target_pos_label = target_obj_desc['position_abs']
                rel_pos = config.CONCEPTUAL_POSITIONS.get(target_pos_label, (0.5, 0.5))
                target_pos_xy = (rel_pos[0] * config.CANVAS_WIDTH, rel_pos[1] * config.CANVAS_HEIGHT)
                dist = np.linalg.norm(np.array(canvas_obj.position_xy) - np.array(target_pos_xy))
                if dist > config.AGENT_MOVE_STEP_SIZE_ABS:
                    return {"action": "MOVE", "params": {"object_id": canvas_obj.obj_id, "new_position_xy": target_pos_xy}}

            elif 'relation' in target_obj_desc:
                relation_info = target_obj_desc['relation']
                ref_target_id = relation_info.get('reference_obj_id')
                if ref_target_id and ref_target_id in target_to_canvas_map:
                    ref_canvas_obj = target_to_canvas_map[ref_target_id]['canvas_obj']
                    offset = config.AGENT_MOVE_STEP_SIZE_ABS * 2
                    target_pos_xy = list(ref_canvas_obj.position_xy)
                    rel_type = relation_info['type']
                    
                    if rel_type == 'left_of': target_pos_xy[0] -= offset
                    elif rel_type == 'right_of': target_pos_xy[0] += offset
                    elif rel_type == 'above': target_pos_xy[1] -= offset
                    elif rel_type == 'below': target_pos_xy[1] += offset
                    
                    dist = np.linalg.norm(np.array(canvas_obj.position_xy) - np.array(target_pos_xy))
                    if dist > config.AGENT_MOVE_STEP_SIZE_ABS:
                        return {"action": "MOVE", "params": {"object_id": canvas_obj.obj_id, "new_position_xy": tuple(target_pos_xy)}}

        # --- Phase 3: Correct other properties (e.g., color) ---
        for target_obj_desc in self.parsed_target_description:
            target_id = target_obj_desc['id']
            match_info = target_to_canvas_map.get(target_id)
            if not match_info: continue
            
            canvas_obj = match_info['canvas_obj']
            target_color = target_obj_desc.get('color', 'black')
            
            if canvas_obj.color != target_color:
                return {"action": "CHANGE_COLOR", "params": {"object_id": canvas_obj.obj_id, "new_color": target_color}}

        return None
