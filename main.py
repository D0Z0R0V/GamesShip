import pygame, sys, pyglet
import os, time, random
pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

#Загрузка изображений
RED_SPACE_SHIP = pygame.image.load(os.path.join("Image", "ino_red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("Image", "ino.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("Image", "ino_yellow.png"))
HEALTH = pygame.image.load(os.path.join("Image", "health.png"))

#Корабль игрока
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("Image", "gun.png"))

#Лазеры
RED_LASER = pygame.image.load(os.path.join("Image", "laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("Image", "laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("Image", "laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("Image", "laser_yellow.png"))

#background
BG = pygame.transform.scale(pygame.image.load(os.path.join("Image", "Fong.jpg")), (WIDTH, HEIGHT))
  
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img 
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel
        
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30
    #это важная штука для инициализации    
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.health_img = None
        self.lasers = []
        self.healths = []
        self.cool_down_counter = 0
        
    def draw(self,window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
            
    #корявая отрисовка аптечки
    def draws(self,window):
        window.blit(self.health_img, (self.x, self.y))
        for healt in self.healths:
            healt.draws(window)
            
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in  self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
        
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def get_heights(self):
        return self.health_img.get_height()
        
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)#маска помогает нам считывать положения пикселя. Поможет в будущем, чтоб описывать столкновения
        self.max_health = health
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+21, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def move_lasers(self, vel, objs, sc, stats):
        self.cooldown()
        for laser in  self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        stats.score += 10 #эта строка увеличивает счет на 10 очков за каждого уничтоженного врага
                        check_max_score(stats, sc)
                        sc.image_score() #эта строка обновляет изображение партитуры
                        sc.show_score()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        
    def draw(self,window):
           super().draw(window)
           self.healthbar(window)
           
    def init(self, x, y, health=100):
        super().__init__(x, y, health)
                        
    """Создание полосы здоровья"""                   
    def healthbar(self,window):
        pygame.draw.rect(window, (255,255,255), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))
        
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP,RED_LASER),
        
        "green" : (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue" : (BLUE_SPACE_SHIP, BLUE_LASER)
    }
    
    def __init__(self, x, y, color, health=100): #"red", "green", "blue"
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]#получение нужного цвета, для определенного корабля
        self.mask = pygame.mask.from_surface(self.ship_img)#служит для связи маски с объектом
        
    #перемещение врага вниз
    def move(self,vel):
        self.y += vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+16, self.y+3, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1   
            
class Health(Ship):
    COLOR = {
        "health":(HEALTH)
    }
    
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)       
        self.health_img = HEALTH
        self.mask = pygame.mask.from_surface(self.health_img)#служит для связи маски с объектом
        
    def moves(self, vel):
        self.y += vel 

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)
   
class Stats():
    def __init__(self):
        self.reset_stats()
        #этот блок кода считывает наивысший балл из файла и присваивает его атрибуту max_score
        try:
            with open('maxscore.txt', 'r') as n:
                self.max_score = int(n.read())
        except FileNotFoundError:
            self.max_score = 0
    
    def reset_stats(self):
        self.score = 0
           
class Scores(Ship):
    """Вывод очков игры"""
    def __init__(self,screen,stats):
        #Инициализацияя подсчета очков
        self.screen = WIN
        self.screen_rect = WIN.get_rect()
        self.stats = stats
        self.text_color = (255,255,255)
        self.font = pygame.font.SysFont(None, 36)
        self.image_score()
        self.image_max_score() #эта строка создает изображение с максимальной оценкой
        
    def image_score(self):
        """Преобразовывает текст в изобржаение"""
        self.score_img = self.font.render(str(self.stats.score), True, self.text_color, (0,0,0))
        self.score_rect = self.score_img.get_rect()
        self.score_rect.center = self.screen_rect.center
        self.score_rect.top = 20
        
    def image_max_score(self):
        #Преобразовывает текст в изобржаение
        self.max_score_img = self.font.render(str(self.stats.max_score), True, self.text_color, (0,0,0))
        self.max_score_rect = self.max_score_img.get_rect()
        self.max_score_rect.center = self.screen_rect.center
        self.max_score_rect.top = 50
        
    def show_score(self):
        #Вывод счета на экран
        self.screen.blit(self.score_img, self.score_rect)
        self.screen.blit(self.max_score_img,self.max_score_rect)#эта строка показывает максимальный балл на экране
                
