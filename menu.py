import pygame
import sys
import GameScreen
import os

import Settings

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deep")


def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def main_menu():
    font = pygame.font.Font(None, 50)
    start_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 50, 200, 50)
    settings_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 25, 200, 50)
    quit_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 100, 200, 50)

    # Load the background images
    background_images = []
    background_images_path = "assets/Background"
    for i in range(1, 8):  # Assuming you have images named BackgroundImage_1.png to BackgroundImage_7.png
        image_path = os.path.join(background_images_path, f"BackgroundImage_{i}.png")
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (WIDTH, HEIGHT))
        background_images.append(image)

    menu_music_path = "assets/music/menuMusic.mp3"
    pygame.mixer.music.load(menu_music_path)
    pygame.mixer.music.play(-1)  # The -1 means the music will loop forever

    frame_index = 0
    clock = pygame.time.Clock()
    transition_timer = 0
    transition_duration = 4  # 4 seconds for the transition animation

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.collidepoint(mouse_pos):
                    pygame.mixer.music.fadeout(1000)  # Fade out the menu music (1 second)

                    # Transition animation loop
                    for i in range(transition_duration * 60):  # 60 frames per second
                        alpha_value = int(255 - 255 * (i / (transition_duration * 60)))
                        screen.fill((0, 0, 0))  # Clear the screen with black

                        # Draw the previous background image with full opacity
                        screen.blit(background_images[frame_index], (0, 0))

                        # Draw the next background image with alpha blending
                        next_frame_index = (frame_index + 6) % len(background_images)
                        next_image = pygame.Surface((WIDTH, HEIGHT))
                        next_image.set_alpha(alpha_value)
                        next_image.blit(background_images[next_frame_index], (0, 0))
                        screen.blit(next_image, (0, 0))

                        pygame.display.flip()
                        clock.tick(60)

                    frame_index = (frame_index + 1) % len(background_images)  # Update frame_index for next iteration

                    return "game"
                elif settings_button.collidepoint(mouse_pos):
                    Settings.main()  # Open the settings screen
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Display the current background image
        screen.blit(background_images[frame_index], (0, 0))

        # Draw the buttons
        pygame.draw.rect(screen, BLACK, start_button)
        draw_text("START", font, WHITE, WIDTH / 2, HEIGHT / 2 - 25)

        pygame.draw.rect(screen, BLACK, settings_button)
        draw_text("SETTINGS", font, WHITE, WIDTH / 2, HEIGHT / 2 + 50)

        pygame.draw.rect(screen, BLACK, quit_button)
        draw_text("QUIT GAME", font, WHITE, WIDTH / 2, HEIGHT / 2 + 125)

        # Update the frame index for the next iteration
        frame_index = (frame_index + 1) % len(background_images)

        # Update the screen
        pygame.display.flip()
        clock.tick(60)
def settings_screen():
    pass


def main():
    while True:
        next_screen = main_menu()

        if next_screen == "game":
            GameScreen.game_screen()
        elif next_screen == "settings":
            settings_screen()


if __name__ == "__main__":
    main()
