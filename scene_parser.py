# scene_parser.py

import re
from typing import List, Dict, Any

class SceneParser:
    def __init__(self, lexicon):
        """
        Initializes the SceneParser with a lexicon to know which words are keywords.

        Args:
            lexicon: An instance of the Lexicon class.
        """
        self.lexicon = lexicon
        # Build regex patterns from the lexicon's known concepts... makes the parser adaptable when adding new shapes, colors, etc...
        self.shape_pattern = r'(' + '|'.join(self.lexicon.shapes) + r')'
        self.color_pattern = r'(' + '|'.join(self.lexicon.colors) + r')'
        self.size_pattern = r'(' + '|'.join(self.lexicon.sizes) + r')'
        self.position_pattern = r'(' + '|'.join(self.lexicon.conceptual_positions_labels) + r')'
        self.relation_pattern = r'(' + '|'.join(self.lexicon.relations) + r')'

    def parse_description(self, description_text: str) -> List[Dict[str, Any]]:
        """
        Parses a full scene description into a list of conceptual objects.
        Example: "A large red circle in the center, with a small blue square to its left."

        Args:
            description_text: The string describing the scene.

        Returns:
            A list of dictionaries, where each dictionary represents a conceptual object
            with its properties and relations.
        """
        parsed_objects = []
        object_id_counter = 0

        # Split the description by clauses, often separated by commas or "and" or "with"
        # A simple split by comma is a good first approximation.
        clauses = re.split(r',| with | and ', description_text)

        # Context for relational phrases like "to its left"
        last_object_id = None

        for i, clause in enumerate(clauses):
            clause = clause.strip()
            if not clause:
                continue

            conceptual_object = self._parse_clause(clause)
            
            if conceptual_object:
                # Assign a unique ID to each object for referencing
                obj_id = f"obj_{object_id_counter}"
                conceptual_object['id'] = obj_id

                # Handle simple "it" pronoun reference for relations
                if conceptual_object.get('relation') and 'reference_obj' not in conceptual_object['relation']:
                    if last_object_id:
                        conceptual_object['relation']['reference_obj_id'] = last_object_id
                    else:
                        print(f"Warning: Relational clause '{clause}' has no clear reference object. Ignoring relation.")
                        del conceptual_object['relation']

                parsed_objects.append(conceptual_object)
                last_object_id = obj_id
                object_id_counter += 1

        return parsed_objects


    def _parse_clause(self, clause_text: str) -> Dict[str, Any] | None:
        """
        Parses a single clause describing one object.
        Example: "a large red circle in the center"
        Example: "a small blue square to its left"
        """
        clause_text = clause_text.lower()
        
        # --- Find Core Object Properties ---
        shape_match = re.search(self.shape_pattern, clause_text)
        if not shape_match:
            return None
        
        conceptual_object = {'type': 'conceptual_object'}
        conceptual_object['shape'] = shape_match.group(1)

        # Find color, size
        color_match = re.search(self.color_pattern, clause_text)
        conceptual_object['color'] = color_match.group(1) if color_match else 'black' # Default color

        size_match = re.search(self.size_pattern, clause_text)
        conceptual_object['size'] = size_match.group(1) if size_match else 'medium' # Default size

        # --- Find Position or Relation ---
        position_match = re.search(self.position_pattern, clause_text)
        
        # Determine relation type based on more flexible patterns
        found_relation_type = None
        for rel_concept in self.lexicon.relations:
            current_rel_pattern = ""
            if rel_concept == "left_of":
                current_rel_pattern = r'\b(left_of|to (?:its|the) left)\b'
            elif rel_concept == "right_of":
                current_rel_pattern = r'\b(right_of|to (?:its|the) right)\b'
            elif rel_concept == "above":
                current_rel_pattern = r'\babove\b'
            elif rel_concept == "below":
                current_rel_pattern = r'\bbelow\b'
            elif rel_concept == "near":
                current_rel_pattern = r'\bnear\b'
            elif rel_concept == "overlapping_with":
                current_rel_pattern = r'\boverlapping_with\b'
            
            if current_rel_pattern:
                if re.search(current_rel_pattern, clause_text):
                    found_relation_type = rel_concept
                    break

        if position_match:
            conceptual_object['position_abs'] = position_match.group(1)
        
        # If a relation is found and no absolute position was set for this object
        if found_relation_type and 'position_abs' not in conceptual_object:
            relation_details = {'type': found_relation_type}
            
            # Simple pronoun check ("to its left", "above it")
            if re.search(r'\b(its?|the)\b', clause_text):
                # The reference object will be filled in by the main parse_description method
                pass
            
            conceptual_object['relation'] = relation_details
            
        return conceptual_object
