# hdc_utils.py

import numpy as np
import config

# Initialize random seed for reproducibility
if config.RANDOM_SEED is not None:
    np.random.seed(config.RANDOM_SEED)

def generate_random_hv(dimensionality: int, vector_type: str = config.VECTOR_TYPE) -> np.ndarray:
    """
    Generates a random hypervector.

    Args:
        dimensionality: The number of dimensions for the hypervector.
        vector_type: 'BINARY' (0,1), 'BIPOLAR' (-1,1).

    Returns:
        A NumPy array representing the hypervector.
    """
    if vector_type == 'BINARY':
        return np.random.randint(0, 2, size=dimensionality, dtype=np.int8)
    elif vector_type == 'BIPOLAR':
        return np.random.choice([-1, 1], size=dimensionality, dtype=np.int8)
    # TODO: maybe implement DENSE vectors in the future
    # elif vector_type == 'DENSE':
    #     return np.random.randn(dimensionality)
    else:
        raise ValueError(f"Unsupported vector_type: {vector_type}")

def bind(hv1: np.ndarray, hv2: np.ndarray, vector_type: str = config.VECTOR_TYPE) -> np.ndarray:
    """
    Binds two hypervectors using element-wise XOR for BINARY/BIPOLAR.
    This operation is its own inverse.

    Args:
        hv1: The first hypervector.
        hv2: The second hypervector.
        vector_type: The type of vectors being bound.

    Returns:
        The resulting bound hypervector.
    """
    if hv1.shape != hv2.shape:
        raise ValueError("Hypervectors must have the same dimensionality to be bound.")
    if vector_type == 'BINARY':
        return np.bitwise_xor(hv1, hv2)
    elif vector_type == 'BIPOLAR':
        return hv1 * hv2
    else:
        raise ValueError(f"Binding not implemented for vector_type: {vector_type}")

def bundle(hvs: list[np.ndarray], vector_type: str = config.VECTOR_TYPE) -> np.ndarray:
    """
    Bundles a list of hypervectors using element-wise majority sum for BINARY/BIPOLAR.

    Args:
        hvs: A list of hypervectors to bundle.
        vector_type: The type of vectors being bundled.

    Returns:
        The resulting bundled hypervector.
    """
    if not hvs:
        return np.zeros(config.DIMENSIONALITY, dtype=np.int8 if vector_type != 'DENSE' else np.float32)


    dimensionality = hvs[0].shape[0]
    for hv in hvs:
        if hv.shape[0] != dimensionality:
            raise ValueError("All hypervectors in a bundle must have the same dimensionality.")

    if vector_type == 'BINARY':
        sum_vector = np.sum(hvs, axis=0, dtype=np.int16)
        threshold = len(hvs) / 2.0
        bundled_hv = (sum_vector > threshold).astype(np.int8)
        return bundled_hv
    elif vector_type == 'BIPOLAR':
        sum_vector = np.sum(hvs, axis=0, dtype=np.int16)
        bundled_hv = np.sign(sum_vector).astype(np.int8)
        zero_indices = (bundled_hv == 0)
        if np.any(zero_indices):
            bundled_hv[zero_indices] = np.random.choice([-1, 1], size=np.sum(zero_indices))
        return bundled_hv
    else:
        raise ValueError(f"Bundling not implemented for vector_type: {vector_type}")

def cosine_similarity(hv1: np.ndarray, hv2: np.ndarray) -> float:
    """
    Computes the cosine similarity between two hypervectors.
    Assumes vectors are 1D.
    """
    if hv1.shape != hv2.shape:
        if np.all(hv1 == 0) or np.all(hv2 == 0):
            return 0.0
        raise ValueError("Hypervectors must have the same dimensionality for cosine similarity.")
    
    if np.all(hv1 == 0) and np.all(hv2 == 0): # Both zero
        return 1.0
    if np.all(hv1 == 0) or np.all(hv2 == 0): # One zero
        return 0.0

    # Cast to float64 for robust numerical calc
    hv1_float = hv1.astype(np.float64)
    hv2_float = hv2.astype(np.float64)

    dot_product = np.dot(hv1_float, hv2_float)
    norm_hv1 = np.linalg.norm(hv1_float)
    norm_hv2 = np.linalg.norm(hv2_float)

    if norm_hv1 == 0 or norm_hv2 == 0:
        return 0.0  # Avoid division by zero
    
    similarity = dot_product / (norm_hv1 * norm_hv2)
    return similarity

def hamming_similarity(hv1: np.ndarray, hv2: np.ndarray) -> float:
    """
    Computes Hamming similarity (fraction of matching bits) for BINARY vectors.
    1 - normalized Hamming distance.
    """
    if config.VECTOR_TYPE != 'BINARY':
        print("Warning: Hamming similarity typically used for binary vectors.")

    if hv1.shape != hv2.shape:
        raise ValueError("Hypervectors must have the same dimensionality for Hamming similarity.")
    
    dimensionality = hv1.shape[0]
    if dimensionality == 0:
        return 1.0

    distance = np.sum(hv1 != hv2)
    similarity = 1.0 - (distance / dimensionality)
    return similarity

def get_similarity(hv1: np.ndarray, hv2: np.ndarray) -> float:
    """
    Wrapper to get similarity based on vector type.
    Currently uses cosine for all, but could select based on config.
    """
    return cosine_similarity(hv1, hv2)


def permute(hv: np.ndarray, n: int = 1, inverse=False) -> np.ndarray:
    """
    Performs a cyclic permutation (roll) on the hypervector.
    This is useful for encoding sequences or roles.
    Permutation by n positions. If inverse is True, permutes by -n.

    Args:
        hv: The hypervector to permute.
        n: The number of positions to roll.
        inverse: If True, rolls in the opposite direction.

    Returns:
        The permuted hypervector.
    """
    shift = n if not inverse else -n
    return np.roll(hv, shift)
