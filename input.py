import pygame

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

"""Главное меню игры"""
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    input_box = pygame.Rect(525, 250, 140, 36)
    color_inactive = pygame.Color("yellow")
    color_active = pygame.Color("red")
    color = color_inactive
    active = False
    text = ''
    run = True
    
    while run:
        #WIN.blit(BG, (0,0))
        title_label = title_font.render("Введите имя: ", 1,(255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
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
                        print(text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                #main()
                
        WIN.fill((30, 30, 30))
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
    pygame.quit()


if __name__ == '__main__':
    pygame.init()
    main_menu()
    pygame.quit()