# hdc-scene-composer-guidance

A proof-of-concept system that uses Hyperdimensional Computing (HDC) to guide an agent in iteratively constructing a 2D scene from a text description.

---

## Introduction

**HDC Scene Composer** is a proof-of-concept application demonstrating how Hyperdimensional Computing (HDC), a brain-inspired computational paradigm, can be used to guide a generative process. The system takes a natural language description of a 2D scene and iteratively constructs it on a canvas by proposing and executing a sequence of corrective actions.

This project serves as a palpable prototype for goal-directed generation, showcasing how a complex, compositional goal can be represented as a single high-dimensional vector and used to steer a simple agent towards a desired state, even from a random configuration.

![HDC Scene Composer In Action](assets/hdc-scene-composer-output1.gif)
- *a large green triangle at the bottom_left, with a medium purple circle to its right, and a small yellow square above the circle*

---

## Features

-   **Natural Language Parsing**: Interprets simple but compositional descriptions of scenes (e.g., "a large red circle in the center, with a small blue square to its left").
-   **Hyperdimensional Encoding**: Represents all concepts—shapes, colors, sizes, positions, and relations—as high-dimensional vectors (hypervectors).
-   **Goal-Oriented Guidance System**: The core of the project. It compares the desired target scene with the current state of the canvas and intelligently proposes one single, corrective action at a time.
-   **Robust Iterative Construction**: An agent executes the proposed actions (ADD, MOVE, CHANGE_COLOR) step-by-step. Objects without absolute positions are placed randomly, demonstrating the system's ability to guide them to their correct final state from an arbitrary starting point.
-   **Live Visualization**: Includes a `tkinter`-based GUI that allows you to watch the agent construct the scene in near real-time.
-   **GIF Generation**: Automatically saves the construction process as a GIF via a command-line flag to easily visualize and share the results.

---

## How It Works

The system operates on a closed-loop, "sense-act" cycle guided by HDC principles:

1.  **Parse & Encode Goal**: The input text description is first parsed into a structured list of conceptual objects and their relationships. This structured list is then encoded into a single `TARGET_SCENE_HV` (Target Scene Hypervector) using HDC operations (`bind` and `bundle`). This vector represents the complete goal state.
2.  **Sense & Encode Current State**: In each iteration, the system observes the objects currently on the canvas. It encodes this arrangement into a `CURRENT_SCENE_HV`.
3.  **Compare & Propose Action**: The `GuidanceSystem` compares the current state to the target goal. It doesn't just look at overall similarity; it intelligently identifies the most salient discrepancy (e.g., a missing object, an object in the wrong place) and proposes a single, concrete action.
4.  **Act & Repeat**: An `Agent` takes this proposed action (e.g., `{'action': 'MOVE', ...}`) and executes it, modifying the canvas. The loop then repeats until the `GuidanceSystem` determines that the current state matches the target, proposing no further actions.

This iterative correction process demonstrates a primitive but powerful form of generative guidance.

---

## Project Structure

The repository is organized into modular Python files, each with a specific responsibility:

-   `main.py`: The main entry point and orchestration loop for the system.
-   `guidance_system.py`: The "brain" of the operation; decides on the next best action.
-   `scene_encoder.py`: Handles the conversion of concepts and scenes into hypervectors.
-   `agent.py`: Executes actions (ADD, MOVE, etc.) on the canvas.
-   `canvas.py`: Defines the data structures for the canvas and the objects on it.
-   `scene_parser.py`: Parses the input text description into a structured format.
-   `lexicon.py`: Creates and stores the primitive hypervectors for all known concepts.
-   `hdc_utils.py`: Provides the core mathematical operations for HDC (binding, bundling, similarity).
-   `config.py`: Contains all global configuration parameters.
-   `next_steps.md`: Discusses how this prototype's principles can be applied to future work.

---

## How to Run

1.  **Prerequisites**:
    -   Python 3.x
    -   NumPy (`pip install numpy`)
    -   Pillow (`pip install Pillow`)
    -   `tkinter` is used for the visualizer and is typically included with Python. On some Linux distributions, you may need to install it separately (e.g., `sudo apt-get install python3-tk`).

2.  **Execution**:
    -   Clone the repository.
    -   Open `main.py` and modify the `TARGET_SCENE` variable at the bottom to describe the scene you want to generate.
    -   Run the script from your terminal:

    ```bash
    # To run with live visualization
    python main.py

    # To run and also save the process as a GIF
    python main.py --gif
    ```
    -   A `tkinter` window will appear and show the scene being constructed. If the `--gif` flag is used, a file named `assets/hdc-scene-composer-output.gif` will be saved in the root directory.

## More examples

![HDC Scene Composer In Action 2](assets/hdc-scene-composer-output2.gif)
- *"a large black square in the middle_left, with a medium red square to its right, and a small blue square to the right of the red square"*

![HDC Scene Composer In Action 3](assets/hdc-scene-composer-output3.gif)
- *"a blue circle at the bottom_right and above it a square, with a yellow triangle to the left of the square"*

![HDC Scene Composer In Action 4](assets/hdc-scene-composer-output4.gif)
- *"a large red circle at the center, with a small yellow circle overlapping_with it"*

![HDC Scene Composer In Action 5](assets/hdc-scene-composer-output5.gif)
- *"a large black square at the center and a small red triangle at the top_left, with a medium blue circle to the right of the triangle, and a yellow square below the circle"*

## TODO
- [ ] Fix relative positions.
- [ ] Implement way to describe multiple shapes relatives to one centroid.