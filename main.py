"""
Image Labeler Application - Modular Version

A GUI application for labeling images with bounding boxes in YOLO format.
"""

import os
from typing import List, Optional

from ui import MainWindow, GridView, LabelingView, NavigationControls, ZoomControls
from core import ImageManager, LabelManager, ZoomManager
from utils import (
    DEFAULT_IMAGES_DIR, DEFAULT_LABELS_DIR, 
    create_directories, get_image_files
)


class ImageLabelerApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        # Initialize main window
        self.main_window = MainWindow()
        self.root = self.main_window.root
        
        # Initialize directories
        self.images_dir = DEFAULT_IMAGES_DIR
        self.labels_dir = DEFAULT_LABELS_DIR
        create_directories(self.images_dir, self.labels_dir)
        
        # Initialize core managers
        self.image_manager = ImageManager()
        self.label_manager = LabelManager(self.labels_dir)
        self.zoom_manager = ZoomManager(self.image_manager, self._update_display)
        
        # Initialize UI components
        self.grid_view = GridView(self.root)
        self.labeling_view = LabelingView(self.root)
        self.nav_controls = NavigationControls(self.root)
        self.zoom_controls = ZoomControls(self.root)
        
        # Application state
        self.images: List[str] = []
        self.current_image_index: int = 0
        self.current_view: str = "grid"  # "grid" or "labeling"
        
        # Setup UI
        self._setup_ui()
        self._setup_callbacks()
        self._setup_keyboard_shortcuts()
        
        # Auto-load images from default directory
        self._auto_load_images()
    
    def run(self) -> None:
        """Start the application."""
        self.main_window.run()
    
    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # Add zoom controls to navigation frame
        self.zoom_controls.add_to_frame(self.nav_controls.frame)
        
        # Initially hide labeling UI components
        self.labeling_view.hide()
        self.nav_controls.pack_forget()
    
    def _setup_callbacks(self) -> None:
        """Setup callback functions for UI components."""
        # Main window callbacks
        self.main_window.set_load_images_callback(self._load_images_from_directory)
        
        # Grid view callbacks
        self.grid_view.set_selection_callback(self._select_image)
        
        # Navigation controls callbacks
        self.nav_controls.set_grid_command(self._show_grid_view)
        self.nav_controls.set_navigation_commands(self._prev_image, self._next_image)
        self.nav_controls.set_clear_command(self._clear_labels)
        
        # Zoom controls callbacks
        self.zoom_controls.set_zoom_commands(
            self._zoom_to_fit, self._zoom_to_100, self._zoom_to_200
        )
        
        # Labeling view callbacks
        self.labeling_view.set_callbacks(
            box_created=self._on_box_created,
            pan_start=self._on_pan_start,
            pan_update=self._on_pan_update,
            pan_end=self._on_pan_end,
            mouse_motion=self._on_mouse_motion
        )
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        self.main_window.bind_keyboard_shortcuts(
            prev_image=self._prev_image,
            next_image=self._next_image,
            undo_box=self._undo_box,
            zoom_in=self._zoom_in,
            zoom_out=self._zoom_out,
            zoom_fit=self._zoom_to_fit,
            zoom_100=self._zoom_to_100,
            zoom_200=self._zoom_to_200,
            clear_labels=self._clear_labels,
            grid_scroll_up=self._grid_scroll_up,
            grid_scroll_down=self._grid_scroll_down
        )
        
        # Bind zoom mousewheel events
        self._bind_zoom_mousewheel()
    
    def _auto_load_images(self) -> None:
        """Auto-load images from the default images directory."""
        self.images = get_image_files(self.images_dir)
        if self.images:
            self._show_grid_view()
    
    def _load_images_from_directory(self, directory: str) -> None:
        """Load images from a selected directory."""
        self.images = get_image_files(directory)
        if self.images:
            self.current_image_index = 0
            self._show_grid_view()
    
    def _show_grid_view(self) -> None:
        """Show the grid view of all images."""
        self.current_view = "grid"
        
        # Hide labeling UI
        self.labeling_view.hide()
        self.nav_controls.pack_forget()
        
        # Clear labeling state
        self.labeling_view.clear_canvas()
        self.label_manager.clear_boxes()
        
        # Show grid UI
        self.grid_view.show()
        self.grid_view.populate_grid(self.images)
    
    def _select_image(self, index: int) -> None:
        """Select an image and switch to labeling view."""
        self.current_image_index = index
        self._show_labeling_view()
    
    def _show_labeling_view(self) -> None:
        """Show the labeling view for the current image."""
        if not self.images:
            return
        
        self.current_view = "labeling"
        
        # Hide grid UI
        self.grid_view.hide()
        
        # Show labeling UI
        self.labeling_view.show()
        self.nav_controls.pack(side="bottom", fill="x")
        
        # Load and display current image
        self._load_current_image()
        self._update_navigation_buttons()
    
    def _load_current_image(self) -> None:
        """Load the current image and its labels."""
        if not self.images or self.current_image_index >= len(self.images):
            return
        
        image_path = self.images[self.current_image_index]
        
        # Load image
        if self.image_manager.load_image(image_path):
            # Load labels
            self.label_manager.load_labels(image_path)
            
            # Display image and fit to canvas
            self._fit_image_to_canvas()
            self._update_display()
    
    def _fit_image_to_canvas(self) -> None:
        """Fit the image to the canvas size."""
        self.labeling_view.canvas.update_idletasks()
        canvas_width = self.labeling_view.canvas.winfo_width()
        canvas_height = self.labeling_view.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            scale = self.image_manager.calculate_fit_scale(canvas_width, canvas_height)
            self.image_manager.set_scale_and_center(scale, canvas_width, canvas_height)
        else:
            # Canvas not ready yet, try again later
            self.root.after(100, self._fit_image_to_canvas)
    
    def _update_display(self) -> None:
        """Update the image display and bounding boxes."""
        if self.current_view != "labeling":
            return
        
        # Display image on canvas
        self.image_manager.display_on_canvas(self.labeling_view.canvas)
        
        # Draw bounding boxes
        boxes = self.label_manager.get_boxes()
        self.labeling_view.draw_boxes(boxes, self.image_manager)
        
        # Update zoom indicator
        zoom_percentage = self.zoom_manager.get_zoom_percentage()
        self.zoom_controls.update_zoom_indicator(zoom_percentage)
    
    def _prev_image(self) -> None:
        """Navigate to the previous image."""
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self._load_current_image()
    
    def _next_image(self) -> None:
        """Navigate to the next image."""
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self._load_current_image()
    
    def _update_navigation_buttons(self) -> None:
        """Update the state of navigation buttons."""
        self.nav_controls.update_navigation_state(bool(self.images))
    
    def _on_box_created(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Handle creation of a new bounding box."""
        if not self.images:
            return
        
        # Convert canvas coordinates to image coordinates
        img_x1, img_y1 = self.image_manager.canvas_to_image_coords(x1, y1)
        img_x2, img_y2 = self.image_manager.canvas_to_image_coords(x2, y2)
        
        # Normalize coordinates
        x_center, y_center, width, height = self.image_manager.normalize_coordinates(
            img_x1, img_y1, img_x2, img_y2
        )
        
        # Add to label manager
        self.label_manager.add_box(x_center, y_center, width, height)
        
        # Save labels
        current_image_path = self.images[self.current_image_index]
        self.label_manager.save_labels(current_image_path)
    
    def _clear_labels(self) -> None:
        """Clear all labels for the current image."""
        if not self.images:
            return
        
        # Clear labels
        self.label_manager.clear_boxes()
        
        # Delete label file
        current_image_path = self.images[self.current_image_index]
        self.label_manager.delete_labels(current_image_path)
        
        # Update display
        self._update_display()
    
    def _undo_box(self) -> None:
        """Undo the last bounding box."""
        if not self.images:
            return
        
        if self.label_manager.remove_last_box():
            # Save updated labels
            current_image_path = self.images[self.current_image_index]
            self.label_manager.save_labels(current_image_path)
            
            # Update display
            self._update_display()
    
    def _zoom_in(self) -> None:
        """Zoom in on the image."""
        self.zoom_manager.zoom_in_keyboard()
    
    def _zoom_out(self) -> None:
        """Zoom out on the image."""
        self.zoom_manager.zoom_out_keyboard()
    
    def _zoom_to_fit(self) -> None:
        """Zoom to fit the image in the canvas."""
        self._fit_image_to_canvas()
        self._update_display()
    
    def _zoom_to_100(self) -> None:
        """Set zoom to 100%."""
        self.zoom_manager.zoom_to_scale(1.0)
    
    def _zoom_to_200(self) -> None:
        """Set zoom to 200%."""
        self.zoom_manager.zoom_to_scale(2.0)
    
    def _on_pan_start(self, x: float, y: float) -> None:
        """Handle start of panning."""
        self.zoom_manager.start_pan(x, y)
    
    def _on_pan_update(self, x: float, y: float) -> None:
        """Handle pan update."""
        def move_boxes(dx, dy):
            self.labeling_view.move_boxes(dx, dy)
        
        self.zoom_manager.update_pan(x, y, self.labeling_view.canvas, move_boxes)
    
    def _on_pan_end(self) -> None:
        """Handle end of panning."""
        self.zoom_manager.end_pan()
    
    def _on_mouse_motion(self, x: float, y: float) -> None:
        """Handle mouse motion for zoom centering."""
        self.zoom_manager.update_mouse_position(x, y)
    
    def _grid_scroll_up(self) -> None:
        """Scroll up in grid view."""
        if self.current_view == "grid":
            self.grid_view.scroll_up()
    
    def _grid_scroll_down(self) -> None:
        """Scroll down in grid view."""
        if self.current_view == "grid":
            self.grid_view.scroll_down()
    
    def _bind_zoom_mousewheel(self) -> None:
        """Bind mousewheel events for zooming."""
        def _on_zoom_mousewheel(event):
            if self.current_view == "labeling":
                # Get mouse position for zoom centering
                canvas = self.labeling_view.canvas
                mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
                mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
                self.zoom_manager.update_mouse_position(mouse_x, mouse_y)
                
                # Zoom based on scroll direction
                if event.delta > 0:  # Scroll up - zoom in
                    self.zoom_manager.zoom_in_mouse()
                else:  # Scroll down - zoom out
                    self.zoom_manager.zoom_out_mouse()
        
        def _on_zoom_mouse_scroll(event):
            if self.current_view == "labeling":
                # Get mouse position for zoom centering
                canvas = self.labeling_view.canvas
                mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
                mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
                self.zoom_manager.update_mouse_position(mouse_x, mouse_y)
                
                # Handle mouse scroll events
                if event.num == 4:  # Scroll up - zoom in
                    self.zoom_manager.zoom_in_mouse()
                elif event.num == 5:  # Scroll down - zoom out
                    self.zoom_manager.zoom_out_mouse()
        
        # Bind to root window
        self.root.bind_all("<MouseWheel>", _on_zoom_mousewheel)
        self.root.bind_all("<Button-4>", _on_zoom_mouse_scroll)
        self.root.bind_all("<Button-5>", _on_zoom_mouse_scroll)


def main():
    """Main entry point."""
    app = ImageLabelerApp()
    app.run()


if __name__ == "__main__":
    main()
