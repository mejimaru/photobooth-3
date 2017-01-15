import piggyphoto, pygame
import time

DEFAULT_RESOLUTION = [640,424]

DEFAULT_FONT_SIZE = 72

COUNTER_FONT_SIZE = 140

MOUSE_LEFT = 1
MOUSE_RIGHT = 3

class PhotoBoothState(object):

    def __init__(self, photobooth, next_state, counter_callback=None, counter_callback_args=None, counter=-1):
        self.photobooth = photobooth
        self.next_state = next_state
        self.inital_counter = counter

        self.counter_callback = counter_callback
        self.counter_callback_args = counter_callback_args
        self.counter_sleep_time = 1
        self.reset()

    def reset(self):
        self.counter = self.inital_counter
        self.counter_last_update_time = time.time()

    def set_counter(self, value):
        self.counter_last_update_time = time.time()
        self.counter = value

    def update_callback(self, photobooth):
        pass

    def update(self):
        self.update_callback()
        self.update_counter()

    def update_counter(self):

        if self.counter > 0:
            now = time.time()
            diff = now - self.counter_last_update_time
            if diff >= self.counter_sleep_time:
                self.counter_last_update_time = now
                self.counter-=1
                if self.is_counter_expired():
                    if self.counter_callback:
                        if(self.counter_callback_args):
                            self.counter_callback(*self.counter_callback_args)
                        else:
                            self.counter_callback()

                return True

        return False

    def is_counter_expired(self):
        return self.counter == 0

    def is_counter_enabled(self):
        return self.counter > -1


class PhotoBooth(object):
    def __init__(self):
        self.cam = None
        self.screen = None
        self._state = None

        self.screen = pygame.display.set_mode(DEFAULT_RESOLUTION)  # , pygame.FULLSCREEN)

        self.screen.fill((128, 128, 128))


    def init_camera(self):
        self.cam = get_camera()
        picture = get_preview(self.cam)
        self.screen = pygame.display.set_mode(picture.get_size())#, pygame.FULLSCREEN) # Uncomment to enable full screen

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self._state.reset()

#helper functions

def get_text_mid_position(resolution):
    return (resolution[0]/2,resolution[1]/2)

def quit_pressed():
    if pygame.event.get(pygame.QUIT):
        return True
    for event in pygame.event.get(pygame.KEYDOWN):
        if event.key == pygame.K_ESCAPE:
            return True
    return False

def mouse_pressed():
    for event in pygame.event.get(pygame.MOUSEBUTTONUP):
        if event.button == MOUSE_LEFT:
            return True
    return False

def show_cam_picture(screen, picture):
    screen.blit(picture, (0, 0))

def get_camera():
    cam = piggyphoto.camera()

    # set capturetarget to memory card
    cam_config = cam.config
    cam_config['main']['settings']['capturetarget'].value = 'Memory card'
    cam.config = cam_config

    #cam.leave_locked()
    return cam

def get_preview(cam):
    cam.capture_preview('preview.jpg')
    picture = pygame.image.load("preview.jpg")
    return picture

def get_text_img(text, size, color):
    font = pygame.font.Font(None, size)

    return font.render(text, True, color)

def show_text(screen, text, pos, size=DEFAULT_FONT_SIZE):
    txt_img = get_text_img(text, size, (255, 255, 255))
    screen.blit(txt_img,
                (pos[0] - txt_img.get_width() // 2, pos[1] - txt_img.get_height() // 2))

def take_photo(app):
    app.cam.capture_image('snap.jpg')
    app.last_photo = pygame.image.load('snap.jpg')
    app.last_photo = pygame.transform.scale(app.last_photo, app.screen.get_size())

#State machine callback functions

class StateWaitingForCamera(PhotoBoothState):
    def __init__(self, photobooth, next_state):
        super(self.__class__, self).__init__(photobooth=photobooth, next_state=next_state)

    def update_callback(self):
        # try initialisation again
        try:
            self.photobooth.init_camera()
            self.photobooth.state = self.next_state
        except Exception, e:
            show_text(self.photobooth.screen, "Camera not connected: "+str(e), get_text_mid_position(DEFAULT_RESOLUTION))
            time.sleep(30)


class StateWaitingForPhotoTrigger(PhotoBoothState):
    def __init__(self, photobooth, next_state):
        super(self.__class__, self).__init__(photobooth=photobooth, next_state=next_state)

    def update_callback(self):
        if mouse_pressed():
            self.photobooth.state = self.next_state
        preview_img = get_preview(self.photobooth.cam)
        show_cam_picture(self.photobooth.screen, preview_img)


class StatePhotoTrigger(PhotoBoothState):
    def __init__(self, photobooth, next_state, counter=-1):
        super(self.__class__, self).__init__(photobooth=photobooth, next_state=next_state, counter=counter, counter_callback=self._take_photo)

    def update_callback(self):

        preview_img = get_preview(self.photobooth.cam)
        show_cam_picture(self.photobooth.screen, preview_img)
        # Show countdown
        show_text(self.photobooth.screen, str(self.counter), get_text_mid_position(DEFAULT_RESOLUTION), 140)

    def _take_photo(self):
        #first update to latest preview
        preview_img = get_preview(self.photobooth.cam)
        show_cam_picture(self.photobooth.screen, preview_img)
        pygame.display.update()
        #take photo
        take_photo(self.photobooth)
        self.photobooth.state = self.next_state


class StateShowPhoto(PhotoBoothState):
    def __init__(self, photobooth, next_state, counter=-1):
        super(self.__class__, self).__init__(photobooth=photobooth, next_state=next_state, counter=counter, counter_callback=self._switch_to_next_state)

    def update_callback(self):
        show_cam_picture(self.photobooth.screen, app.last_photo)
        show_text(self.photobooth.screen, "Last Photo:", (70, 30), 36)

    def _switch_to_next_state(self):
        self.photobooth.state = self.next_state


if __name__ == '__main__':
    pygame.init()

    pygame.event.set_allowed(None)
    pygame.event.set_allowed(pygame.MOUSEBUTTONUP)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(pygame.QUIT)

    app = PhotoBooth()

    # Create all states
    state_show_photo = StateShowPhoto(photobooth=app, next_state=None, counter=5)

    state_trigger_photo = StatePhotoTrigger(photobooth=app, next_state=state_show_photo, counter=5)

    state_waiting_for_photo_trigger = StateWaitingForPhotoTrigger(photobooth=app, next_state=state_trigger_photo)

    state_show_photo.next_state = state_waiting_for_photo_trigger

    state_waiting_for_camera = StateWaitingForCamera(photobooth=app, next_state=state_waiting_for_photo_trigger)

    app.state = state_waiting_for_camera


    while not quit_pressed():
        pygame.display.update()
        try:

            app.state.update()

            pygame.event.pump()
            #pygame.event.clear()

        except Exception, e:
            print(e)
            show_text(app.screen, "Error", get_text_mid_position(DEFAULT_RESOLUTION))


    if app.cam:
        app.cam.exit()
