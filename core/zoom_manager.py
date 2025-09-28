"""Zoom and pan functionality management."""

import time
from typing import Optional, Callable
from utils.constants import (
    MIN_ZOOM, MAX_ZOOM_MOUSE, MAX_ZOOM_KEYBOARD, 
    ZOOM_COOLDOWN, ZOOM_INCREMENT_KEYBOARD, ZOOM_INCREMENT_MOUSE
)


class ZoomManager:
    """Manages zoom and pan operations."""
    
    def __init__(self, image_manager, update_callback: Optional[Callable] = None):
        self.image_manager = image_manager
        self.update_callback = update_callback
        
        # Mouse tracking for zoom centering
        self.last_mouse_x: float = 0
        self.last_mouse_y: float = 0
        
        # Zoom debouncing
        self.last_zoom_time: float = 0
        
        # Pan state
        self.is_panning: bool = False
        self.pan_start_x: Optional[float] = None
        self.pan_start_y: Optional[float] = None
        
        # Drawing state (prevents zoom during box drawing)
        self.drawing_box: bool = False
    
    def set_drawing_mode(self, drawing: bool) -> None:
        """Set whether we're currently drawing a bounding box."""
        self.drawing_box = drawing
    
    def update_mouse_position(self, x: float, y: float) -> None:
        """Update the last known mouse position for zoom centering."""
        self.last_mouse_x = x
        self.last_mouse_y = y
    
    def can_zoom_in_keyboard(self) -> bool:
        """Check if we can zoom in using keyboard shortcuts."""
        return self.image_manager.scale_factor * ZOOM_INCREMENT_KEYBOARD <= MAX_ZOOM_KEYBOARD
    
    def can_zoom_out(self) -> bool:
        """Check if we can zoom out."""
        return self.image_manager.scale_factor / ZOOM_INCREMENT_KEYBOARD >= MIN_ZOOM
    
    def can_zoom_in_mouse(self) -> bool:
        """Check if we can zoom in using mouse wheel."""
        return self.image_manager.scale_factor * ZOOM_INCREMENT_MOUSE <= MAX_ZOOM_MOUSE
    
    def zoom_in_keyboard(self) -> bool:
        """Zoom in using keyboard increment. Returns True if zoom occurred."""
        if not self.can_zoom_in_keyboard() or self.drawing_box:
            return False
        
        new_scale = self.image_manager.scale_factor * ZOOM_INCREMENT_KEYBOARD
        return self._zoom_to_scale(new_scale, center_on_mouse=False)
    
    def zoom_out_keyboard(self) -> bool:
        """Zoom out using keyboard increment. Returns True if zoom occurred."""
        if not self.can_zoom_out() or self.drawing_box:
            return False
        
        new_scale = self.image_manager.scale_factor / ZOOM_INCREMENT_KEYBOARD
        return self._zoom_to_scale(new_scale, center_on_mouse=False)
    
    def zoom_in_mouse(self) -> bool:
        """Zoom in using mouse increment with debouncing. Returns True if zoom occurred."""
        if not self._can_zoom_with_debouncing() or not self.can_zoom_in_mouse() or self.drawing_box:
            return False
        
        new_scale = self.image_manager.scale_factor * ZOOM_INCREMENT_MOUSE
        return self._zoom_to_scale(new_scale, center_on_mouse=True)
    
    def zoom_out_mouse(self) -> bool:
        """Zoom out using mouse increment with debouncing. Returns True if zoom occurred."""
        if not self._can_zoom_with_debouncing() or not self.can_zoom_out() or self.drawing_box:
            return False
        
        new_scale = self.image_manager.scale_factor / ZOOM_INCREMENT_MOUSE
        return self._zoom_to_scale(new_scale, center_on_mouse=True)
    
    def zoom_to_scale(self, scale: float, center_on_mouse: bool = False) -> bool:
        """Zoom to a specific scale. Returns True if zoom occurred."""
        if self.drawing_box:
            return False
        
        # Clamp scale to valid range
        scale = max(MIN_ZOOM, min(MAX_ZOOM_KEYBOARD, scale))
        return self._zoom_to_scale(scale, center_on_mouse)
    
    def _zoom_to_scale(self, new_scale: float, center_on_mouse: bool) -> bool:
        """Internal method to perform zoom operation."""
        if center_on_mouse:
            # Calculate new image position to keep the same point under the mouse
            img_x, img_y = self.image_manager.canvas_to_image_coords(
                self.last_mouse_x, self.last_mouse_y
            )
            
            # Update scale factor
            self.image_manager.scale_factor = new_scale
            
            # Calculate new image position
            new_canvas_x, new_canvas_y = self.image_manager.image_to_canvas_coords(img_x, img_y)
            self.image_manager.image_x = self.last_mouse_x - (new_canvas_x - self.image_manager.image_x)
            self.image_manager.image_y = self.last_mouse_y - (new_canvas_y - self.image_manager.image_y)
        else:
            # Simple zoom without centering
            self.image_manager.scale_factor = new_scale
        
        if self.update_callback:
            self.update_callback()
        
        return True
    
    def _can_zoom_with_debouncing(self) -> bool:
        """Check if enough time has passed since last zoom for debouncing."""
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_zoom_time >= ZOOM_COOLDOWN:
            self.last_zoom_time = current_time
            return True
        return False
    
    def start_pan(self, x: float, y: float) -> None:
        """Start panning operation."""
        self.is_panning = True
        self.pan_start_x = x
        self.pan_start_y = y
    
    def update_pan(self, x: float, y: float, canvas, move_callback: Optional[Callable] = None) -> None:
        """Update pan operation."""
        if not self.is_panning or self.pan_start_x is None or self.pan_start_y is None:
            return
        
        dx = x - self.pan_start_x
        dy = y - self.pan_start_y
        
        # Only pan if there's significant movement
        if abs(dx) > 1 or abs(dy) > 1:
            self.image_manager.move_image(canvas, dx, dy)
            
            if move_callback:
                move_callback(dx, dy)
            
            # Update pan start position for next movement
            self.pan_start_x = x
            self.pan_start_y = y
    
    def end_pan(self) -> None:
        """End panning operation."""
        self.is_panning = False
        self.pan_start_x = None
        self.pan_start_y = None
    
    def get_zoom_percentage(self) -> int:
        """Get current zoom level as percentage."""
        return int(self.image_manager.scale_factor * 100)
