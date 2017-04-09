#!/usr/bin/python

from abc import ABCMeta, abstractmethod

from pygame_utils import *

import imp


class ButtonState(object):
    BUTTON_PRESSED = 0
    BUTTON_NOT_PRESSED = 1


class LedState(object):
    OFF = 0
    ON = 1


class AbstractUserIo(object):
    """
    Abstract interface for all additional hardware user interfaces buttons, leds ...
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def any_button_pressed(self):
        raise NotImplementedError

    @abstractmethod
    def set_all_led(self, led_state):
        raise NotImplementedError

    @abstractmethod
    def show_led_coutdown(self, counter):
        raise NotImplementedError


class UserIoFactory(object):
    """
    Factory for the registration and creation of AbstractUserIo
    """
    algorithms = {}

    @classmethod
    def register_algorithm(cls, id_class, class_obj):
        """
        Register an algorithm in the factory under the given ID
        Algorithm has to be a subclass of AbstractUserIo
        :param id_class: ID for the algorithm
        :type id_class: str
        :param class_obj: the algorithm class
        :type class_obj: AbstractUserIo
        :return:
        """
        if not issubclass(class_obj, AbstractUserIo):
            assert ("Algo is not subclass of AbstractActivationAlgorithm")
        if cls.algorithms.has_key(id_class):
            assert ("Algorithm ID already in use")
        else:
            cls.algorithms[id_class] = class_obj

    @classmethod
    def create_algorithm(cls, id_class, **kwargs):
        """
        Initialize the algorithm with the given ID
        :param id_class: the id of the impl that should be created
        :type id_class str
        :return: a specific instance of AbstractUserIo
        """
        if not cls.algorithms.has_key(id_class):
            raise LookupError("Cannot find class_id: " + id_class)
        else:
            return cls.algorithms[id_class](**kwargs)


class PyGameUserIo(AbstractUserIo):
    def __init__(self, photobooth, **kwargs):
        self._photobooth = photobooth
        pass

    def any_button_pressed(self):
        keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
        return self._photobooth.event_manager.key_pressed(keys)

    def set_all_led(self, led_state):
        print('set all led:', led_state)
        pass

    def show_led_coutdown(self, counter):
        print('led countdown:', counter)
        pass


UserIoFactory.register_algorithm(id_class='pygame', class_obj=PyGameUserIo)

try:
    imp.find_module('RPi')
    found_rpi_module = True
except ImportError:
    found_rpi_module = False
    print("Couldn't find RPi module, proceeding without")

if found_rpi_module:

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)


    class RaspiPushButton(object):

        def __init__(self, color, button_pin, led_pin):
            self.color = color
            self.button_pin = button_pin
            self.led_pin = led_pin

            self.led_state = LedState.OFF
            self.reset_button_state()

            GPIO.setup(self.button_pin, GPIO.IN)

            GPIO.setup(self.led_pin, GPIO.OUT)

            GPIO.output(self.led_pin, GPIO.LOW)

            GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self._press_callback, bouncetime=300)
            
        def __del__(self):
            GPIO.cleanup(self.button_pin)
            GPIO.cleanup(self.led_pin)

        def _press_callback(self, channel):

            self.button_event_state = ButtonState.BUTTON_PRESSED
            print('_press_callback', self.color)

        def is_pressed(self):
            return GPIO.input(self.button_pin) == GPIO.LOW

        def was_pressed(self):
            result = self.button_event_state == ButtonState.BUTTON_PRESSED
            self.reset_button_state()
            return result

        def reset_button_state(self):
            self.button_event_state = ButtonState.BUTTON_NOT_PRESSED

        def led_on(self):
            self.set_led(LedState.ON)

        def led_off(self):
            self.set_led(LedState.OFF)

        def set_led(self, state):
            self.led_state = state
            if self.led_state == LedState.OFF:
                GPIO.output(self.led_pin, GPIO.LOW)
            elif self.led_state == LedState.ON:
                GPIO.output(self.led_pin, GPIO.HIGH)


    class ButtonRail(AbstractUserIo):

        # Adjust configuration if necessary
        push_buttons = [RaspiPushButton(color='green', button_pin=23, led_pin=18),
                        RaspiPushButton(color='blue', button_pin=25, led_pin=24),
                        RaspiPushButton(color='yellow', button_pin=16, led_pin=12),
                        RaspiPushButton(color='red', button_pin=21, led_pin=20)]

        def __init__(self, **kwargs):
            pass

        def any_button_pressed(self):
            """
            Check if any button was pressed
            :return: true if a button was pressed since last call
            """

            result = False
            for button in ButtonRail.push_buttons:
                if button.was_pressed():
                    result = True
                    # do not break in order to reset all buttons
                    # reset is done inside was_pressed()

            return result

        def set_all_led(self, led_state):

            for button in ButtonRail.push_buttons:
                button.set_led(led_state)

        def show_led_coutdown(self, counter):

            if counter == 4:
                ButtonRail.push_buttons[0].led_off()
            if counter == 3:
                ButtonRail.push_buttons[1].led_off()
            if counter == 2:
                ButtonRail.push_buttons[2].led_off()
            if counter == 1:
                ButtonRail.push_buttons[3].led_off()
            if counter == 0:
                self.set_all_led(LedState.ON)

        def test_routine(self):
            """
            This is a very simple test routine that lights the button that is pressed
            """

            while True:  # TODO replace endless loop

                for button in ButtonRail.push_buttons:
                    if button.is_pressed():
                        print("pressed: ", button.color)
                        button.led_on()
                    else:
                        button.led_off()

        def __del__(self):
            GPIO.cleanup()


    UserIoFactory.register_algorithm(id_class='raspi', class_obj=ButtonRail)

    if __name__ == '__main__':
        button_rail = ButtonRail()
        button_rail.test_routine()