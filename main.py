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
    def __init__(self, shape_type: str, color: str, size: float, rel_pos, parent=None, interactable=False, has_border=False, border_thickness=3, z_order=0):
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

    def draw(self, screen, root_size, mouse_pos, mouse_click_pos):
        size = self.get_pixel_size(root_size)
        pos = self.get_absolute_position(root_size)

        rect = pygame.Rect(
            pos[0] - size[0] // 2,
            pos[1] - size[1] // 2,
            size[0],
            size[1]
        )

        # Interactable behavior
        draw_color = get_color(self.color)
        if self.interactable and rect.collidepoint(mouse_pos):
            draw_color = tuple(min(c + 40, 255) for c in draw_color)  # lighten on hover
            if mouse_click_pos and rect.collidepoint(mouse_click_pos):
                print(f"{self.shape_type.capitalize()} was clicked!")

        # Draw shape
        if self.shape_type == "square":
            pygame.draw.rect(screen, draw_color, rect)
        elif self.shape_type == "circle":
            pygame.draw.circle(screen, draw_color, pos, size[0] // 2)
        else:
            print(f"Unsupported shape: {self.shape_type}")

        # Draw matching border if requested
        if self.has_border:
            border_color = get_color("black")
            if self.shape_type == "square":
                pygame.draw.rect(screen, border_color, rect, self.border_thickness)
            elif self.shape_type == "circle":
                pygame.draw.circle(screen, border_color, pos, size[0] // 2 + self.border_thickness // 2, self.border_thickness)
        
        # Draw children recursively
        for child in sorted(self.children, key=lambda x: x.z_order):
            child.draw(screen, root_size, mouse_pos, mouse_click_pos)

def create_safe(open: bool, sizeMult: float):
    safe_size = 0.7 * sizeMult
    safe_bg = Shape("square", "gray", safe_size, (0.5, 0.5), interactable=False, has_border=True, z_order=1)

    door = Shape("square", "gray", 0.5, (0.0 * safe_size, 0.0 * safe_size), parent=safe_bg, interactable=True, has_border=True, z_order=2)
    
    screw_size = 0.1 * sizeMult
    screw_position = (0.5 * safe_size) + (0.5 * screw_size)
    screw1 = Shape("circle", "lightgray", screw_size, (-screw_position, -screw_position), parent=safe_bg, interactable=True, has_border=True, z_order=3)
    screw2 = Shape("circle", "lightgray", screw_size, (screw_position, -screw_position), parent=safe_bg, interactable=True, has_border=True, z_order=3)
    screw3 = Shape("circle", "lightgray", screw_size, (-screw_position, screw_position), parent=safe_bg, interactable=True, has_border=True, z_order=3)
    screw4 = Shape("circle", "lightgray", screw_size, (screw_position, screw_position), parent=safe_bg, interactable=True, has_border=True, z_order=3)

    dial_size = 0.3 * sizeMult
    dial = Shape("circle", "lightgray", dial_size, (0, 0), parent=safe_bg, interactable=True, has_border=True, z_order=3)

    return safe_bg
                      
    

# -------- Main Program --------
running = True
mouse_click_pos = None

# Define shapes
# root_shape = Shape("square", "gray", 0.3, (0.5, 0.5), interactable=True, has_border=True, border_thickness=5)
# child1 = Shape("circle", "blue", 0.1, (1.0, 0.0), parent=root_shape, interactable=True, has_border=True, border_thickness=3)
# child2 = Shape("square", "red", 0.1, (0.0, 1.0), parent=root_shape, interactable=True, has_border=True, border_thickness=2)

safe = create_safe(False, 1.0)

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

    # Draw the full shape hierarchy starting from the root
    safe.draw(screen, (width, height), mouse_pos, mouse_click_pos)

    # Text
    display_message("Hello Player!", 0.1, 0.1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
