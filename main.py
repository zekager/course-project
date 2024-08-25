import tkinter as tk
import time
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.ttk import Progressbar
import sqlite3
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import bcrypt

def load_screen():
    def start_loading():
        root.destroy()
        start_game()

    root = tk.Tk()
    root.title("Завантаження...")
    root.geometry("300x300")
    root.config(bg="#f0f0f0")


    file_path = 'mon.png'
    if not path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
    else:
        bg_image = tk.PhotoImage(file=file_path)
        bg_label = tk.Label(root, image=bg_image)
        bg_label.place(relwidth=1, relheight=1)

    label = tk.Label(root, text="Містичний мисливець", font=("Anticva-Regular.otf", 18), bg="#f0f0f0")
    label.pack(pady=120)

    progressbar = Progressbar(root, length=150, mode="determinate")
    progressbar["maximum"] = 100
    progressbar.pack()

    def update_progressbar():
        progressbar["value"] += 10
        if progressbar["value"] >= 100:
            start_loading()
        else:
            root.after(100, update_progressbar)

    update_progressbar()

    root.mainloop()

def start_game():
    print("")

load_screen()

root = tk.Tk()
root.title("Автентифікація користувача")
root.geometry("500x500")  
root.config(bg="#f0f0f0")

icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')
conn.commit()

c.execute('''
    CREATE TABLE IF NOT EXISTS levels_completed (
        username TEXT PRIMARY KEY,
        last_level INTEGER NOT NULL
    )
''')
conn.commit()

c.execute('''
    CREATE TABLE IF NOT EXISTS coins (
        username TEXT NOT NULL,
        coins INTEGER NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    )
''')
conn.commit()

current_user = None

def register_user():
    username = username_entry.get()
    password = password_entry.get()
    phone = phone_entry.get()
    email = email_entry.get()
    
    if username and password and phone and email:
        if not phone.isdigit():
            messagebox.showerror("Error", "Phone number must contain only digits")
            return
        if len(phone) != 12:  
            messagebox.showerror("Error", "Phone number must be 10 digits long")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            c.execute("INSERT INTO users (username, password, phone, email) VALUES (?, ?, ?, ?)",
                      (username, hashed_password, phone, email))
            conn.commit()
            messagebox.showinfo("Success", "Registration Successful")
            switch_to_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    else:
        messagebox.showerror("Error", "Please fill in all fields")

def login_user():
    global current_user
    username = login_username_entry.get()
    password = login_password_entry.get()
    
    if username and password:
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            messagebox.showinfo("Success", "Login Successful")
            current_user = username  
            root.destroy()
            start_game()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    else:
        messagebox.showerror("Error", "Please fill in all fields")

def switch_to_login():
    register_frame.pack_forget()
    login_frame.pack()

def switch_to_register():
    login_frame.pack_forget()
    register_frame.pack()

register_frame = tk.Frame(root)
register_frame.config(bg="#f0f0f0")
register_frame.place(relx=0.5, rely=0.5, anchor="center")  

tk.Label(register_frame, text="Register", font=('Helvetica', 20), bg="#f0f0f0").pack(pady=10)
tk.Label(register_frame, text="Username", bg="#f0f0f0").pack()
username_entry = tk.Entry(register_frame, bg="#e3e3e3", bd=0)
username_entry.pack()
tk.Label(register_frame, text="Password", bg="#f0f0f0").pack()
password_entry = tk.Entry(register_frame, show='*', bg="#e3e3e3", bd=0)
password_entry.pack()
tk.Label(register_frame, text="Phone Number", bg="#f0f0f0").pack()
phone_entry = tk.Entry(register_frame, bg="#e3e3e3", bd=0)
phone_entry.pack()
tk.Label(register_frame, text="Email", bg="#f0f0f0").pack()
email_entry = tk.Entry(register_frame, bg="#e3e3e3", bd=0)
email_entry.pack()
tk.Button(register_frame, text="Register", command=register_user, bg="#4caf50", fg="white", bd=0).pack(pady=10)
tk.Button(register_frame, text="Switch to Login", command=switch_to_login, bg="#2196f3", fg="white", bd=0).pack(pady=10)

