import pygame
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# Constants for the game
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

# Secret key for AES encryption (set to 2003 as a fixed key)
SECRET_KEY = b'2003'  # Key length needs to be 16, 24, or 32 bytes, so we pad it if necessary.
SECRET_KEY = SECRET_KEY.ljust(16, b'\0')  # Ensure the key is 16 bytes long.


def encrypt_data(data):
    """Encrypts the given data using AES encryption."""
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct


def decrypt_data(iv, encrypted_data):
    """Decrypts the given encrypted data using AES decryption."""
    iv = base64.b64decode(iv)
    encrypted_data = base64.b64decode(encrypted_data)
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')
    return decrypted_data


def save_game_data(player_name, player_x, player_y, npc_interacted, filename="AllSave.txt"):
    """Saves game data (player name, position, NPC interaction status) to a file."""
    try:
        iv, encrypted_name = encrypt_data(f"NAME:{player_name}")
        game_data = f"X:{player_x}\nY:{player_y}\nNPC_INTERACTED:{npc_interacted}"
        iv_game_data, encrypted_game_data = encrypt_data(game_data)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"IV:{iv}\n")
            file.write(f"Data:{encrypted_name}\n")
            file.write(f"GameDataIV:{iv_game_data}\n")
            file.write(f"GameData:{encrypted_game_data}\n")

        print(f"Game data saved successfully!")
    except Exception as e:
        print(f"Error saving game data: {e}")


