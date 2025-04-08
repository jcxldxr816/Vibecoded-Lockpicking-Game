import pygame
import sys

pygame.init()

# Set up window
width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Shape Hierarchy with Matching Borders")

clock = pygame.time.Clock()

# Define the font and color customization
default_font = "arial"
default_font_size = 24
default_font_color = (255, 255, 0)

def display_message(message, pos_x, pos_y, font_size=default_font_size, font_color=default_font_color):
    """Displays a given message at a position relative to the window size."""
    # Convert relative positions (float) to pixel positions
    x = pos_x * width
    y = pos_y * height
    
    # Resize font based on window size (optional scaling factor)
    scale_factor = width / 800  # Scale based on window width
    scaled_font_size = int(font_size * scale_factor)
    
    # Create a font object with the new size
    font = pygame.font.SysFont(default_font, scaled_font_size)
    
    # Render the message
    text = font.render(message, True, font_color)
    
    # Get the rect of the text to position it
    text_rect = text.get_rect()
    text_rect.topleft = (x, y)
    
    # Draw the text onto the screen
    screen.blit(text, text_rect)

# Color name → RGB
def get_color(name):
    colors = {
        "gray": (128, 128, 128),
        "lightgray": (180, 180, 180),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
    }
    return colors.get(name.lower(), (255, 255, 255))  # default to white

