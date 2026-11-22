
import socket
import threading
import time
import random
import ipaddress

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window

# Android PyJNIus support
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    WindowManager = autoclass('android.view.WindowManager')
    FLAG_KEEP_SCREEN_ON = WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False
    activity = None
    FLAG_KEEP_SCREEN_ON = 0


MAX_DURATION = 30
CHECK_INTERVAL = 1.0


def validate_target_ip(value):
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError:
        raise ValueError("Enter a valid IP address.")

    if not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
    ):
        raise ValueError("Only private/local IP addresses are allowed.")

    return str(address)


class NetLagEngine:

    def __init__(self, update_log_cb, stop_ui_cb, update_status_cb):
        self.update_log_cb = update_log_cb
        self.stop_ui_cb = stop_ui_cb
        self.update_status_cb = update_status_cb

        self.running = False
        self.stop_event = threading.Event()
        self.worker = None

        self.checks = 0
        self.successes = 0

        self.target_ip = ""
        self.target_port = 80
        self.duration = 30

        self.lock = threading.Lock()

    def start(self, ip, port, duration):

        if self.running:
            return

        self.target_ip = validate_target_ip(ip)
        self.target_port = int(port)
        self.duration = min(max(int(duration), 1), MAX_DURATION)

        self.checks = 0
        self.successes = 0

        self.stop_event.clear()
        self.running = True

        self.keep_screen_on(True)

        self.update_log_cb(
            f"> LOCAL TCP TEST STARTED: {self.target_ip}:{self.target_port}"
        )

        self.update_log_cb(
            f"> INTERVAL: 1 SECOND | DURATION: {self.duration}s"
        )

        self.worker = threading.Thread(
            target=self.run_test,
            daemon=True
        )
        self.worker.start()

    def run_test(self):

        deadline = time.monotonic() + self.duration

        try:
            while (
                self.running
                and not self.stop_event.is_set()
                and time.monotonic() < deadline
            ):

                cycle_start = time.monotonic()
                check_start = time.monotonic()

                result = "NO CONNECTION"

                try:
                    with socket.create_connection(
                        (self.target_ip, self.target_port),
                        timeout=2
                    ):
                        result = "CONNECTED"

                        with self.lock:
                            self.successes += 1

                except OSError:
                    result = "NO CONNECTION"

                elapsed = (time.monotonic() - check_start) * 1000

                with self.lock:
                    self.checks += 1
                    checks = self.checks
                    successes = self.successes

                self.update_status_cb(checks, successes)

                self.update_log_cb(
                    f"> CHECK {checks}: {result} | {elapsed:.1f} ms"
                )

                remaining = CHECK_INTERVAL - (
                    time.monotonic() - cycle_start
                )

                if remaining > 0:
                    self.stop_event.wait(remaining)

        finally:
            self.running = False
            self.keep_screen_on(False)

            if self.stop_event.is_set():
                self.update_log_cb("> TEST STOPPED BY USER.")
            else:
                self.update_log_cb("> TEST DURATION COMPLETED.")

            Clock.schedule_once(
                lambda dt: self.stop_ui_cb(),
                0
            )

    def stop(self):

        if self.running:
            self.stop_event.set()
            self.update_log_cb("> STOP REQUESTED...")

    def keep_screen_on(self, enable):

        if not IS_ANDROID or activity is None:
            return

        try:
            from android.runnable import run_on_ui_thread

            if enable:

                @run_on_ui_thread
                def keep_on():
                    activity.getWindow().addFlags(
                        FLAG_KEEP_SCREEN_ON
                    )

                keep_on()

            else:

                @run_on_ui_thread
                def keep_off():
                    activity.getWindow().clearFlags(
                        FLAG_KEEP_SCREEN_ON
                    )

                keep_off()

        except Exception:
            pass


