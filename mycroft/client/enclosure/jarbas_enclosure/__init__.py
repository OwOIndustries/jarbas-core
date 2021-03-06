from mycroft.client.enclosure import Enclosure
import cv2, imutils
import random
import time
from os.path import dirname, join, exists

__author__ = "jarbas"


class JarbasEnclosure(Enclosure):
    def __init__(self, ws=None, name="Jarbas"):
        super(JarbasEnclosure, self).__init__(ws, name)
        self.fullscreen = False
        self.width = 700
        self.height = 800
        self.default_spf = 200 #miliseconds per frame
        self.frames_dir = join(dirname(__file__), "frames")
        # load default frames
        self.blank_frame = self.load(join(self.frames_dir, "blank.png"))
        self.alarm = self.load(join(self.frames_dir, "alarm.png"))
        self.dead = self.load(join(self.frames_dir, "dead.png"))
        self.down = self.load(join(self.frames_dir, "down.png"))
        self.down_left = self.load(join(self.frames_dir, "down_left.png"))
        self.down_right = self.load(join(self.frames_dir, "down_right.png"))
        self.closed_eyes = self.load(join(self.frames_dir, "eyes_closed"))
        self.face = self.load(join(self.frames_dir, "face.png"))
        self.left = self.load(join(self.frames_dir, "left.png"))
        self.middle_blink = self.load(join(self.frames_dir,
                                          "middle_blink.png"))
        self.mouth1= self.load(join(self.frames_dir, "mouth1.png"))
        self.mouth2 = self.load(join(self.frames_dir, "mouth2.png"))
        self.mouth3 = self.load(join(self.frames_dir, "mouth3.png"))
        self.mouth4 = self.load(join(self.frames_dir, "mouth4.png"))
        self.right = self.load(join(self.frames_dir, "right.png"))
        self.up = self.load(join(self.frames_dir, "up.png"))
        self.up_left = self.load(join(self.frames_dir, "up_left.png"))
        self.up_right = self.load(join(self.frames_dir, "up_right.png"))
        self.eyes_crossed = self.load(join(self.frames_dir,
                                           "crossed_eyes.png"))

        self.current_frame = self.blank_frame.copy()
        self.detect_coordinates(self.current_frame)
        self.current_frame = self.draw_custom(self.face.copy())
        self.frames = []

    # animations
    def mouth_shift(self):
        timestep = self.default_spf/3
        animation = [self.face, self.mouth1, self.mouth2,
                     self.mouth3, self.mouth4]
        self.frames.append((timestep, random.choice(animation)))

    def wake_up(self):
        timestep = self.default_spf
        animation = [self.dead, self.closed_eyes, self.middle_blink,
                     self.face]
        self.current_frame = self.draw_custom(self.face)
        for frame in animation:
            self.frames.append((timestep, frame))

    def go_to_sleep(self):
        timestep = self.default_spf
        animation = [self.face, self.middle_blink, self.closed_eyes,
                     self.dead]
        self.current_frame = self.draw_custom(self.dead)
        for frame in animation:
            self.frames.append((timestep, frame))

    def look_left_down(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.down_left)
        self.frames.append((timestep, self.down_left))

    def look_right_down(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.down_right)
        self.frames.append((timestep, self.down_right))

    def look_left_up(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.up_left)
        self.frames.append((timestep, self.up_left))

    def look_right_up(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.up_right)
        self.frames.append((timestep, self.up_right))

    def look_up(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.up)
        self.frames.append((timestep, self.up))

    def look_down(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.down)
        self.frames.append((timestep, self.down))

    def look_left(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.left)
        self.frames.append((timestep, self.left))

    def look_right(self):
        timestep = self.default_spf
        self.current_frame = self.draw_custom(self.right)
        self.frames.append((timestep, self.right))

    def blink(self):
        timestep = self.default_spf
        animation = [self.face, self.middle_blink, self.closed_eyes,
                     self.middle_blink, self.face]
        for frame in animation:
            self.frames.append((timestep, frame))

    def cross_eyes(self):
        timestep = self.default_spf
        animation = [self.face, self.eyes_crossed, self.face]
        for frame in animation:
            self.frames.append((timestep, frame))

    def roll_eyes(self):
        timestep = self.default_spf
        animation = [self.up_right, self.right, self.down_right, self.down,
                     self.down_left, self.left, self.up_left, self.up]
        for frame in animation:
            self.frames.append((timestep, frame))

    def alarm(self):
        timestep = self.default_spf * 2
        animation = [self.face, self.alarm]
        for frame in animation:
            self.frames.append((timestep, frame))

    # drawing
    def draw_custom(self, pic):
        # get base pic
        base = self.blank_frame.copy()
        # get draw area
        x, y, w, h = self.draw_area
        # blit pictures
        base[y:y + h, x:x + w] = pic[y:y + h, x:x + w]
        return base

    def run(self):
        while True:
            if len(self.frames):
                # finish showing queued frames
                time, pic = self.frames[0]
                pic = self.draw_custom(pic)
                self.show(pic, time)
                self.frames.pop(0)
            else:
                # show current default frame
                self.show(self.current_frame)

    def detect_coordinates(self, pic):
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 5, 255,
                               cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh, 1,
                                cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if imutils.is_cv2() else cnts[1]
        areas = {}

        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            if len(approx) == 4:
                a=cv2.contourArea(cnt)
                (x, y, w, h) = cv2.boundingRect(approx)
                areas[a] = (x+x*10/100, y+y*10/100, w-x*20/100, h-y*20/100)
            self.draw_area = areas[sorted(areas)[-1]]
        # TODO mouth area
        # TODO eyes area

    def load(self, path):
        if not exists(path):
            return None
        pic = cv2.imread(path, -1)
        return imutils.resize(pic, self.width, self.height)

    def show(self, pic, time=1.0):
        if time < 1:
            time = 1
        pic = imutils.resize(pic, self.width, self.height)
        cv2.imshow("jarbas", pic)
        cv2.waitKey(int(time))

    # listeners
    def record_begin(self, message):
        ''' listening started '''
        pass

    def record_end(self, message):
        ''' listening ended '''
        pass

    def talk_start(self, message):
        ''' speaking started '''
        self.speaking = True
        while self.speaking:
            self.mouth_shift()
            time.sleep(self.default_spf)

    def talk_stop(self, message):
        ''' speaking ended '''
        self.speaking = False

    def handle_speak(self, message):
        pass

    def handle_sleep(self, message):
        ''' go to sleep animation '''
        self.go_to_sleep()

    def handle_awake(self, message):
        ''' wake up animation '''
        self.wake_up()

    def reset(self, message):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        pass

    def system_reset(self, message):
        """The enclosure hardware should reset any CPUs, etc."""
        pass

    def system_mute(self, message):
        """Mute (turn off) the system speaker."""
        pass

    def system_unmute(self, message):
        """Unmute (turn on) the system speaker."""
        pass

    def system_blink(self, message):
        """The 'eyes' should blink the given number of times.
        Args:
            times (int): number of times to blink
        """
        times = message.data.get("times")
        for i in range(0, times):
            self.blink()

    def eyes_on(self, message):
        """Illuminate or show the eyes."""
        self.current_frame = self.draw_custom(self.face)

    def eyes_off(self, message):
        """Turn off or hide the eyes."""
        self.current_frame = self.draw_custom(self.closed_eyes)

    def eyes_blink(self, message):
        """Make the eyes blink
        Args:
            side (str): 'r', 'l', or 'b' for 'right', 'left' or 'both'
        """
        side = message.data.get("side")
        if side == "b":
            self.blink()
        else:
            self.blink()
        # TODO all cases

    def eyes_narrow(self, message):
        """Make the eyes look narrow, like a squint"""
        self.current_frame = self.draw_custom(self.middle_blink)

    def eyes_look(self, message):
        """Make the eyes look to the given side
        Args:
            side (str): 'r' for right
                        'l' for left
                        'u' for up
                        'd' for down
                        'c' for crossed
                        'ul' for up-left
                        'dl' for down-left
                        'ur' for up-right
                        'dr' for down-right
        """
        side = message.data.get("side")
        if side == "r":
            self.look_right()
        elif side == "l":
            self.look_left()
        elif side == "u":
            self.look_up()
        elif side == "d":
            self.look_down()
        elif side == "c":
            self.cross_eyes()
        elif side == "ul":
            self.look_left_up()
        elif side == "dl":
            self.look_left_down()
        elif side == "ur":
            self.look_right_up()
        elif side == "dr":
            self.look_right_down()

    def eyes_color(self, message):
        """Change the eye color to the given RGB color
        Args:
            r (int): 0-255, red value
            g (int): 0-255, green value
            b (int): 0-255, blue value
        """
        # TODO use opencv2 to edit frames
        r = message.data.get("r")
        if r > 255/2:
            self.current_frame = self.draw_custom(self.alarm)
        g = message.data.get("g")
        b = message.data.get("b")
        if b > 255/2:
            self.current_frame = self.draw_custom(self.face)

    def eyes_brightness(self, message):
        """Set the brightness of the eyes in the display.
        Args:
            level (int): 1-30, bigger numbers being brighter
        """
        level = message.data.get("brightness", 30)
        # TODO opencv edit

    def eyes_reset(self, message):
        """Restore the eyes to their default (ready) state."""
        self.current_frame = self.draw_custom(self.face)

    def eyes_timed_spin(self, message):
        """Make the eyes 'roll' for the given time.
        Args:
            length (int): duration in milliseconds of roll, None = forever
        """
        length = message.data.get("length")
        seconds = length / 1000
        start = time.time()
        while time.time() - start < seconds:
            self.roll_eyes()
            time.sleep(0.3*8) #roll animation time

    def eyes_volume(self, message):
        """Indicate the volume using the eyes
        Args:
            volume (int): 0 to 11
        """
        # TODO draw in face
        volume = message.data.get("volume")

    def mouth_reset(self, message):
        """Restore the mouth display to normal (blank)"""
        self.current_frame = self.draw_custom(self.face)

    def mouth_talk(self, message):
        """Show a generic 'talking' animation for non-synched speech"""
        self.mouth_shift()

    def mouth_think(self, message):
        """Show a 'thinking' image or animation"""
        self.roll_eyes()

    def mouth_listen(self, message):
        """Show a 'listening' image or animation"""
        pass

    def mouth_smile(self, message):
        """Show a 'smile' image or animation"""
        pass

    def mouth_viseme(self, message):
        """Display a viseme mouth shape for synched speech
        Args:
            code (int):  0 = shape for sounds like 'y' or 'aa'
                         1 = shape for sounds like 'aw'
                         2 = shape for sounds like 'uh' or 'r'
                         3 = shape for sounds like 'th' or 'sh'
                         4 = neutral shape for no sound
                         5 = shape for sounds like 'f' or 'v'
                         6 = shape for sounds like 'oy' or 'ao'
        """
        code = message.data.get("code")

    def mouth_text(self, message):
        """Display text (scrolling as needed)
        Args:
            text (str): text string to display
        """
        text = message.data.get("text")

    def mouth_display(self, message):
        """Display images on faceplate. Currently supports images up to 16x8,
           or half the face. You can use the 'x' parameter to cover the other
           half of the faceplate.
        Args:
            img_code (str): text string that encodes a black and white image
            x (int): x offset for image
            y (int): y offset for image
            refresh (bool): specify whether to clear the faceplate before
                            displaying the new image or not.
                            Useful if you'd like to display muliple images
                            on the faceplate at once.
        """
        img_code = message.data.get("img_code", "")
        x = message.data.get("x", 0)
        y = message.data.get("y", 0)
        refresh = message.data.get("refresh", True)

    def weather_display(self, message):
        """Show a the temperature and a weather icon

        Args:
            img_code (char): one of the following icon codes
                         0 = sunny
                         1 = partly cloudy
                         2 = cloudy
                         3 = light rain
                         4 = raining
                         5 = stormy
                         6 = snowing
                         7 = wind/mist
            temp (int): the temperature (either C or F, not indicated)
        """
        img_code = message.data.get("img_code")
        temp = message.data.get("temp")

    def activate_mouth_events(self, message):
        """Enable movement of the mouth with speech"""
        pass

    def deactivate_mouth_events(self, message):
        """Disable movement of the mouth with speech"""
        pass
