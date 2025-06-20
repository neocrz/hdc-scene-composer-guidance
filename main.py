# main.py

import time
import tkinter as tk
import sys
import os
from PIL import Image, ImageGrab

# Import all our custom modules
import config
from lexicon import Lexicon
from scene_parser import SceneParser
from scene_encoder import SceneEncoder
from canvas import Canvas, CanvasObject
from agent import Agent
from guidance_system import GuidanceSystem

class Visualizer:
    """A simple Tkinter based visualizer for the canvas."""
    def __init__(self, canvas: Canvas, width: int, height: int, title: str = "HDC Scene Composer"):
        self.canvas_data = canvas
        self.width = width
        self.height = height

        self.root = tk.Tk()
        self.root.title(title)
        self.tk_canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=config.CANVAS_BACKGROUND_COLOR)
        self.tk_canvas.pack()
        self.tk_canvas_objects: dict[str, int] = {}

    def update(self):
        """Redraws the entire canvas based on the current state of the Canvas data object."""
        self.tk_canvas.delete("all")

        for obj in self.canvas_data.get_all_objects():
            x, y = obj.position_xy
            size = obj.size_val
            color = obj.color

            if obj.shape == 'circle':
                self.tk_canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline='black')
            elif obj.shape == 'square':
                self.tk_canvas.create_rectangle(x - size, y - size, x + size, y + size, fill=color, outline='black')
            elif obj.shape == 'triangle':
                # Equilateral triangle points
                p1 = (x, y - size)
                p2 = (x - size * 0.866, y + size * 0.5)
                p3 = (x + size * 0.866, y + size * 0.5)
                self.tk_canvas.create_polygon(p1, p2, p3, fill=color, outline='black')

        self.root.update_idletasks()
        self.root.update()

    def save_frame(self, filepath: str):
        """Saves the current state of the canvas as an image file."""
        # Calculate coordinates of the canvas widget on the screen
        x = self.root.winfo_rootx() + self.tk_canvas.winfo_x()
        y = self.root.winfo_rooty() + self.tk_canvas.winfo_y()
        x1 = x + self.tk_canvas.winfo_width()
        y1 = y + self.tk_canvas.winfo_height()
        
        # Grab the image of the canvas area and save it
        ImageGrab.grab().crop((x, y, x1, y1)).save(filepath)

def create_gif(frame_folder: str, output_filename: str):
    """
    Compiles a GIF from a folder of frame images using robust file handling.
    """
    frame_files = sorted(os.listdir(frame_folder), key=lambda f: int(f.split('.')[0].split('_')[-1]))

    if not frame_files:
        print("Error: No frames found in the folder to create a GIF.")
        return

    frames = []
    for filename in frame_files:
        filepath = os.path.join(frame_folder, filename)
        try:
            with Image.open(filepath) as img:
                frames.append(img.copy()) # Use a copy to detach from the file handle
        except IOError:
            print(f"Warning: Could not read frame {filename}. Skipping.")
            continue
    
    if not frames:
        print("Error: Frame images could not be processed.")
        return

    # The first frame is the base, others are appended.s
    frames[0].save(
        output_filename,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=500,
        loop=0         # Loop forever
    )
    print(f"Successfully created GIF: {output_filename}")