login_frame = tk.Frame(root)
login_frame.config(bg="#f0f0f0")
tk.Label(login_frame, text="Login", font=('Helvetica', 20), bg="#f0f0f0").pack(pady=10)
tk.Label(login_frame, text="Username", bg="#f0f0f0").pack()
login_username_entry = tk.Entry(login_frame, bg="#e3e3e3", bd=0)
login_username_entry.pack()
tk.Label(login_frame, text="Password", bg="#f0f0f0").pack()
login_password_entry = tk.Entry(login_frame, show='*', bg="#e3e3e3", bd=0)
login_password_entry.pack()
tk.Button(login_frame, text="Login", command=login_user, bg="#4caf50", fg="white", bd=0).pack(pady=10)
tk.Button(login_frame, text="Switch to Register", command=switch_to_register, bg="#2196f3", fg="white", bd=0).pack(pady=10)

root.mainloop()


def show_rules_messagebox():
    rules_text = (
        "Правила гри:\n"
        "1. Використовуйте стрілки для переміщення.\n"
        "2. Натиcкайте на пробіл для стрибка.\n"
        "3. Збирайте монети та уникайте ворогів та лави.\n"
        "4. Досягніть виходу, щоб завершити рівень.\n"
        "\n"
        "Rules: \n"
        "1. Use arrows to move. \n"
        "2. Press the space bar to jump. \n"
        "3. Collect coins and avoid enemies and lava. \n"
        "4. Reach the exit to complete the level."
    )
    messagebox.showinfo("Правила гри", rules_text)

def update_last_level(username, last_level):
    c.execute("SELECT * FROM levels_completed WHERE username =?", (username,))
    record = c.fetchone()
    if record:
        c.execute("UPDATE levels_completed SET last_level =? WHERE username =?", (last_level, username))
    else:
        c.execute("INSERT INTO levels_completed (username, last_level) VALUES (?,?)", (username, last_level))
    conn.commit()

def update_coins(username, coins):
    c.execute("SELECT * FROM coins WHERE username = ?", (username,))
    record = c.fetchone()
    if record:
        c.execute("UPDATE coins SET coins = coins + ? WHERE username = ?", (coins, username))
    else:
        c.execute("INSERT INTO coins (username, coins) VALUES (?, ?)", (username, coins))
    
    conn.commit()

# Запуск Pygame игры после успешного логина
def start_game():
    pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Містичний мисливець')

font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_level = pygame.font.SysFont('Bauhaus 93', 30)
loading_font = pygame.font.SysFont('Bauhaus 93', 50)  # Font for loading screen

icon = pygame.image.load('icon1.png')
pygame.display.set_icon(icon)

# Определение переменных игры
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_level = 7
score = 0