class Shape:
    def __init__(self, shape_type: str, color: str, size: float, rel_pos, parent=None, 
                 interactable=False, has_border=False, border_thickness=3, z_order=0):
        self.shape_type = shape_type
        self.color = color
        self.size = size  # scale factor (0.0 to 1.0)
        self.rel_pos = rel_pos  # (x, y) relative to parent or screen
        self.parent = parent
        self.children = []
        self.interactable = interactable
        self.has_border = has_border
        self.border_thickness = border_thickness
        self.z_order = z_order
        self.scene = None  # Will be set when added to scene

        if parent:
            parent.children.append(self)

    def get_absolute_position(self, root_size):
        """Calculate screen-space position based on parent or window."""
        if self.parent:
            parent_pos = self.parent.get_absolute_position(root_size)
            parent_size = self.parent.get_pixel_size(root_size)
            return (
                parent_pos[0] + int(parent_size[0] * self.rel_pos[0]),
                parent_pos[1] + int(parent_size[1] * self.rel_pos[1])
            )
        else:
            return (
                int(root_size[0] * self.rel_pos[0]),
                int(root_size[1] * self.rel_pos[1])
            )

    def get_pixel_size(self, root_size):
        base = min(root_size)
        return (int(base * self.size), int(base * self.size))

    def check_interaction(self, screen_pos, size, mouse_pos):
        """Returns True if mouse is over this shape"""
        rect = pygame.Rect(
            screen_pos[0] - size[0] // 2,
            screen_pos[1] - size[1] // 2,
            size[0],
            size[1]
        )
        
        if self.shape_type == "square":
            return rect.collidepoint(mouse_pos)
        elif self.shape_type == "circle":
            # For circles, check if mouse is within radius
            center = (screen_pos[0], screen_pos[1])
            radius = size[0] // 2
            dx = mouse_pos[0] - center[0]
            dy = mouse_pos[1] - center[1]
            return (dx * dx + dy * dy) <= (radius * radius)
        return False

    def draw(self, screen, root_size):
        """Draw the shape normally"""
        size = self.get_pixel_size(root_size)
        pos = self.get_absolute_position(root_size)
        
        draw_color = get_color(self.color)
        self._draw_shape(screen, pos, size, draw_color)
        if self.has_border:
            self._draw_border(screen, pos, size)
            
    def draw_highlighted(self, screen, root_size):
        """Draw the shape in its highlighted state"""
        size = self.get_pixel_size(root_size)
        pos = self.get_absolute_position(root_size)
        
        highlight_color = tuple(min(c + 40, 255) for c in get_color(self.color))
        self._draw_shape(screen, pos, size, highlight_color)
        if self.has_border:
            self._draw_border(screen, pos, size)
            
    def _draw_shape(self, screen, pos, size, color):
        """Internal method for drawing the shape"""
        if self.shape_type == "square":
            pygame.draw.rect(screen, color, pygame.Rect(
                pos[0] - size[0] // 2,
                pos[1] - size[1] // 2,
                size[0],
                size[1]
            ))
        elif self.shape_type == "circle":
            pygame.draw.circle(screen, color, pos, size[0] // 2)
            
    def _draw_border(self, screen, pos, size):
        """Internal method for drawing the border"""
        border_color = get_color("black")
        if self.shape_type == "square":
            pygame.draw.rect(screen, border_color, pygame.Rect(
                pos[0] - size[0] // 2,
                pos[1] - size[1] // 2,
                size[0],
                size[1]
            ), self.border_thickness)
        elif self.shape_type == "circle":
            pygame.draw.circle(screen, border_color, pos, 
                size[0] // 2 + self.border_thickness // 2, 
                self.border_thickness)

    def handle_click(self):
        """Handle click events"""
        print(f"{self.shape_type.capitalize()} (z:{self.z_order}) was clicked!")
        # Future: self.on_click()

class SceneManager:
    def __init__(self):
        self.root_shapes = []
        self.all_shapes = []  # Flat list for easy z-order operations
        
    def add_shape(self, shape):
        if not shape.parent:
            self.root_shapes.append(shape)
        self.all_shapes.append(shape)
        
    def get_shape_at(self, mouse_pos, root_size):
        # Get all shapes under the mouse, sorted by z-order (highest first)
        shapes_under_mouse = [
            shape for shape in sorted(self.all_shapes, key=lambda x: -x.z_order)
            if shape.interactable and shape.check_interaction(
                shape.get_absolute_position(root_size),
                shape.get_pixel_size(root_size),
                mouse_pos
            )
        ]
        return shapes_under_mouse[0] if shapes_under_mouse else None
    
    def draw(self, screen, root_size, mouse_pos, mouse_click_pos):
        # First pass: Draw all shapes in normal state
        for shape in sorted(self.all_shapes, key=lambda x: x.z_order):
            shape.draw(screen, root_size)
            
        # Second pass: Draw only the hovered shape again with highlight
        # (if it exists and is interactable)
        hovered_shape = self.get_shape_at(mouse_pos, root_size)
        if hovered_shape:
            # Draw all shapes that are above our hovered shape again
            # to maintain proper z-ordering
            hover_z = hovered_shape.z_order
            
            # Draw the highlight
            hovered_shape.draw_highlighted(screen, root_size)
            
            # Redraw any shapes that should appear above the highlighted shape
            for shape in sorted(self.all_shapes, key=lambda x: x.z_order):
                if shape.z_order > hover_z:
                    shape.draw(screen, root_size)
            
            # Handle click if needed
            if mouse_click_pos and hovered_shape.check_interaction(
                hovered_shape.get_absolute_position(root_size),
                hovered_shape.get_pixel_size(root_size),
                mouse_click_pos
            ):
                hovered_shape.handle_click()

def create_safe(open: bool, sizeMult: float):
    scene = SceneManager()
    
    safe_size = 0.7 * sizeMult
    safe_bg = Shape("square", "gray", safe_size, (0.5, 0.5), 
                    interactable=False, has_border=True, z_order=0)
    scene.add_shape(safe_bg)

    door = Shape("square", "gray", 0.5, (0.0 * safe_size, 0.0 * safe_size), 
                 parent=safe_bg, interactable=True, has_border=True, z_order=10)
    scene.add_shape(door)
    
    screw_size = 0.1 * sizeMult
    screw_position = (0.5 * safe_size) + (0.5 * screw_size)
    screws = []
    for pos in [(-screw_position, -screw_position),
                (screw_position, -screw_position),
                (-screw_position, screw_position),
                (screw_position, screw_position)]:
        screw = Shape("circle", "lightgray", screw_size, pos,
                     parent=safe_bg, interactable=True, has_border=True, z_order=20)
        scene.add_shape(screw)
        screws.append(screw)

    dial_size = 0.3 * sizeMult
    dial = Shape("circle", "lightgray", dial_size, (0, 0),
                 parent=safe_bg, interactable=True, has_border=True, z_order=30)
    scene.add_shape(dial)

    return scene
                      
    

# -------- Main Program --------
running = True
mouse_click_pos = None

# Define shapes
safe_scene = create_safe(False, 1.0)

while running:
    mouse_click_pos = None
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click_pos = event.pos

    screen.fill((30, 30, 30))

    # Draw the full shape hierarchy using the scene manager
    safe_scene.draw(screen, (width, height), mouse_pos, mouse_click_pos)

    # Text
    display_message("Hello Player!", 0.1, 0.1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
