# lexicon.py

import numpy as np
import config
import hdc_utils

class Lexicon:
    def __init__(self, dimensionality: int = config.DIMENSIONALITY, vector_type: str = config.VECTOR_TYPE):
        """
        Initializes the Lexicon, creating hypervectors for all primitive concepts.

        Args:
            dimensionality: The dimensionality of the hypervectors.
            vector_type: The type of hypervectors ('BINARY', 'BIPOLAR').
        """
        self.dimensionality = dimensionality
        self.vector_type = vector_type
        self.primitive_hvs = {}

        if config.VERBOSE_LEVEL > 0:
            print(f"Initializing Lexicon with D={dimensionality}, Type={vector_type}...")

        # --- Primitive Concepts ---
        # Shapes
        self.shapes = ["circle", "square", "triangle"]
        # Colors
        self.colors = ["red", "blue", "green", "yellow", "black", "purple"] # Added more colors
        # Relative Sizes
        self.sizes = ["small", "medium", "large"]
        # Spatial Relations (for describing relationships between objects)
        self.relations = ["above", "below", "left_of", "right_of", "near", "overlapping_with"]
        
        # Conceptual Absolute Positions (these are labels; their actual HVs are generated)
        # Their interpretation as coordinates is in config.CONCEPTUAL_POSITIONS
        self.conceptual_positions_labels = list(config.CONCEPTUAL_POSITIONS.keys())

        # Placeholder/Special HVs
        self.special_hvs_labels = ["UNKNOWN_CONCEPT", "EMPTY_SCENE_ELEMENT"]

        self._generate_primitive_hvs()

        # Grid-based position HVs if that strategy is chosen
        self.position_grid_hvs = None
        if hasattr(config, 'POSITION_GRID_CELLS_X') and hasattr(config, 'POSITION_GRID_CELLS_Y'):
             self._generate_position_grid_hvs(config.POSITION_GRID_CELLS_X, config.POSITION_GRID_CELLS_Y)

        if config.VERBOSE_LEVEL > 0:
            print("Lexicon initialized with primitive HVs.")
            if self.position_grid_hvs is not None:
                print(f"Position grid HVs generated for {config.POSITION_GRID_CELLS_X}x{config.POSITION_GRID_CELLS_Y} grid.")


    def _generate_primitive_hvs(self):
        """Generates and stores hypervectors for all defined primitive concepts."""
        all_concepts = (
            self.shapes +
            self.colors +
            self.sizes +
            self.relations +
            self.conceptual_positions_labels +
            self.special_hvs_labels
        )

        for concept_label in all_concepts:
            if concept_label not in self.primitive_hvs: # Avoid regeneration if called multiple times
                self.primitive_hvs[concept_label] = hdc_utils.generate_random_hv(
                    self.dimensionality, self.vector_type
                )
                if config.VERBOSE_LEVEL > 1:
                    print(f"  Generated HV for: {concept_label}")
        
        if "NONE" not in self.primitive_hvs:
             self.primitive_hvs["NONE"] = hdc_utils.generate_random_hv(self.dimensionality, self.vector_type)


    def _generate_position_grid_hvs(self, grid_x_cells: int, grid_y_cells: int):
        """
        Generates unique HVs for each cell in a 2D grid.
        These can be used for finer-grained spatial encoding.
        """
        self.position_grid_hvs = {} # Store as dict: (x_idx, y_idx) -> HV
        for r in range(grid_y_cells): # row index
            for c in range(grid_x_cells): # col index
                cell_label = f"pos_grid_{r}_{c}" # Unique label for generation
                # Generate a unique HV for each cell.
                self.position_grid_hvs[(c, r)] = hdc_utils.generate_random_hv(
                    self.dimensionality, self.vector_type
                )
        if config.VERBOSE_LEVEL > 1:
            print(f"  Generated {len(self.position_grid_hvs)} HVs for position grid.")

    def get_hv(self, concept_label: str) -> np.ndarray | None:
        """
        Retrieves the hypervector for a given concept label.

        Args:
            concept_label: The string label of the concept.

        Returns:
            The NumPy array representing the hypervector, or None if not found.
        """
        return self.primitive_hvs.get(concept_label, self.primitive_hvs.get("UNKNOWN_CONCEPT"))

    def get_position_grid_hv(self, x_cell_idx: int, y_cell_idx: int) -> np.ndarray | None:
        """
        Retrieves the hypervector for a specific cell in the position grid.

        Args:
            x_cell_idx: The x-index of the grid cell.
            y_cell_idx: The y-index of the grid cell.

        Returns:
            The NumPy array for the grid cell HV, or None if grid not used or index out of bounds.
        """
        if self.position_grid_hvs is None:
            if config.VERBOSE_LEVEL > 0:
                print("Warning: Position grid HVs requested but not generated/enabled in config.")
            return self.get_hv("UNKNOWN_CONCEPT")
        
        hv = self.position_grid_hvs.get((x_cell_idx, y_cell_idx))
        if hv is None and config.VERBOSE_LEVEL > 0:
            print(f"Warning: No HV found for grid cell ({x_cell_idx}, {y_cell_idx}). Returning UNKNOWN_CONCEPT.")
            return self.get_hv("UNKNOWN_CONCEPT")
        return hv
        
    def get_all_primitive_labels(self) -> list[str]:
        """Returns a list of all defined primitive concept labels."""
        return list(self.primitive_hvs.keys())