def collide(obj1, obj2):     
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    max_stats = 0
    main_font = pygame.font.SysFont("comicsans", 50) #Задаем определенный шрифт и его размер
    lost_font = pygame.font.SysFont("comicsans", 60)
    
    enemies = []
    health_max = [] #увеличение жизней для игрока
    wave_lenght = 5
    health_lenght = 1
    enemy_vel = 1
    health_vel = 1
    
    player_vel = 5
    laser_vel = 5
    global player_name
    
    player = Player(300, 630)
    stats = Stats()
    sc = Scores(WIN, stats)
    
    clock = pygame.time.Clock()
    
    lost = False
    lost_count = 0
    
    def redraw_window():#Окно прорисовки
        WIN.blit(BG, (0,0))
        #Рисуем текст
        sc.show_score() 
        lives_label = main_font.render(f'Lives: {lives}', 1, (255,255,255))
        level_label = main_font.render(f'Level: {level}', 1, (255,255,255))
        
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        for healt in health_max:
            healt.draws(WIN)
            
        if lost:
            lost_label = lost_font.render("ERROR 404", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))   
        
        player.draw(WIN)
        pygame.display.update()
    
    while run:
        clock.tick(FPS)  
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3:
                run = False
                # Получаем счет игрока
                player_score = stats.score
                # Открываем файл players.txt в режиме дозаписи
                with open('players.txt', 'a') as f:
                    # Записываем имя и счет игрока в файл с пробелом в начале строки
                    f.write(player_name + ':' + str(player_score) + '\n')
            else:
                continue
                
        #создает нам инопланетян для отображения на экране
        if len(enemies) == 0:
            level += 1
            wave_lenght += 6
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(['red', 'green', 'blue']))
                enemies.append(enemy)
        
        #должна управлять аптечками    
        if len(health_max) == 0:
            health_lenght == 1
            for i in range(health_lenght):
                healt = Health(random.randrange(50, WIDTH - 100), random.randrange(-1000, -100), random.choice(['health']))
                health_max.append(healt)
                if level > 1 and level <= 3 and len(health_max) <= 1:
                    health_max.remove(healt)
                elif level > 4 and len(health_max) > 2:
                    health_max.remove(healt)
                    
           
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Получаем счет игрока
                player_score = stats.score
                # Открываем файл players.txt в режиме дозаписи
                with open('players.txt', 'a') as f:
                    # Записываем имя и счет игрока в файл
                    f.write(player_name + ':' + str(player_score) + '\n')
                # Закрываем игру
                #pygame.quit()
                #sys.exit()
                run = False
                
                
        keys = pygame.key.get_pressed()
        #сообщает нам какие клавиши нажаты в настоящее время
        if keys[pygame.K_a] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 13 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        #обработка событий для столкновений и стрельбы инопланетян
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if level > 1 and level <= 4:
                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()
            elif level > 5:
                if random.randrange(0, 1*60) == 1:
                    enemy.shoot()
                    
            if collide(enemy, player):
                player.health -= 5
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            
        player.move_lasers(-laser_vel, enemies, sc, stats)
        
        #жизни
        for healt in health_max[:]:
            healt.moves(health_vel)
                    
            if collide(healt, player):
                if player.health <= 100:
                    player.health = 100
                    health_max.remove(healt)
                    stats.score += 15
                    check_max_score(stats, sc) 
                    sc.image_score() 
                    sc.show_score()
                else:
                    health_max.remove(healt)

            elif healt.y + healt.get_heights() > HEIGHT:
                health_max.remove(healt)
                
#Сохранение информации в файл и сопостовление имени с очками 
def check_max_score(stats, sc):
    """Проверка на новый рекорд"""
    if stats.score > stats.max_score:
        stats.max_score = stats.score
        #sc.image_max_score() #эта строка обновляет изображение максимального балла
        with open('maxscore.txt', 'w') as n:
            n.write(str(stats.max_score))
              
"""Главное меню игры"""
def get_font(size): # Возвращает Press-Start-2P в нужном размере
    return pygame.font.Font("./Font/font.ttf", size)

