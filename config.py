# config.py

# --- HDC Parameters ---
DIMENSIONALITY = 10000  # Dimensionality of hypervectors
VECTOR_TYPE = 'BINARY'   # 'BINARY' or 'BIPOLAR' (-1, 1) # TODO: 'DENSE' is not implemented
RANDOM_SEED = 45         # For reproducibility

# --- Lexicon amd Encoding ---
CONCEPT_SIMILARITY_THRESHOLD = 0.15 # Minimum similarity to consider concepts related for some operations
OBJECT_MATCH_THRESHOLD = 0.20 # Minimum similarity to consider a canvas object matching a target concept

# --- Canvas Parameters ---
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CANVAS_BACKGROUND_COLOR = "white"

# For conceptual positions
# These are just labels; their actual HV representation is in the lexicon
CONCEPTUAL_POSITIONS = {
    "center": (0.5, 0.5), # Relative coordinates (0-1)
    "top_left": (0.25, 0.25),
    "top_right": (0.75, 0.25),
    "bottom_left": (0.25, 0.75),
    "bottom_right": (0.75, 0.75),
    "top_center": (0.5, 0.25),
    "bottom_center": (0.5, 0.75),
    "middle_left": (0.25, 0.5),
    "middle_right": (0.75, 0.5),
}
# grid of HVs for finer position encoding
POSITION_GRID_CELLS_X = 10
POSITION_GRID_CELLS_Y = 10


# --- Agent Parameters ---
AGENT_MOVE_STEP_SIZE_ABS = 20 # Absolute pixel step for MOVE actions if not given a direct target
AGENT_MOVE_STEP_SIZE_REL = 0.05 # Relative (to canvas dimension) step size

# --- Guidance System & Main Loop ---
MAX_ITERATIONS = 50
SIMILARITY_TARGET_THRESHOLD = 0.85 # Overall scene similarity to stop

# --- Visualization ---
SHAPE_VISUAL_PROPERTIES = {
    "circle": {"outline": "black"},
    "square": {"outline": "black"},
    "triangle": {"outline": "black"},
}
DEFAULT_SHAPE_SIZE_VISUAL = 30 # Default visual size for 'medium'

VERBOSE_LEVEL = 2 # 0: None, 1: Basic, 2: Detailed HDC ops
