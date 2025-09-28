"""Labeling view for annotating images with bounding boxes."""

import tkinter as tk
from typing import List, Callable, Optional, Tuple
from utils.constants import BOX_OUTLINE_COLOR, BOX_OUTLINE_WIDTH, MIN_BOX_SIZE


class LabelingView:
    """View for labeling images with bounding boxes."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        
        # Canvas frame with scrollbars
        self.frame = tk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, bg="gray")
        
        # Scrollbars
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Bounding box drawing state
        self.drawing_rect: Optional[int] = None
        self.start_x: Optional[float] = None
        self.start_y: Optional[float] = None
        
        # Box rectangles on canvas
        self.box_rects: List[int] = []
        
        # Callbacks
        self.box_created_callback: Optional[Callable[[float, float, float, float], None]] = None
        self.pan_start_callback: Optional[Callable[[float, float], None]] = None
        self.pan_update_callback: Optional[Callable[[float, float], None]] = None
        self.pan_end_callback: Optional[Callable[[], None]] = None
        self.mouse_motion_callback: Optional[Callable[[float, float], None]] = None
        
        # Bind mouse events
        self._bind_mouse_events()
    
    def show(self) -> None:
        """Show the labeling view."""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Pack canvas and scrollbars in proper order
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for proper resizing
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self._bind_zoom_events()
        self._bind_cursor_events()
    
    def hide(self) -> None:
        """Hide the labeling view."""
        self.frame.pack_forget()
        self._unbind_zoom_events()
        self._unbind_cursor_events()
    
    def clear_canvas(self) -> None:
        """Clear the canvas and reset box rectangles."""
        self.canvas.delete("all")
        self.box_rects.clear()
    
    def draw_boxes(self, boxes: List[Tuple[float, float, float, float, float]], 
                   image_manager) -> None:
        """Draw bounding boxes on the canvas."""
        # Clear existing box rectangles
        for rect_id in self.box_rects:
            self.canvas.delete(rect_id)
        self.box_rects.clear()
        
        if not image_manager.original_image:
            return
        
        # Draw each box
        for class_id, x_center, y_center, width, height in boxes:
            # Convert normalized coordinates to image coordinates
            x1, y1, x2, y2 = image_manager.denormalize_coordinates(x_center, y_center, width, height)
            
            # Convert to canvas coordinates
            canvas_x1, canvas_y1 = image_manager.image_to_canvas_coords(x1, y1)
            canvas_x2, canvas_y2 = image_manager.image_to_canvas_coords(x2, y2)
            
            rect = self.canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                outline=BOX_OUTLINE_COLOR, width=BOX_OUTLINE_WIDTH
            )
            self.box_rects.append(rect)
    
    def move_boxes(self, dx: float, dy: float) -> None:
        """Move all bounding box rectangles."""
        for rect_id in self.box_rects:
            self.canvas.move(rect_id, dx, dy)
    
    def set_callbacks(self, 
                     box_created: Optional[Callable[[float, float, float, float], None]] = None,
                     pan_start: Optional[Callable[[float, float], None]] = None,
                     pan_update: Optional[Callable[[float, float], None]] = None,
                     pan_end: Optional[Callable[[], None]] = None,
                     mouse_motion: Optional[Callable[[float, float], None]] = None) -> None:
        """Set callback functions for various events."""
        if box_created:
            self.box_created_callback = box_created
        if pan_start:
            self.pan_start_callback = pan_start
        if pan_update:
            self.pan_update_callback = pan_update
        if pan_end:
            self.pan_end_callback = pan_end
        if mouse_motion:
            self.mouse_motion_callback = mouse_motion
    
    def _bind_mouse_events(self) -> None:
        """Bind mouse events for drawing and panning."""
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<Motion>", self._on_mouse_motion)
    
    def _bind_zoom_events(self) -> None:
        """Bind zoom events."""
        def _on_zoom_mousewheel(event):
            # This will be handled by the main application
            pass
        
        def _on_zoom_mouse_scroll(event):
            # This will be handled by the main application
            pass
        
        self.canvas.bind_all("<MouseWheel>", _on_zoom_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_zoom_mouse_scroll)
        self.canvas.bind_all("<Button-5>", _on_zoom_mouse_scroll)
    
    def _unbind_zoom_events(self) -> None:
        """Unbind zoom events."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
    
    def _bind_cursor_events(self) -> None:
        """Bind cursor events."""
        self.canvas.bind("<Enter>", self._on_canvas_enter)
        self.canvas.bind("<Leave>", self._on_canvas_leave)
    
    def _unbind_cursor_events(self) -> None:
        """Unbind cursor events."""
        self.canvas.unbind("<Enter>")
        self.canvas.unbind("<Leave>")
    
    def _on_mouse_press(self, event) -> None:
        """Handle mouse press events."""
        if event.state & 0x4:  # Ctrl key is held (0x4 is Ctrl modifier)
            # Start drawing bounding box
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            self.drawing_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, ex, ey, outline=BOX_OUTLINE_COLOR
            )
        else:
            # Start panning
            if self.pan_start_callback:
                self.pan_start_callback(event.x, event.y)
            self.canvas.config(cursor="fleur")
    
    def _on_mouse_drag(self, event) -> None:
        """Handle mouse drag events."""
        if self.drawing_rect:
            # Continue drawing bounding box
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            self.canvas.coords(self.drawing_rect, self.start_x, self.start_y, ex, ey)
        else:
            # Continue panning
            if self.pan_update_callback:
                self.pan_update_callback(event.x, event.y)
    
    def _on_mouse_release(self, event) -> None:
        """Handle mouse release events."""
        if self.drawing_rect:
            # Finish drawing bounding box
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            x1, y1, x2, y2 = self.start_x, self.start_y, ex, ey
            
            # Only save if the box has some size
            if abs(x2 - x1) > MIN_BOX_SIZE and abs(y2 - y1) > MIN_BOX_SIZE:
                if self.box_created_callback:
                    self.box_created_callback(x1, y1, x2, y2)
                
                # Convert to permanent rectangle
                self.canvas.delete(self.drawing_rect)
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, outline=BOX_OUTLINE_COLOR, width=BOX_OUTLINE_WIDTH
                )
                self.box_rects.append(rect)
            else:
                # Delete the temporary rectangle if it's too small
                self.canvas.delete(self.drawing_rect)
            
            # Reset drawing state
            self.drawing_rect = None
            self.start_x = None
            self.start_y = None
        else:
            # End panning
            if self.pan_end_callback:
                self.pan_end_callback()
            self.canvas.config(cursor="")
    
    def _on_mouse_motion(self, event) -> None:
        """Handle mouse motion events."""
        if self.mouse_motion_callback:
            self.mouse_motion_callback(event.x, event.y)
    
    def _on_canvas_enter(self, event) -> None:
        """Handle mouse entering canvas."""
        self.canvas.config(cursor="fleur")
    
    def _on_canvas_leave(self, event) -> None:
        """Handle mouse leaving canvas."""
        self.canvas.config(cursor="")
