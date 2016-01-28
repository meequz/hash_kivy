#! /usr/bin/env python3
# coding: utf-8
import hashlib

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.core.clipboard import Clipboard


class WidgetFactory(object):
    FONT_SIZE = '24dp'
    
    def get_label(self, text='', mono=False):
        label = Label(
            text=text, font_size=self.FONT_SIZE, halign="left", markup=True)
        if mono:
            label.font_name='DroidSansMono'
        label.bind(size=label.setter('text_size'))
        return label
    
    def get_btn(self, text=''):
        return Button(text=text, font_size=self.FONT_SIZE)
    
    def get_text_input(self):
        return TextInput(multiline=False, font_size=self.FONT_SIZE)


class Screen(BoxLayout):
    def __init__(self, app):
        super(Screen, self).__init__(
            orientation='vertical', spacing='5dp', padding='20dp')
        self.app = app
        self.wf = WidgetFactory()
    
    def use(self):
        self.app.root.clear_widgets()
        self.app.root.add_widget(self)


class MainScreen(Screen):
    FORMAT_BORDER_MAX = 32
    
    def create(self, *args):
        self._current_string = ''
        self.clear_widgets()
        
        copy_btn = self._create_top_box()
        result_label_1, result_label_2 = self._create_result_labels()
        name_input, salt_input = self._create_inputs()
        self.add_widget(Label())
        f_slider = self._create_formatting()
        
        self._important_widgets = {
            'result_label_1': result_label_1,
            'result_label_2': result_label_2,
            'f_slider': f_slider,
            'name_input': name_input,
            'salt_input': salt_input,
            'copy_btn': copy_btn,
        }
        
        self.add_widget(Label())
        self._create_generate_btn()
        self.add_widget(Label())
    
    def _create_top_box(self):
        box = BoxLayout(orientation='horizontal')
        box.add_widget(self.wf.get_label('Result:'))
        
        def binding(btn):
            text_to_copy = self.hash_repr.text[:self.hash_repr.format_border]
            Clipboard.copy(text_to_copy)
        
        copy_btn = self.wf.get_btn('Copy')
        copy_btn.disabled = True
        copy_btn.bind(on_release=binding)
        box.add_widget(copy_btn)
        
        self.add_widget(box)
        return copy_btn
        
    def _create_result_labels(self):
        result_label_1 = self.wf.get_label(mono=True)
        result_label_2 = self.wf.get_label(mono=True)
        result_label_1.color = [0.7, 0.7, 0.7, 1]
        result_label_2.color = [0.7, 0.7, 0.7, 1]
        self.add_widget(result_label_1)
        self.add_widget(result_label_2)
        return result_label_1, result_label_2
    
    def _create_inputs(self):
        self.add_widget(self.wf.get_label('String:'))
        name_input = self.wf.get_text_input()
        self.add_widget(name_input)
        
        self.add_widget(self.wf.get_label('Salt:'))
        salt_input = self.wf.get_text_input()
        self.add_widget(salt_input)
        
        return name_input, salt_input
    
    def _create_formatting(self):
        f_label_text = 'Highlight first {} characters:'
        f_label = self.wf.get_label(f_label_text.format(12))
        
        def binding(slider, value):
            f_label.text = f_label_text.format(int(value))
            if value == self.FORMAT_BORDER_MAX:
                f_label.text = 'Highlight all'
            self._show_hash()
        
        f_slider = Slider(
            min=1, max=self.FORMAT_BORDER_MAX, step=1, value=12, padding='0dp')
        f_slider.bind(value=binding)
        self.add_widget(f_label)
        self.add_widget(f_slider)
        return f_slider
    
    def _create_generate_btn(self):
        name_input = self._important_widgets.get('name_input')
        salt_input = self._important_widgets.get('salt_input')
        
        def binding(btn):
            self._current_string = name_input.text + salt_input.text
            self._show_hash()
        
        generate_btn = self.wf.get_btn('Generate')
        generate_btn.bind(on_release=binding)
        self.add_widget(generate_btn)
    
    def _show_hash(self):
        hash_string = self._current_string.encode('utf-8')
        hash_string = hashlib.md5(hash_string)
        hash_string = hash_string.hexdigest()
        self._set_result(hash_string)
        copy_btn = self._important_widgets.get('copy_btn')
        copy_btn.disabled = False
    
    def _set_result(self, text):
        f_slider = self._important_widgets.get('f_slider')
        result_label_1 = self._important_widgets.get('result_label_1')
        result_label_2 = self._important_widgets.get('result_label_2')
        
        self.hash_repr = HashRepr(
            text, format_border=int(f_slider.value), color='ffff00')
        
        result_label_1.text = self.hash_repr.raw[0]
        result_label_2.text = self.hash_repr.raw[1]


class HashRepr(object):
    def __init__(self, text, format_border, color):
        self.text = text
        self.format_border = format_border
        self.color = color
        self.raw = []
        self._generate()
    
    def _generate(self):
        length = len(self.text)
        size = 4
        parts = [self.text[i:i+size] for i in range(0, length, size)]

        place = self.format_border / 4.0
        part_idx = int(place)
        char_idx = int((place - part_idx) * 4)
        
        if place == 4.0:
            parts[3] = parts[3] + '[/color]'
            parts[4] = '[/color]' + parts[4]
        elif place == 8.0:
            parts[7] = parts[7] + '[/color]'
        else:
            if part_idx <= 3:
                parts[part_idx] = parts[part_idx][:char_idx] \
                                  + '[/color]' \
                                  + parts[part_idx][char_idx:]
                parts[4] = '[/color]' + parts[4]
            else:
                parts[3] = parts[3] + '[/color]'
                parts[part_idx] = parts[part_idx][:char_idx] \
                                  + '[/color]' \
                                  + parts[part_idx][char_idx:]
            
        parts[0] = '[color={}]'.format(self.color) + parts[0]
        parts[4] = '[color={}]'.format(self.color) + parts[4]
        self.raw = [' '.join(parts[:4]), ' '.join(parts[4:])]


class MainApp(App):
    def initialize(self, *args):
        self.main_screen = MainScreen(self)
        self.main_screen.create()
        self.main_screen.use()
    
    def build(self):
        self.root = BoxLayout(orientation='horizontal')
        self.bind(on_start=self.initialize)
        return self.root


if __name__ == '__main__':
    MainApp().run()