# Определение цветов
white = (255, 255, 255)
black=(0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# Загрузка звуков
pygame.mixer.music.load('1bg_music.mp3')
pygame.mixer.music.play(-1, 0.0, 0)
coin_fx = pygame.mixer.Sound('coin.mp3')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('jump.mp3')
jump_fx.set_volume(0.1)
game_over_fx = pygame.mixer.Sound('game_over.mp3')
game_over_fx.set_volume(0.5)

# Загрузка изображений
bg_img = pygame.image.load('sky.png')
restart_img = pygame.image.load('restart.png')
start_img = pygame.image.load('start.png')
exit_img = pygame.image.load('quit.png')
music_on_img = pygame.image.load('music_on.png')
music_off_img = pygame.image.load('music_off.png')
sfx_on_img = pygame.image.load('sfx_on.png')
sfx_off_img = pygame.image.load('sfx_off.png')
rules_img = pygame.image.load('rules.png')



def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(100, screen_height - 130)
    skeleton_group.empty()
    Platfom_group.empty()
    lava_group.empty()
    exit_group.empty()

    # Загрузка данных уровня и создание мира
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Получение позиции мыши
        pos = pygame.mouse.get_pos()

        # Проверка нажатия
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка кнопки
        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:

            # Управление
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Обработка анимации
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Добавление гравитации
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Проверка столкновений
            self.in_air = True
            for tile in world.tile_list:
                # Проверка столкновения по x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Проверка столкновения по y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Проверка столкновений с врагами
            if pygame.sprite.spritecollide(self, skeleton_group, False):
                game_over = -1
                game_over_fx.play()
            # Проверка столкновений с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # Проверка столкновений с выходом
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # Проверка столкновений с платформами
            for platform in Platfom_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text("Game over", font, red, (screen_width // 2) - 130, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'R{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('ghost (2).png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load('grassCenter.png')
        grass_img = pygame.image.load('grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    skeleton = Enemy(col_count * tile_size, row_count * tile_size + 12)
                    skeleton_group.add(skeleton)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    Platfom_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    Platfom_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 3))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

def draw_level(level):
    level_text = f"Level: {level}"
    img = font_level.render(level_text, True, white)
    screen.blit(img, (screen_width - 150, 10))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('platform_x.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def draw_pause_menu():
    draw_text('PAUSED', font, black, (screen_width // 2) -92, screen_height // 2 - 350)

player = Player(100, screen_height - 123)

skeleton_group = pygame.sprite.Group()
Platfom_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Создание временной монеты для отображения счета
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Загрузка данных уровня и создание мира
if path.exists(f'level{level}_data'):
    with open(f'level{level}_data', 'rb') as pickle_in:
        world_data = pickle.load(pickle_in)
world = World(world_data)

# Создание кнопок
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
quit_button = Button(screen_width // 2 - 50, screen_height // 2 + 240, exit_img)  # Измененные координаты y
start_button = Button(425, 250, start_img)
exit_button = Button(425, 500, exit_img)
music_button = Button(10, screen_height - 260, music_on_img)
sfx_button = Button(10, screen_height - 150, sfx_on_img)
rules_button = Button(425, 370, rules_img)

paused = False

# Кнопки для меню паузы
pause_restart_button = Button(screen_width // 2 - 50, screen_height // 2 -250, restart_img)
pause_music_button = Button(screen_width // 2 - 50, screen_height // 2 - 125, music_on_img)
pause_sfx_button = Button(screen_width // 2 - 50, screen_height // 2 - 0  , sfx_on_img)
pause_quit_button = Button(screen_width // 2 - 50, screen_height // 2 +125, exit_img)


music_on = True
sfx_on = True

run = True
show_rules = False

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused  # Переключение состояния паузы

    # Отрисовка заднего фона
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))

    if main_menu:
        if music_button.draw():
            music_on = not music_on
            if music_on:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            music_button.image = music_on_img if music_on else music_off_img

        if sfx_button.draw():
            sfx_on = not sfx_on
            volume = 0.5 if sfx_on else 0
            coin_fx.set_volume(volume)
            jump_fx.set_volume(volume)
            game_over_fx.set_volume(volume)
            sfx_button.image = sfx_on_img if sfx_on else sfx_off_img

        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
        if rules_button.draw():
            show_rules_messagebox()

    elif paused:
        draw_pause_menu()

        if pause_quit_button.draw():
            run = False
        if pause_restart_button.draw():
            world_data = []
            world = reset_level(level)
            player = Player(100, screen_height - 123)
            game_over = 0
            score = 0
            paused = False
        if pause_music_button.draw():
            music_on = not music_on
            if music_on:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            pause_music_button.image = music_on_img if music_on else music_off_img
        if pause_sfx_button.draw():
            sfx_on = not sfx_on
            volume = 0.5 if sfx_on else 0
            coin_fx.set_volume(volume)
            jump_fx.set_volume(volume)
            game_over_fx.set_volume(volume)
            pause_sfx_button.image = sfx_on_img if sfx_on else sfx_off_img

    else:
        # Отрисовка мира и игрока
        world.draw()

        if game_over == 0:
            skeleton_group.update()
            Platfom_group.update()

            # Проверка сбора монет
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        draw_level(level)

        skeleton_group.draw(screen)
        Platfom_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        if game_over == -1:
            if game_over == -1:
                if current_user:
                    update_coins(current_user, score)
                    
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                player = Player(100, screen_height - 123)
                game_over = 0
                score = 0
            if quit_button.draw():
                run = False

        if game_over == 1:
            if current_user:
                update_coins(current_user, score)
                update_last_level(current_user, level)
            level += 1
            if level <= max_level:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("YOU WIN!", font, blue, (screen_width // 2) - 133, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                if quit_button.draw():
                    run = False

    pygame.display.update()

pygame.quit()
