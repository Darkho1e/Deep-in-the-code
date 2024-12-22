import os
import pygame
import sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Settings")


def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def draw_slider(x, y, width, height, value):
    # Draw the track
    track_rect = pygame.Rect(x, y + height // 2 - 5, width, 10)
    pygame.draw.rect(screen, WHITE, track_rect)

    # Draw the knob
    knob_width = 20
    knob_rect = pygame.Rect(x + (width - knob_width) * value, y, knob_width, height)
    pygame.draw.rect(screen, WHITE, knob_rect)


def settings_screen():
    background_images = []
    background_images_path = "assets/Background"
    for i in range(1, 8):  # Assuming you have images named BackgroundImage_1.png to BackgroundImage_7.png
        image_path = os.path.join(background_images_path, f"BackgroundImage_{i}.png")
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (WIDTH, HEIGHT))
        background_images.append(image)

    font = pygame.font.Font(None, 50)
    back_button = pygame.Rect(10, 10, 100, 50)

    volume_slider = pygame.Rect(WIDTH / 2 - 150, HEIGHT / 2 - 25, 300, 50)
    volume = 0.5  # Initial volume value (0 to 1)


    frame_index = 0
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    if volume_slider.collidepoint(event.pos):
                        # Calculate the relative position of the mouse click within the slider
                        relative_pos = event.pos[0] - volume_slider.left
                        volume = max(0, min(1, relative_pos / volume_slider.width))
                        # Set the volume of the menu music based on the slider position
                        pygame.mixer.music.set_volume(volume)
                    elif back_button.collidepoint(event.pos):
                        return "menu"  # Return to the main menu when the back button is clicked

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button held while moving
                    if volume_slider.collidepoint(event.pos):
                        # Calculate the relative position of the mouse drag within the slider
                        relative_pos = event.pos[0] - volume_slider.left
                        volume = max(0, min(1, relative_pos / volume_slider.width))
                        # Set the volume of the menu music based on the slider position
                        pygame.mixer.music.set_volume(volume)

        # Draw the background
        screen.blit(background_images[frame_index], (0, 0))

        # Draw the buttons
        pygame.draw.rect(screen, BLACK, back_button)
        draw_text("Back", font, WHITE, 60, 35)

        # Draw the volume slider
        draw_slider(volume_slider.left, volume_slider.top, volume_slider.width, volume_slider.height, volume)

        # Draw the volume percentage as text
        volume_percentage = int(volume * 100)
        draw_text(f"Volume: {volume_percentage}%", font, WHITE, WIDTH / 2, HEIGHT / 2 + 100)

        frame_index = (frame_index + 1) % len(background_images)

        # Update the screen
        pygame.display.flip()


def main():
    while True:
        next_screen = settings_screen()

        if next_screen == "menu":
            return


if __name__ == "__main__":
    main()
