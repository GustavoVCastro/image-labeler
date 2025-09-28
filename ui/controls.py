"""UI control widgets and buttons."""

import tkinter as tk
from typing import Callable, Optional


class NavigationControls:
    """Navigation and action control buttons."""
    
    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent)
        
        # Navigation buttons
        self.grid_button = tk.Button(self.frame, text="Grid")
        self.grid_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(self.frame, text="Previous")
        self.prev_button.pack(side=tk.LEFT, padx=(10, 0))
        
        self.next_button = tk.Button(self.frame, text="Next")
        self.next_button.pack(side=tk.LEFT)
        
        # Action buttons
        self.clear_labels_button = tk.Button(self.frame, text="Clear Labels")
        self.clear_labels_button.pack(side=tk.LEFT, padx=(10, 0))
    
    def set_grid_command(self, command: Callable) -> None:
        """Set the command for the grid button."""
        self.grid_button.config(command=command)
    
    def set_navigation_commands(self, prev_command: Callable, next_command: Callable) -> None:
        """Set the commands for navigation buttons."""
        self.prev_button.config(command=prev_command)
        self.next_button.config(command=next_command)
    
    def set_clear_command(self, command: Callable) -> None:
        """Set the command for the clear labels button."""
        self.clear_labels_button.config(command=command)
    
    def update_navigation_state(self, has_images: bool) -> None:
        """Update the state of navigation buttons based on whether images are loaded."""
        state = tk.NORMAL if has_images else tk.DISABLED
        self.prev_button.config(state=state)
        self.next_button.config(state=state)
    
    def pack(self, **kwargs) -> None:
        """Pack the control frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self) -> None:
        """Hide the control frame."""
        self.frame.pack_forget()


class ZoomControls:
    """Zoom control buttons and indicator."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        
        # Zoom buttons (will be added to the navigation controls frame)
        self.zoom_fit_button: Optional[tk.Button] = None
        self.zoom_200_button: Optional[tk.Button] = None
        self.zoom_100_button: Optional[tk.Button] = None
        self.zoom_label: Optional[tk.Label] = None
    
    def add_to_frame(self, frame: tk.Frame) -> None:
        """Add zoom controls to an existing frame (typically navigation controls)."""
        # Zoom controls
        self.zoom_fit_button = tk.Button(frame, text="Fit")
        self.zoom_fit_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.zoom_200_button = tk.Button(frame, text="200%")
        self.zoom_200_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.zoom_100_button = tk.Button(frame, text="100%")
        self.zoom_100_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Zoom level indicator
        self.zoom_label = tk.Label(frame, text="Zoom: 100%", font=("Arial", 10))
        self.zoom_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def set_zoom_commands(self, fit_command: Callable, zoom_100_command: Callable, zoom_200_command: Callable) -> None:
        """Set the commands for zoom buttons."""
        if self.zoom_fit_button:
            self.zoom_fit_button.config(command=fit_command)
        if self.zoom_100_button:
            self.zoom_100_button.config(command=zoom_100_command)
        if self.zoom_200_button:
            self.zoom_200_button.config(command=zoom_200_command)
    
    def update_zoom_indicator(self, zoom_percentage: int) -> None:
        """Update the zoom level indicator."""
        if self.zoom_label:
            self.zoom_label.config(text=f"Zoom: {zoom_percentage}%")