class MainLayout(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.target_ip = self.get_local_ip()
        self.port = 80
        self.duration = 30

        self.check_count = 0
        self.success_count = 0

        self.engine = NetLagEngine(
            self.update_log,
            self.reset_ui,
            self.update_status
        )

        # 1. TITLE
        self.title_label = Label(
            text="N E T - L A G",
            font_size='35sp',
            bold=True,
            color=(0, 1, 0, 1),
            size_hint_y=None,
            height=60
        )

        self.add_widget(self.title_label)

        # 2. STATUS GRID
        status_grid = GridLayout(
            cols=3,
            spacing=10,
            size_hint_y=None,
            height=80
        )

        self.ip_box, self.ip_value = self.create_status_box(
            "TARGET", self.target_ip
        )

        self.check_box, self.check_value = self.create_status_box(
            "CHECKS", "0"
        )

        self.success_box, self.success_value = self.create_status_box(
            "SUCCESS", "0"
        )

        status_grid.add_widget(self.ip_box)
        status_grid.add_widget(self.check_box)
        status_grid.add_widget(self.success_box)

        self.add_widget(status_grid)

        # 3. SCAN AREA
        self.scan_area = BoxLayout(size_hint_y=0.2)

        with self.scan_area.canvas:
            Color(0.1, 0.1, 0.1, 1)

            self.scan_bg = Rectangle(
                pos=self.scan_area.pos,
                size=self.scan_area.size
            )

            Color(0, 1, 0, 0.8)

            self.scan_line = Line(
                points=[
                    self.scan_area.x,
                    self.scan_area.y,
                    self.scan_area.right,
                    self.scan_area.y
                ],
                width=2
            )

        self.scan_area.bind(
            pos=self.update_scan_canvas,
            size=self.update_scan_canvas
        )

        self.scan_y = 0
        self.scan_direction = 1

        Clock.schedule_interval(
            self.animate_scan,
            0.02
        )

        self.add_widget(self.scan_area)

        # 4. TERMINAL LOG
        self.log_scroll = ScrollView()

        self.log_label = Label(
            text=(
                "> SYSTEM INITIALIZED...\n"
                "> SAFE LOCAL NETWORK CHECKER READY...\n"
                "> WAITING FOR COMMANDS...\n"
            ),
            font_size='12sp',
            color=(0, 1, 0, 1),
            halign='left',
            valign='top',
            size_hint_y=None
        )

        self.log_label.bind(
            texture_size=self.log_label.setter('size')
        )

        self.log_scroll.add_widget(self.log_label)
        self.add_widget(self.log_scroll)

        # 5. BUTTONS
        btn_grid = GridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None,
            height=60
        )

        self.config_btn = Button(
            text="CONFIG",
            background_color=(0, 0.5, 0, 1)
        )

        self.config_btn.bind(
            on_press=self.open_config
        )

        self.action_btn = Button(
            text="START TEST",
            background_color=(0, 0.8, 0, 1)
        )

        self.action_btn.bind(
            on_press=self.toggle_test
        )

        btn_grid.add_widget(self.config_btn)
        btn_grid.add_widget(self.action_btn)

        self.add_widget(btn_grid)

        Clock.schedule_interval(
            self.glitch_title,
            0.1
        )

    # STATUS BOX
    def create_status_box(self, title, value):

        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80
        )

        box.add_widget(
            Label(
                text=title,
                font_size='10sp',
                color=(0.7, 0.7, 0.7, 1)
            )
        )

        value_label = Label(
            text=value,
            font_size='14sp',
            bold=True,
            color=(0, 1, 0, 1)
        )

        box.add_widget(value_label)

        return box, value_label

    # LOCAL IP
    def get_local_ip(self):

        try:
            candidates = socket.getaddrinfo(
                socket.gethostname(),
                None
            )

            for item in candidates:
                ip = item[4][0]

                try:
                    address = ipaddress.ip_address(ip)

                    if (
                        address.version == 4
                        and address.is_private
                        and not address.is_loopback
                    ):
                        return ip

                except ValueError:
                    continue

        except OSError:
            pass

        return "127.0.0.1"

    # GLITCH TITLE ANIMATION
    def glitch_title(self, dt):

        if random.random() > 0.8:

            self.title_label.x = random.randint(-5, 5)

            self.title_label.color = (
                (1, 0, 0, 1)
                if random.random() > 0.5
                else (0, 1, 1, 1)
            )

        else:

            self.title_label.x = 0
            self.title_label.color = (0, 1, 0, 1)

    # SCAN LINE ANIMATION
    def update_scan_canvas(self, *_args):

        self.scan_bg.pos = self.scan_area.pos
        self.scan_bg.size = self.scan_area.size

        self.scan_line.points = [
            self.scan_area.x,
            self.scan_area.y + self.scan_y,
            self.scan_area.right,
            self.scan_area.y + self.scan_y
        ]

    def animate_scan(self, dt):

        height = max(self.scan_area.height, 1)

        self.scan_y += (
            self.scan_direction * height * 0.05
        )

        if self.scan_y > height:
            self.scan_direction = -1

        elif self.scan_y < 0:
            self.scan_direction = 1

        self.scan_y = max(
            0,
            min(self.scan_y, height)
        )

        self.scan_line.points = [
            self.scan_area.x,
            self.scan_area.y + self.scan_y,
            self.scan_area.right,
            self.scan_area.y + self.scan_y
        ]

    # LOG SYSTEM
    def update_log(self, message):

        Clock.schedule_once(
            lambda dt: self._append_log(message),
            0
        )

    def _append_log(self, message):

        self.log_label.text += message + "\n"
        self.log_scroll.scroll_y = 0

    # UPDATE STATUS
    def update_status(self, checks, successes):

        def apply(dt):

            self.check_count = checks
            self.success_count = successes

            self.check_value.text = str(checks)
            self.success_value.text = str(successes)

        Clock.schedule_once(apply, 0)

    # RESET BUTTON
    def reset_ui(self):

        self.action_btn.text = "START ATTACK"

        self.action_btn.background_color = (
            0,
            0.8,
            0,
            1
        )

    # START / STOP
    def toggle_test(self, instance):

        if not self.engine.running:

            try:
                checked_ip = validate_target_ip(
                    self.target_ip
                )

                if not 1 <= int(self.port) <= 65535:
                    raise ValueError(
                        "Port must be between 1 and 65535."
                    )

                if not 1 <= int(self.duration) <= MAX_DURATION:
                    raise ValueError(
                        "Duration must be between 1 and 30 seconds."
                    )

                self.engine.start(
                    checked_ip,
                    self.port,
                    self.duration
                )

                self.action_btn.text = "STOP ATTACK"

                self.action_btn.background_color = (
                    0.8,
                    0,
                    0,
                    1
                )

            except ValueError as error:

                self.update_log(
                    f"> CONFIG ERROR: {error}"
                )

        else:

            self.engine.stop()

    # CONFIG POPUP
    def open_config(self, instance):

        if self.engine.running:

            self.update_log(
                "> STOP THE CURRENT TEST BEFORE CONFIGURATION."
            )

            return

        content = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10
        )

        content.add_widget(
            Label(text="Enter Private / Local IP:")
        )

        ip_input = TextInput(
            text=self.target_ip,
            multiline=False
        )

        content.add_widget(ip_input)

        content.add_widget(
            Label(text="Enter TCP Port:")
        )

        port_input = TextInput(
            text=str(self.port),
            multiline=False,
            input_filter='int'
        )

        content.add_widget(port_input)

        content.add_widget(
            Label(text="Duration (1-30 Seconds):")
        )

        duration_input = TextInput(
            text=str(self.duration),
            multiline=False,
            input_filter='int'
        )

        content.add_widget(duration_input)

        save_btn = Button(
            text="SAVE",
            size_hint_y=None,
            height=50,
            background_color=(0, 0.8, 0, 1)
        )

        content.add_widget(save_btn)

        popup = Popup(
            title="CONFIGURATION",
            content=content,
            size_hint=(0.9, 0.8)
        )

        save_btn.bind(
            on_press=lambda x: self.save_config(
                ip_input.text,
                port_input.text,
                duration_input.text,
                popup
            )
        )

        popup.open()

    # SAVE CONFIG
    def save_config(self, ip, port, duration, popup):

        try:

            checked_ip = validate_target_ip(ip)
            checked_port = int(port)
            checked_duration = int(duration)

            if not 1 <= checked_port <= 65535:
                raise ValueError(
                    "Invalid port number."
                )

            if not 1 <= checked_duration <= MAX_DURATION:
                raise ValueError(
                    "Duration must be 1-90 seconds."
                )

            self.target_ip = checked_ip
            self.port = checked_port
            self.duration = checked_duration

            self.ip_value.text = checked_ip

            self.update_log(
                "> CONFIGURATION SAVED."
            )

            popup.dismiss()

        except (ValueError, TypeError) as error:

            self.update_log(
                f"> ERROR: {error}"
            )


class NetLagApp(App):

    def build(self):

        Window.clearcolor = (
            0.05,
            0.05,
            0.05,
            1
        )

        return MainLayout()


if __name__ == '__main__':
    NetLagApp().run()