#Окно для ввода ника пользователя
def play():
    title_font = get_font(27)
    input_box = pygame.Rect(525, 250, 140, 36)
    color_inactive = pygame.Color("yellow")
    color_active = pygame.Color("red")
    color = color_inactive
    active = False
    text = '' 
    stats = Stats()
    global player_name
    # Переменная состояния кнопки
    button_active = False
    
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        CONTINUE = pygame.mouse.get_pos()

        #WIN.fill("black")
        title_label = title_font.render("Введите имя: ", 1,(255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))        

        PLAY_BACK = Button(image=None, pos=(300, 560), 
                            text_input="BACK", font=get_font(50), base_color="White", hovering_color="Green")
        CONTINUE_PLAY = Button(image=None, pos=(940, 560), 
                            text_input="CONTINUE", font=get_font(50), base_color="White", hovering_color="Yellow")


        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(WIN)
        CONTINUE_PLAY.changeColor(CONTINUE)
        CONTINUE_PLAY.update(WIN)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Получаем счет игрока
                player_score = stats.score
                # Открываем файл players.txt в режиме дозаписи
                with open('players.txt', 'r') as f:
                    # Записываем имя и счет игрока в файл
                    f.write(player_name + ':' + str(player_score))
                # Закрываем игру
                pygame.quit()
                main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if len(text) >=1:
                    button_active = True
                    if CONTINUE_PLAY.checkForInput(CONTINUE):
                        text = ''
                        main() 
                else:
                    button_active = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Если пользователь нажал на прямоугольник input_box
                if input_box.collidepoint(event.pos):
                    #Переключение активной переменной
                    active = not active
                else:
                    active = False
                #Измените текущий цвет поля ввода
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        text = ''
                        main()
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                #main()
            # Записываем имя игрока в переменную
            player_name = text

                
        WIN.fill("black")
        # Отобразить текущий текст.
        txt_surface = title_font.render(text, True, color)
        # Измените размер поля, если текст слишком длинный.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Выделите текст.
        WIN.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Выделите прямоугольник input_box.
        pygame.draw.rect(WIN, color, input_box, 2)

    pygame.display.update()

#Отдельное окно для показа лидеров игры
def leader():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        WIN.fill("white")

        """Дописать сюда сортировку пользователей по очкам в игре и имени, которое они ввели"""
        # Проверяем, есть ли файл players.txt в папке
        if os.path.exists('players.txt'):
            # Если есть, то открываем его в режиме чтения
            with open('players.txt', 'r') as f:
                # Читаем содержимое файла в список
                players_list = f.readlines()
            # Сортируем список по убыванию очков игроков
            players_list = sorted(players_list, key=lambda x: int(x.split(':')[1]), reverse=True)
            # Выводим на экран первые 10 элементов списка
            for i in range(3):
                # Проверяем, что индекс i не выходит за границы списка
                if i < len(players_list):
                    # Получаем имя и счет игрока из строки
                    player_name, player_score = players_list[i].replace('\n','').split(':')
                    # Создаем текстовое изображение с именем и счетом игрока
                    player_text = get_font(45).render(player_name + ' - ' + player_score, True, "Black")
                    # Получаем прямоугольник текстового изображения
                    player_rect = player_text.get_rect(center=(640, 260 + i * 50))
                    # Выводим текстовое изображение на экран
                    WIN.blit(player_text, player_rect)
        else:
            # Если файла нет, то выводим сообщение об ошибке
            error_text = get_font(45).render("Файл players.txt не найден", True, "Black")
            error_rect = error_text.get_rect(center=(640, 260))
            WIN.blit(error_text, error_rect)
            
        #OPTIONS_TEXT = get_font(45).render("Тут должны быть лидеры", True, "Black")
        #OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        #WIN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 660), 
                            text_input="BACK", font=get_font(55), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

#Создание основго экрана меню
def main_menu():
    BG = pygame.image.load(os.path.join("Image", "Background.jpg"))
    while True:
        WIN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(90).render("Space Shooter", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load(os.path.join("Image", "Play Rect.png")), pos=(640, 250), 
                            text_input="PLAY", font=get_font(75), base_color="#fcca03", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load(os.path.join("Image", "Options Rect.png")), pos=(640, 400), 
                            text_input="LEADERS", font=get_font(75), base_color="#fcca03", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load(os.path.join("Image", "Quit Rect.png")), pos=(640, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#fcca03", hovering_color="Red")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    leader()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()          
    
if __name__ == '__main__':
    pygame.init()
    main_menu()
    pygame.quit()