def main_loop(target_description: str, enable_visualization: bool = True, save_gif: bool = False):
    """
    The main execution function.

    Args:
        target_description: The natural language string describing the desired scene.
        enable_visualization: If True, show the Tkinter visualization.
        save_gif: If True, save the process as a GIF.
    """
    print("="*50)
    print("Initializing HDC Scene Composer System...")
    print(f"Target Description: '{target_description}'")
    print("="*50)
    
    frame_folder = "gif_frames"
    if save_gif:
        if os.path.exists(frame_folder):
            for f in os.listdir(frame_folder):
                os.remove(os.path.join(frame_folder, f))
        else:
            os.makedirs(frame_folder)

    # --- Initialization ---
    lexicon = Lexicon()
    parser = SceneParser(lexicon)
    canvas = Canvas()
    scene_encoder = SceneEncoder(lexicon)
    agent = Agent(canvas)
    
    # --- Parse Target Description ---
    parsed_description = parser.parse_description(target_description)
    if not parsed_description:
        print("Error: Could not parse the target description into any known objects. Exiting.")
        return
    
    print(f"Parsed Description: {parsed_description}")
    
    # --- Initialize Guidance System with the Goal ---
    guidance_system = GuidanceSystem(lexicon, scene_encoder, parsed_description)

    # --- Initialize Visualizer ---
    visualizer = None
    if enable_visualization or save_gif:
        visualizer = Visualizer(canvas, config.CANVAS_WIDTH, config.CANVAS_HEIGHT)
        # Draw the initial empty window and pause to allow the OS to place it
        visualizer.update()
        time.sleep(0.5)

    # --- The Main Guidance Loop ---
    print("\n--- Starting Guidance Loop ---")
    frame_count = 0
    for i in range(config.MAX_ITERATIONS):
        print(f"\n--- Iteration {i+1} ---")
        
        if visualizer:
            visualizer.update()
            if save_gif:
                visualizer.save_frame(os.path.join(frame_folder, f"frame_{frame_count}.png"))
                frame_count += 1
            if enable_visualization and i > 0:
                 time.sleep(0.5)

        # A. Get the current scene state as a hypervector
        scene_encoder.encode_canvas_state(canvas)
        
        # B. Ask the guidance system for the next best action
        action_command = guidance_system.propose_action(canvas)

        # C. Check for completion or execute the action
        if action_command is None:
            print("\nGuidance system proposes NO action. Scene is considered complete.")
            break
        
        # D. Have the agent execute the proposed action
        agent.execute_action(action_command)

    else:
        print("\nReached max iterations. Stopping.")

    # --- Final State ---
    print("\n--- Final Canvas State ---")
    print(canvas)
    
    if visualizer:
        # Capture the final frame
        if save_gif:
            visualizer.update()
            visualizer.save_frame(os.path.join(frame_folder, f"frame_{frame_count}.png"))
        
        if enable_visualization:
            print("Displaying final scene. Close the window to exit.")
            visualizer.root.mainloop()
        else:
            # If we only saved a gif without showing the UI, close the hidden window
            visualizer.root.destroy()
            
    # --- Compile GIF ---
    if save_gif:
        create_gif(frame_folder, "hdc-scene-composer-output.gif")

if __name__ == "__main__":
    # --- Handle Command-Line Arguments ---
    save_gif_flag = "--gif" in sys.argv
    
    TARGET_SCENE = "a large green triangle at the bottom_left, with a medium purple circle to its right, and a small yellow square above the circle"


    # --- Basic Layouts (Absolute Positions) ---
    # TARGET_SCENE = "a large red square in the center, a small blue circle at the top_center, and a small green circle at the bottom_center"
    # TARGET_SCENE = "a yellow circle at the top_left, a yellow circle at the top_right, a yellow circle at the bottom_left, and a yellow circle at the bottom_right"
    # TARGET_SCENE = "a purple square, a red circle, and a green triangle"
    # --- Relational Chains ---
    # TARGET_SCENE = "a large black square in the middle_left, with a medium red square to its right, and a small blue square to the right of the red square"
    TARGET_SCENE = "a large purple circle in the center, with a small red square above it, a small blue square below it, a small green square to its left, and a small yellow square to its right" # (needs fix)
    # TARGET_SCENE = "a blue circle at the bottom_right and above it a square, with a yellow triangle to the left of the square"
    # --- More Complex Scenarios & Edge Cases ---
    # TARGET_SCENE = "a large red circle at the center, with a small yellow circle overlapping_with it"
    # TARGET_SCENE = "a large red square in the center, and a large blue square in the center"
    # TARGET_SCENE = "a large circle at the top_left, and a small square at the bottom_right"
    # TARGET_SCENE = "a large black square at the center and a small red triangle at the top_left, with a medium blue circle to the right of the triangle, and a yellow square below the circle"

    main_loop(TARGET_SCENE, enable_visualization=True, save_gif=save_gif_flag)
