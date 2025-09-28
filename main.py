import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class ImageLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeler")
        
        # Set initial window size
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)  # Minimum size

        # Create directories if they don't exist
        self.images_dir = "images"
        self.labels_dir = "labels"
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.labels_dir, exist_ok=True)

        # Grid canvas for browsing images
        self.grid_canvas = tk.Canvas(root, bg="white")
        self.grid_frame = tk.Frame(self.grid_canvas)
        self.grid_canvas.create_window(0, 0, anchor=tk.NW, window=self.grid_frame)
        self.scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.grid_canvas.yview, width=15)
        self.grid_canvas.config(yscrollcommand=self.scrollbar.set)
        
        # Initially hide grid UI (will be shown when images are loaded)
        self.grid_canvas.pack_forget()
        self.scrollbar.pack_forget()

        # Canvas for displaying image with scrollbars
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack_forget()  # Initially hide
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="gray")
        
        # Add scrollbars
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # Navigation buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack_forget()  # Initially hide

        self.grid_button = tk.Button(self.button_frame, text="Grid", command=self.show_grid)
        self.grid_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_image)
        self.next_button.pack(side=tk.RIGHT)
        
        # Zoom controls
        self.zoom_fit_button = tk.Button(self.button_frame, text="Fit", command=self.zoom_to_fit)
        self.zoom_fit_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.zoom_200_button = tk.Button(self.button_frame, text="200%", command=self.zoom_to_200)
        self.zoom_200_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.zoom_100_button = tk.Button(self.button_frame, text="100%", command=self.zoom_to_100)
        self.zoom_100_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear labels
        self.clear_labels_button = tk.Button(self.button_frame, text="Clear Labels", command=self.clear_labels)
        self.clear_labels_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Zoom level indicator
        self.zoom_label = tk.Label(self.button_frame, text="Zoom: 100%", font=("Arial", 10))
        self.zoom_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image Directory", command=self.load_images)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

        self.images = []
        self.current_image_index = 0
        self.image_tk = None
        self.image_path = None
        self.boxes = []
        self.box_rects = []
        self.scale_factor = 1.0
        self.original_image = None
        self.image_x = 0  # Current x position of the image on canvas
        self.image_y = 0  # Current y position of the image on canvas
        self.last_mouse_x = 0  # Last mouse x position for zoom centering
        self.last_mouse_y = 0  # Last mouse y position for zoom centering
        
        # Zoom limits to prevent performance issues
        self.min_zoom = 0.1  # Minimum zoom (10% of original size)
        self.max_zoom_mouse = 2.0  # Maximum zoom for mouse wheel (200%)
        self.max_zoom_keyboard = 2.0  # Maximum zoom for keyboard shortcuts (200%)
        
        # Zoom debouncing to prevent laggy mouse wheel behavior
        self.zoom_cooldown = 50  # milliseconds between zoom operations
        self.last_zoom_time = 0

        # Mouse events for panning and drawing boxes
        self.canvas.bind("<ButtonPress-1>", self.start_pan_or_draw)
        self.canvas.bind("<B1-Motion>", self.pan_or_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_pan_or_draw)
        
        # Variables for panning
        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_start_canvas_x = None
        self.pan_start_canvas_y = None
        self.is_panning = False

        # Keyboard navigation
        root.bind("<Left>", lambda e: self.prev_image())
        root.bind("<Right>", lambda e: self.next_image())
        root.bind("<Control-z>", lambda e: self.undo_box())
        root.bind("<Control-plus>", lambda e: self.zoom_in())
        root.bind("<Control-equal>", lambda e: self.zoom_in())  # Ctrl+= is same as Ctrl+Plus
        root.bind("<Control-minus>", lambda e: self.zoom_out())
        root.bind("<Control-0>", lambda e: self.zoom_to_fit())  # Ctrl+0 to fit to canvas
        root.bind("<Control-1>", lambda e: self.zoom_to_100())  # Ctrl+1 to zoom to 100%
        root.bind("<Control-2>", lambda e: self.zoom_to_200())  # Ctrl+2 to zoom to 200%
        root.bind("<Control-BackSpace>", lambda e: self.clear_labels())  # Ctrl+Backspace clears labels
        
        # Grid navigation
        root.bind("<Up>", lambda e: self.grid_scroll_up())
        root.bind("<Down>", lambda e: self.grid_scroll_down())

        # Variables for bounding box drawing (when Ctrl is held)
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.drawing_box = False  # Flag to prevent zoom reset during drawing

        # Auto load images
        self.load_images_auto()

    def load_images_auto(self):
        """Auto-load images from the images directory"""
        if os.path.exists(self.images_dir):
            self.images = [os.path.join(self.images_dir, f) for f in os.listdir(self.images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if self.images:
                self.show_grid()

    def show_grid(self):
        """Show grid view of all images"""
        # Hide labeling UI
        self.canvas_frame.pack_forget()
        self.button_frame.pack_forget()
        
        # Clear canvas and reset state
        self.canvas.delete("all")
        self.boxes = []
        self.box_rects = []
        self.image_path = None
        self.original_image = None
        
        # Unbind zoom mousewheel events
        self.unbind_zoom_mousewheel()
        
        # Clear grid configuration
        for widget in self.canvas_frame.winfo_children():
            widget.grid_forget()
        
        # Show grid UI
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear existing thumbnails
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Create thumbnails
        cols = 4
        for i, image_path in enumerate(self.images):
            try:
                # Create thumbnail
                img = Image.open(image_path)
                img.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(img)
                
                # Create button with thumbnail
                btn = tk.Button(self.grid_frame, image=photo, command=lambda idx=i: self.select_image(idx))
                btn.image = photo  # Keep reference
                btn.grid(row=i//cols, column=i%cols, padx=5, pady=5)
                
            except Exception as e:
                print(f"Error loading thumbnail for {image_path}: {e}")
        
        # Update scroll region
        self.grid_frame.update_idletasks()
        self.grid_canvas.config(scrollregion=self.grid_canvas.bbox("all"))
        
        # Bind mousewheel to canvas for scrolling
        self.bind_mousewheel()

    def select_image(self, index):
        """Select an image and switch to labeling view"""
        self.current_image_index = index
        self.show_labeling_view()

    def show_labeling_view(self):
        """Show the labeling view for current image"""
        # Hide grid UI
        self.grid_canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # Unbind mousewheel from canvas
        self.unbind_mousewheel()
        
        # Show labeling UI
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack canvas and scrollbars in proper order
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for proper resizing
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mouse scroll events for zooming
        self.bind_zoom_mousewheel()
        
        # Bind mouse enter/leave events to update cursor
        self.canvas.bind("<Enter>", self.on_canvas_enter)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        
        # Bind mouse motion to track position for zoom centering
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        
        # Initialize mouse position to canvas center
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width > 1 and canvas_height > 1:
            self.last_mouse_x = canvas_width / 2
            self.last_mouse_y = canvas_height / 2
        
        # Display image and load existing boxes
        self.display_image()
        self.load_boxes()

    def load_images(self):
        dir_path = filedialog.askdirectory(title="Select Images Directory")
        if dir_path:
            self.images = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if self.images:
                self.show_grid()

    def display_image(self):
        if self.images:
            # Clear canvas and reset boxes
            self.canvas.delete("all")
            self.boxes = []
            self.box_rects = []
            
            # Reset image position
            self.image_x = 0
            self.image_y = 0
            
            self.image_path = self.images[self.current_image_index]
            self.original_image = Image.open(self.image_path)
            self.scale_image_to_fit()
            self.update_buttons()

    def scale_image_to_fit(self):
        """Scale image to fit the canvas size"""
        if not self.original_image:
            return
            
        # Don't reset zoom if we're currently drawing a bounding box
        if self.drawing_box:
            return
            
        # Get canvas size
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet, try again later
            self.root.after(100, self.scale_image_to_fit)
            return
        
        # Calculate scale to fit image in canvas
        img_width, img_height = self.original_image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale_factor = min(scale_x, scale_y) * 0.9  # 90% to leave some margin
        
        # Ensure initial scale factor respects zoom limits
        self.scale_factor = max(self.min_zoom, min(self.max_zoom_keyboard, self.scale_factor))
        
        # Center image on canvas when fitting
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        if new_width < canvas_width:
            self.image_x = (canvas_width - new_width) / 2
        else:
            self.image_x = 0
        if new_height < canvas_height:
            self.image_y = (canvas_height - new_height) / 2
        else:
            self.image_y = 0
        
        self.update_displayed_image()
        self.update_zoom_indicator()

    def update_displayed_image(self, preserve_center=False):
        """Update the displayed image with current scale factor"""
        if not self.original_image:
            return
            
        # Don't update if we're currently drawing a bounding box
        if self.drawing_box:
            return
            
        # Store current image position before updating
        old_image_x = self.image_x
        old_image_y = self.image_y
        
        # Resize image
        img_width, img_height = self.original_image.size
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        
        resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas and redraw
        self.canvas.delete("all")
        self.image_canvas_id = self.canvas.create_image(self.image_x, self.image_y, anchor=tk.NW, image=self.image_tk)
        
        # Update scroll region to include the entire image
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        # Clear box rectangles list before redrawing
        self.box_rects = []
        
        # Redraw existing boxes
        self.redraw_boxes()
        
        # Update cursor based on new zoom level
        if hasattr(self, 'canvas') and self.canvas.winfo_viewable():
            self.on_canvas_enter(None)

    def zoom_in(self):
        """Zoom in on the image (keyboard shortcut)"""
        new_scale = self.scale_factor * 1.1  # Same increment as mouse for consistency
        if new_scale <= self.max_zoom_keyboard:
            self.zoom_to_scale(new_scale, center_on_mouse=False)

    def zoom_out(self):
        """Zoom out on the image"""
        new_scale = self.scale_factor * 0.909090909  # 1/1.1 for consistent steps
        if new_scale >= self.min_zoom:
            self.zoom_to_scale(new_scale, center_on_mouse=False)

    def zoom_in_smooth(self):
        """Zoom in with smaller increment for smoother mouse wheel experience"""
        new_scale = self.scale_factor * 1.05  # Smaller increment for smoother mouse wheel
        if new_scale <= self.max_zoom_mouse:
            self.zoom_to_scale(new_scale, center_on_mouse=True)

    def zoom_out_smooth(self):
        """Zoom out with smaller increment for smoother mouse wheel experience"""
        new_scale = self.scale_factor * 0.952380952  # 1/1.05 for consistent steps
        if new_scale >= self.min_zoom:
            self.zoom_to_scale(new_scale, center_on_mouse=True)

    def debounced_zoom_in(self):
        """Debounced zoom in to prevent rapid successive operations"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_zoom_time >= self.zoom_cooldown:
            self.zoom_in_smooth()
            self.last_zoom_time = current_time

    def debounced_zoom_out(self):
        """Debounced zoom out to prevent rapid successive operations"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_zoom_time >= self.zoom_cooldown:
            self.zoom_out_smooth()
            self.last_zoom_time = current_time

    def zoom_to_scale(self, new_scale, center_on_mouse=False):
        """Zoom to a specific scale, optionally centering on mouse position"""
        # Don't zoom if we're currently drawing a bounding box
        if self.drawing_box:
            return
            
        if center_on_mouse:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Use mouse position if available and valid, otherwise center on canvas
            if (hasattr(self, 'last_mouse_x') and hasattr(self, 'last_mouse_y') and 
                self.last_mouse_x >= 0 and self.last_mouse_y >= 0):
                mouse_x = max(0, min(self.last_mouse_x, canvas_width))
                mouse_y = max(0, min(self.last_mouse_y, canvas_height))
            else:
                # Fallback to canvas center
                mouse_x = canvas_width / 2
                mouse_y = canvas_height / 2
            
            # Convert mouse position to image coordinates
            img_x = (mouse_x - self.image_x) / self.scale_factor
            img_y = (mouse_y - self.image_y) / self.scale_factor
            
            # Update scale factor
            self.scale_factor = new_scale
            
            # Calculate new image position to keep the same point under the mouse
            new_image_x = mouse_x - img_x * self.scale_factor
            new_image_y = mouse_y - img_y * self.scale_factor
            
            # Update image position
            self.image_x = new_image_x
            self.image_y = new_image_y
        else:
            # Simple zoom without centering
            self.scale_factor = new_scale
        
        self.update_displayed_image()
        self.update_zoom_indicator()

    def update_zoom_indicator(self):
        """Update the zoom level indicator in the bottom bar"""
        if hasattr(self, 'zoom_label'):
            zoom_percentage = int(self.scale_factor * 100)
            self.zoom_label.config(text=f"Zoom: {zoom_percentage}%")

    def zoom_to_fit(self):
        """Reset zoom to fit the image in the canvas"""
        self.scale_image_to_fit()

    def zoom_to_100(self):
        """Set zoom to exactly 100% (1:1)"""
        self.zoom_to_scale(1.0, center_on_mouse=False)

    def zoom_to_200(self):
        """Set zoom to exactly 200%"""
        self.zoom_to_scale(2.0, center_on_mouse=False)

    def can_pan(self):
        """Check if panning is possible (image larger than canvas)"""
        if not self.original_image:
            return False
        
        # Get canvas size
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return False
        
        # Get image size at current scale
        img_width, img_height = self.original_image.size
        scaled_width = int(img_width * self.scale_factor)
        scaled_height = int(img_height * self.scale_factor)
        
        # Panning is possible if image is larger than canvas
        return scaled_width > canvas_width or scaled_height > canvas_height

    def redraw_boxes(self):
        """Redraw all bounding boxes with current scale factor and image position"""
        if not self.original_image:
            return
            
        img_width, img_height = self.original_image.size
        
        for class_id, x_center, y_center, width, height in self.boxes:
            # Convert normalized coordinates to canvas coordinates
            x1 = (x_center - width/2) * img_width * self.scale_factor + self.image_x
            y1 = (y_center - height/2) * img_height * self.scale_factor + self.image_y
            x2 = (x_center + width/2) * img_width * self.scale_factor + self.image_x
            y2 = (y_center + height/2) * img_height * self.scale_factor + self.image_y
            
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
            self.box_rects.append(rect)

    def load_boxes(self):
        """Load existing bounding boxes for current image"""
        # Clear existing boxes
        self.boxes = []
        self.box_rects = []
        
        if not self.image_path:
            return
            
        label_file = os.path.splitext(os.path.basename(self.image_path))[0] + ".txt"
        label_path = os.path.join(self.labels_dir, label_file)
        
        if os.path.exists(label_path):
            try:
                with open(label_path, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            class_id, x_center, y_center, width, height = map(float, parts)
                            self.boxes.append((class_id, x_center, y_center, width, height))
                            
                # Redraw boxes with current scale
                self.redraw_boxes()
            except Exception as e:
                print(f"Error loading boxes: {e}")

    def prev_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.display_image()
            self.load_boxes()

    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.display_image()
            self.load_boxes()

    def update_buttons(self):
        if not self.images:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)

    def start_pan_or_draw(self, event):
        """Start panning or drawing based on whether Ctrl is held"""
        if event.state & 0x4:  # Ctrl key is held (0x4 is Ctrl modifier)
            # Start drawing bounding box
            self.drawing_box = True  # Set flag to prevent zoom reset
            # Store current zoom and position to preserve them
            self.saved_scale_factor = self.scale_factor
            self.saved_image_x = self.image_x
            self.saved_image_y = self.image_y
            # Use canvas-relative coordinates to avoid offsets during zoom/pan
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, ex, ey, outline="red")
        else:
            # Start panning - allow free dragging regardless of image size
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            # Get current canvas scroll position
            self.pan_start_canvas_x = self.canvas.canvasx(0)
            self.pan_start_canvas_y = self.canvas.canvasy(0)
            self.is_panning = True
            self.canvas.config(cursor="fleur")  # Change cursor to indicate panning

    def pan_or_draw(self, event):
        """Continue panning or drawing based on current mode"""
        if self.rect:
            # Continue drawing bounding box
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            self.canvas.coords(self.rect, self.start_x, self.start_y, ex, ey)
        elif self.is_panning:
            # Continue panning - make the grabbed point follow the cursor
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            
            # Only pan if there's significant movement
            if abs(dx) > 1 or abs(dy) > 1:
                # Move the image
                self.canvas.move(self.image_canvas_id, dx, dy)
                
                # Update stored image position
                self.image_x += dx
                self.image_y += dy
                
                # Move all bounding box rectangles with the image
                for rect_id in self.box_rects:
                    self.canvas.move(rect_id, dx, dy)
                
                # Update pan start position for next movement
                self.pan_start_x = event.x
                self.pan_start_y = event.y

    def end_pan_or_draw(self, event):
        """End panning or drawing"""
        if self.rect:
            # Finish drawing bounding box
            ex = self.canvas.canvasx(event.x)
            ey = self.canvas.canvasy(event.y)
            x1, y1, x2, y2 = self.start_x, self.start_y, ex, ey
            
            # Only save if the box has some size
            if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                # Convert canvas coordinates to original image coordinates
                img_width, img_height = self.original_image.size
                # Adjust for image position
                x1_orig = (x1 - self.image_x) / self.scale_factor
                y1_orig = (y1 - self.image_y) / self.scale_factor
                x2_orig = (x2 - self.image_x) / self.scale_factor
                y2_orig = (y2 - self.image_y) / self.scale_factor
                
                # Normalize to image size
                x_center = (x1_orig + x2_orig) / 2 / img_width
                y_center = (y1_orig + y2_orig) / 2 / img_height
                width = abs(x2_orig - x1_orig) / img_width
                height = abs(y2_orig - y1_orig) / img_height
                class_id = 0  # Assume single class for now

                # Add to boxes list
                self.boxes.append((class_id, x_center, y_center, width, height))
                
                # Convert to permanent rectangle
                self.canvas.delete(self.rect)
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                self.box_rects.append(rect)
                
                # Save to label file
                self.save_labels()
                
                # Update zoom indicator without triggering image redraw
                self.update_zoom_indicator()
            else:
                # Delete the temporary rectangle if it's too small
                self.canvas.delete(self.rect)
            
            # Reset drawing state
            self.rect = None
            self.drawing_box = False  # Clear flag to allow zoom reset again
            
            # Restore zoom and position if they were changed during drawing
            if (hasattr(self, 'saved_scale_factor') and 
                (self.scale_factor != self.saved_scale_factor or 
                 self.image_x != self.saved_image_x or 
                 self.image_y != self.saved_image_y)):
                self.scale_factor = self.saved_scale_factor
                self.image_x = self.saved_image_x
                self.image_y = self.saved_image_y
                self.update_displayed_image()
                self.update_zoom_indicator()
            else:
                # Redraw all boxes to ensure they're properly positioned
                self.redraw_boxes()
        elif self.is_panning:
            # End panning
            self.canvas.config(cursor="")  # Reset cursor
            self.is_panning = False

    def clear_labels(self):
        """Remove all labels for the current image and delete label file."""
        if not self.image_path:
            return
        # Clear in-memory boxes and visuals
        self.boxes = []
        for rect_id in self.box_rects:
            self.canvas.delete(rect_id)
        self.box_rects = []
        # Remove label file if exists
        label_file = os.path.splitext(os.path.basename(self.image_path))[0] + ".txt"
        label_path = os.path.join(self.labels_dir, label_file)
        try:
            if os.path.exists(label_path):
                os.remove(label_path)
        except Exception as e:
            print(f"Error deleting label file: {e}")
        # Ensure UI reflects cleared state
        self.update_displayed_image()

    def on_canvas_enter(self, event):
        """Update cursor when mouse enters canvas"""
        # Always show panning cursor since we allow free dragging
        self.canvas.config(cursor="fleur")

    def on_canvas_leave(self, event):
        """Reset cursor when mouse leaves canvas"""
        self.canvas.config(cursor="")
    
    def on_mouse_motion(self, event):
        """Track mouse position for zoom centering"""
        # Use event coordinates for mouse motion (they're already relative to canvas)
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def save_labels(self):
        """Save all boxes to label file"""
        if not self.image_path:
            return
            
        label_file = os.path.splitext(os.path.basename(self.image_path))[0] + ".txt"
        label_path = os.path.join(self.labels_dir, label_file)
        
        with open(label_path, "w") as f:
            for class_id, x_center, y_center, width, height in self.boxes:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def undo_box(self):
        """Undo the last bounding box"""
        if self.boxes and self.box_rects:
            # Remove last box
            self.boxes.pop()
            self.canvas.delete(self.box_rects.pop())
            
            # Save updated labels
            self.save_labels()
            # Force a redraw so any stale rectangles disappear immediately
            self.update_displayed_image()

    def bind_mousewheel(self):
        """Bind mousewheel and mouse scroll events to the grid canvas for scrolling"""
        def _on_mousewheel(event):
            self.grid_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_mouse_scroll(event):
            # Handle mouse scroll events (Button-4 and Button-5)
            if event.num == 4:  # Scroll up
                self.grid_canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                self.grid_canvas.yview_scroll(1, "units")
        
        # Bind to the canvas and all its children
        self.grid_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.grid_canvas.bind_all("<Button-4>", _on_mouse_scroll)
        self.grid_canvas.bind_all("<Button-5>", _on_mouse_scroll)
        
    def unbind_mousewheel(self):
        """Unbind mousewheel and mouse scroll events"""
        self.grid_canvas.unbind_all("<MouseWheel>")
        self.grid_canvas.unbind_all("<Button-4>")
        self.grid_canvas.unbind_all("<Button-5>")
        
    def grid_scroll_up(self):
        """Scroll up in grid view"""
        if self.grid_canvas.winfo_viewable():
            self.grid_canvas.yview_scroll(-1, "units")
            
    def grid_scroll_down(self):
        """Scroll down in grid view"""
        if self.grid_canvas.winfo_viewable():
            self.grid_canvas.yview_scroll(1, "units")
    
    def bind_zoom_mousewheel(self):
        """Bind mousewheel and mouse scroll events to the canvas for zooming"""
        def _on_zoom_mousewheel(event):
            # Get the actual mouse position relative to the canvas
            self.last_mouse_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            self.last_mouse_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            # Zoom in/out based on scroll direction with debouncing
            if event.delta > 0:  # Scroll up - zoom in
                self.debounced_zoom_in()
            else:  # Scroll down - zoom out
                self.debounced_zoom_out()
        
        def _on_zoom_mouse_scroll(event):
            # Get the actual mouse position relative to the canvas
            self.last_mouse_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            self.last_mouse_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            # Handle mouse scroll events (Button-4 and Button-5) for zooming with debouncing
            if event.num == 4:  # Scroll up - zoom in
                self.debounced_zoom_in()
            elif event.num == 5:  # Scroll down - zoom out
                self.debounced_zoom_out()
        
        # Bind to the canvas
        self.canvas.bind_all("<MouseWheel>", _on_zoom_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_zoom_mouse_scroll)
        self.canvas.bind_all("<Button-5>", _on_zoom_mouse_scroll)
        
    def unbind_zoom_mousewheel(self):
        """Unbind zoom mousewheel and mouse scroll events"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabeler(root)
    root.mainloop()
