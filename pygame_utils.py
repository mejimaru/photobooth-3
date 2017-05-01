import pygame

DEFAULT_FONT_SIZE = 72

COLOR_GREEN = (34,139,34)
COLOR_RED = (200,0,0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (220,220,220)
COLOR_YELLOW = (240,230,140)
COLOR_BLUE =(0,0,255)
COLOR_ORANGE = (210,105,30)
COLOR_DARK_GREY = (105, 105, 105)

class PyGameEventManager(object):
    """
    Classes caches and simplifies pygame event management
    """

    MOUSE_LEFT = 1
    MOUSE_RIGHT = 3

    def __init__(self):
        self.events = []
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(pygame.MOUSEBUTTONUP)
        pygame.event.set_allowed(pygame.KEYDOWN)
        pygame.event.set_allowed(pygame.QUIT)

    def update_events(self):
        """
        Update method has to be called every cycle in python main loop
        """
        self.events = pygame.event.get()
        pygame.event.pump()

    def key_pressed(self, keys):
        """
        check if a key from the given key list is pressed
        :param keys:
        :return: True if one is pressed
        """
        for event in self.events:
            if event.type == pygame.KEYDOWN and event.key in keys:
                return True
        return False

    def mouse_pressed(self, mouse_key=MOUSE_LEFT):
        """
        Check if a mousekey was pressed
        :param mouse_key: define the mouse key
        :return: True if pressed
        """
        for event in self.events:
            #print(event)
            if event.type == pygame.MOUSEBUTTONUP and event.button == mouse_key:
                return True
        return False

    def quit_pressed(self):
        """
        Check if application termination was requested
        :return True if quit was pressed/requested
        """
        for event in self.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE \
                or event.type == pygame.QUIT:
                return True

def get_text_mid_position(resolution):
    return (resolution[0]/2,resolution[1]/2)

def show_cam_picture(screen, picture, fullscreen = True):
    if fullscreen:
        img = pygame.transform.scale(picture, screen.get_size())
    else:
        img = picture
    screen.blit(img, (0, 0))

def get_text_img(text, size, color):
    font = pygame.font.Font(None, size)

    return font.render(text, True, color)

def draw_rect(screen, pos, size, color=COLOR_GREY, color_border=None, size_border = 1):
    pygame.draw.rect(screen, color, (pos[0],pos[1],size[0],size[1]))
    if color_border:
        pygame.draw.rect(screen, color_border, (pos[0], pos[1], size[0], size[1]),size_border)

def draw_circle(screen, pos, size, color, color_border=None, size_border = 1):
    pygame.draw.circle(screen, color, pos, size)
    if color_border:
        pygame.draw.circle(screen, color_border, pos, size, size_border)

def draw_text_box(screen, text, pos, size=DEFAULT_FONT_SIZE, text_color=COLOR_DARK_GREY, box_color=COLOR_GREY, border_color=COLOR_WHITE, margin=10):

    txt_img = get_text_img(text, size, text_color)

    rect_size = (txt_img.get_width() + margin*2, txt_img.get_height() + margin*2)

    #vertical center alignment
    if not pos[0]:
        pos_x = get_text_mid_position(screen.get_size())[0] - rect_size[0]//2
    else:
        pos_x = pos[0]

    # horizontal center alignment
    if not pos[1]:
        pos_y = get_text_mid_position(screen.get_size())[1] - rect_size[1] // 2
    else:
        pos_y = pos[1]

    rect_pos = (pos_x - margin, pos_y - margin)

    draw_rect(screen=screen, pos=rect_pos, size=rect_size, color=box_color, color_border=border_color)

    screen.blit(txt_img,(pos_x,pos_y))

def show_text_mid(screen, text, mid_pos, size=DEFAULT_FONT_SIZE, color=COLOR_WHITE):
    """
    Show text using mid position for entire text
    :param screen:
    :param text:
    :param mid_pos:
    :param size:
    :return:
    """
    txt_img = get_text_img(text, size, color)
    screen.blit(txt_img,
                (mid_pos[0] - txt_img.get_width() // 2, mid_pos[1] - txt_img.get_height() // 2))

def show_text_left(screen, text, pos, size=DEFAULT_FONT_SIZE,  color=COLOR_WHITE):
    """
    Show text with left pos reference position
    :param screen:
    :param text:
    :param pos:
    :param size:
    :return:
    """
    txt_img = get_text_img(text, size, color)
    screen.blit(txt_img,pos)


def draw_button_bar(screen, text=["","","",""], pos=(145,380), size=40, font_size=32, margin=30):
    pos_x = pos[0]
    pos_y = pos[1]

    if text[0]:
        draw_circle(screen=screen,pos=(pos_x,pos_y), size=size, color=COLOR_RED, color_border=COLOR_WHITE, size_border=1)
        show_text_mid(screen=screen,text=text[0],mid_pos=(pos_x,pos_y),size=font_size,color=COLOR_WHITE)
    pos_x+=margin+size*2
    if text[1]:
        draw_circle(screen=screen, pos=(pos_x, pos_y), size=size, color=COLOR_BLUE, color_border=COLOR_WHITE, size_border=1)
        show_text_mid(screen=screen, text=text[1], mid_pos=(pos_x, pos_y), size=font_size, color=COLOR_WHITE)
    pos_x += margin + size*2
    if text[2]:
        draw_circle(screen=screen, pos=(pos_x, pos_y), size=size, color=COLOR_YELLOW, color_border=COLOR_WHITE, size_border=1)
        show_text_mid(screen=screen, text=text[2], mid_pos=(pos_x, pos_y), size=font_size, color=COLOR_WHITE)
    pos_x += margin + size*2
    if text[3]:
        draw_circle(screen=screen, pos=(pos_x, pos_y), size=size, color=COLOR_GREEN, color_border=COLOR_WHITE, size_border=1)
        show_text_mid(screen=screen, text=text[3], mid_pos=(pos_x, pos_y), size=font_size, color=COLOR_WHITE)