def load_game_data(filename="AllSave.txt"):
    """Loads game data (player name, position, NPC interaction status) from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            iv_line = file.readline().strip()
            data_line = file.readline().strip()
            iv_game_data_line = file.readline().strip()
            game_data_line = file.readline().strip()

            iv = iv_line.split("IV:")[1]
            encrypted_data = data_line.split("Data:")[1]
            iv_game_data = iv_game_data_line.split("GameDataIV:")[1]
            encrypted_game_data = game_data_line.split("GameData:")[1]

            player_name = decrypt_data(iv, encrypted_data)
            game_data = decrypt_data(iv_game_data, encrypted_game_data)

            # Parse the game data for position and NPC interaction status
            game_data_dict = dict(line.split(":") for line in game_data.split("\n"))
            player_x = int(game_data_dict.get("X", 400))  # Default position if no data found
            player_y = int(game_data_dict.get("Y", 300))
            npc_interacted = game_data_dict.get("NPC_INTERACTED", "False") == "True"

            return player_name.replace("NAME:", ""), player_x, player_y, npc_interacted
    except Exception as e:
        print(f"Error loading game data: {e}")
        return None, 400, 300, False  # Default values if loading fails


class GameScreen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Your Game")
        self.clock = pygame.time.Clock()

        # Load game data (player name, position, and NPC interaction status)
        self.player_name, self.player_x, self.player_y, self.npc_interacted = load_game_data()  # Load all data
        if not self.player_name:
            self.player_name = "Player"  # Default name if no name is loaded

        # Other variables
        self.player_direction = "left"
        self.offset_x, self.offset_y = 0, 0
        self.chat_stage, self.chat_open = 0, False
        self.npc_frame_index, self.npc_animation_timer = 0, pygame.time.get_ticks()
        self.npc_x, self.npc_y = 400, 200
        self.input_active = False  # Add this line to initialize the input_active variable

        try:
            self.player_image_idle = pygame.image.load("assets/Player_image/SingeIdleLeft.png")
            self.player_image_idle_right = pygame.image.load("assets/Player_image/SingeIdleRight.png")
            self.npc_frames = [
                pygame.transform.scale(
                    pygame.image.load(f"assets/NPC/ComputerNPC{i}.png"),
                    (50, 50)
                )
                for i in range(1, 15)
            ]
        except pygame.error as e:
            print(f"Error loading images: {e}")
            sys.exit()

        # NPC messages hardcoded instead of from a file
        self.npc_messages = [
            "Hello, welcome to the game!",
            "I hope you enjoy your adventure.",
            "Let me know if you need any help.",
            "Good luck on your journey!"
        ]

    def split_text(self, text, font, max_width):
        """Splits text into multiple lines to fit within the specified width."""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def display_player(self, x, y, direction):
        if direction == "right":
            self.screen.blit(self.player_image_idle_right, (x - self.offset_x, y - self.offset_y))
        else:
            self.screen.blit(self.player_image_idle, (x - self.offset_x, y - self.offset_y))

        font = pygame.font.Font(None, 36)
        name_text = font.render(self.player_name, True, GOLD)
        name_rect = name_text.get_rect(center=(x - self.offset_x + 25, y - self.offset_y - 20))
        self.screen.blit(name_text, name_rect)

    def display_npc(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.npc_animation_timer > 100:
            self.npc_frame_index = (self.npc_frame_index + 1) % len(self.npc_frames)
            self.npc_animation_timer = current_time

        self.screen.blit(self.npc_frames[self.npc_frame_index],
                         (self.npc_x - self.offset_x, self.npc_y - self.offset_y))

    def display_button(self, text, x, y):
        font = pygame.font.Font(None, 36)
        button_rect = pygame.Rect(x, y, 120, 40)
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, button_rect)
        else:
            pygame.draw.rect(self.screen, WHITE, button_rect)

        button_text = font.render(text, True, BLACK)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)
        return button_rect

    def npc_interaction(self):
        if self.npc_interacted:
            return  # If already interacted with NPC, don't allow another interaction

        font = pygame.font.Font(None, 36)
        player_name = ""

        while self.chat_open:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        else:
                            player_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.display_button("ENTER", WIDTH // 2 - 140, HEIGHT // 2 + 100).collidepoint(mouse_pos):
                        self.player_name = player_name
                        self.chat_open = False
                        self.chat_stage = 1  # Switch to stage 1 of the chat
                        self.npc_interacted = True
                        save_game_data(self.player_name, self.player_x, self.player_y,
                                       self.npc_interacted)  # Save the data
                        return
                    if self.display_button("CANCEL", WIDTH // 2 + 20, HEIGHT // 2 + 100).collidepoint(mouse_pos):
                        self.chat_open = False
                        return

            input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)
            if input_box.collidepoint(pygame.mouse.get_pos()) or self.input_active:
                self.input_active = True

            self.screen.fill(BLACK)
            text = font.render("Enter your name:", True, WHITE)  # Text in English
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            self.screen.blit(text, text_rect)
            pygame.draw.rect(self.screen, WHITE, input_box, 2)
            name_text = font.render(player_name, True, WHITE)
            self.screen.blit(name_text, (input_box.x + 10, input_box.y + 10))

            # Display buttons for interaction
            self.display_button("ENTER", WIDTH // 2 - 140, HEIGHT // 2 + 100)
            self.display_button("CANCEL", WIDTH // 2 + 20, HEIGHT // 2 + 100)

            pygame.display.flip()

    def npc_stage_one(self):
        """Stage 1: Display a message with split text."""
        font = pygame.font.Font(None, 36)
        message = f"NPC: Welcome, {self.player_name} To DEEP IN THE CODE. You must complete tasks before the computer monster kills you!!"
        max_width = WIDTH - 40  # Set the max width for the message
        lines = self.split_text(message, font, max_width)

        y_offset = HEIGHT // 2 - len(lines) * 20 // 2  # Adjust vertical position based on the number of lines
        for line in lines:
            text = font.render(line, True, WHITE)
            self.screen.blit(text, (20, y_offset))
            y_offset += 40  # Space between lines

        pygame.display.flip()

    def game_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x -= 5
                self.player_direction = "left"
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x += 5
                self.player_direction = "right"
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player_y -= 5
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player_y += 5

            # If the player hasn't interacted with the NPC yet, allow interaction
            if keys[pygame.K_e] and not self.chat_open and not self.npc_interacted:
                if abs(self.player_x - self.npc_x) < 50 and abs(self.player_y - self.npc_y) < 50:
                    self.chat_open = True
                    self.npc_interaction()

            if self.chat_stage == 1 and self.chat_open:
                self.npc_stage_one()  # Show the stage 1 message

            self.offset_x = self.player_x - WIDTH // 2
            self.offset_y = self.player_y - HEIGHT // 2

            self.screen.fill(BLACK)
            self.display_npc()
            self.display_player(self.player_x, self.player_y, self.player_direction)

            pygame.display.flip()
            self.clock.tick(60)


def game_screen():
    game = GameScreen()
    game.game_loop()


if __name__ == "__main__":
    game_screen()
