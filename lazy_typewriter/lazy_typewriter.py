import os
import time
import keyboard
import platform
import flet as ft

from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key as KeyboardKey

class TypeText(ft.UserControl):
    def __init__(self, lv: ft.ListView, vm_mode_switch_btn: ft.Switch, trigger_snack_bar, type_str_field_value=""):
        super().__init__()
        self.lv = lv
        self.trigger_snack_bar = trigger_snack_bar
        self.vm_mode_switch_btn = vm_mode_switch_btn
        self.type_str_field = ft.TextField(value=type_str_field_value, autofocus=True, cursor_color=ft.colors.BLACK,
                                           color=ft.colors.BLACK, text_align=ft.TextAlign.LEFT, width=300, bgcolor=ft.colors.GREY_400)
        self.drag_icon = ft.Icon(ft.icons.DRAG_INDICATOR, scale=1.8)
        self.pynput_keyboard = KeyboardController()

    def delete_text_field(self, e):
        self.lv.controls.remove(self)
        self.lv.update()

    def keyboard_type(self, e):
        if self.type_str_field.value == "":
            return
        if platform.system() == 'Windows':
            keyboard.press_and_release("alt+tab")
        elif platform.system() == 'Darwin':
            keyboard.press_and_release('command+tab')
        time.sleep(0.3)
        if self.vm_mode_switch_btn.value:
            self._type_text_with_pynput(self.type_str_field.value)
        else:
            keyboard.write(self.type_str_field.value, delay=0.01)
        self.update()
        self.trigger_snack_bar(e, "Typed")

    def build(self):
        return ft.DragTarget(
            on_accept=self._drag_accept,
            content=ft.Row(
                [
                    ft.Draggable(
                        content=self.drag_icon,
                        content_when_dragging=ft.Icon(ft.icons.DRAG_INDICATOR, scale=1.8, color=ft.colors.PRIMARY),
                    ),
                    self.type_str_field,
                    ft.IconButton(ft.icons.KEYBOARD_RETURN,
                                  on_click=self.keyboard_type),
                    ft.IconButton(ft.icons.DELETE,
                                  on_click=self.delete_text_field)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def _drag_accept(self, e: ft.DragTargetAcceptEvent):
        src = self.page.get_control(e.src_id)
        srcouce_index = None
        target_index = None

        for i, line in enumerate(self.lv.controls):
            if line.drag_icon == src.content:
                srcouce_index = i
            if line.drag_icon == self.drag_icon:
                target_index = i

        if srcouce_index is None or target_index is None:
            raise Exception("Can't find srcouce_index or target_index")

        if srcouce_index == target_index:
            self.lv.update()
            return

        for i, line in enumerate(self.lv.controls):
            if line.drag_icon == src.content:
                srcouce = self.lv.controls.pop(i)
                break

        self.lv.update()

        for i, line in enumerate(self.lv.controls):
            if line.drag_icon == self.drag_icon:
                if srcouce_index > target_index:
                    self.lv.controls.insert(i, srcouce)
                else:
                    self.lv.controls.insert(i+1, srcouce)
                break

        self.lv.update()

    def _type_text_with_pynput(self, type_str: str):
        need_convert_char = "~!@#$%^&*()_+{}|:\"<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        mapping_convert_char = "`1234567890-=[]\\;',./abcdefghijklmnopqrstuvwxyz"
        for char in type_str:
            if not char.isascii():
                continue
            if char in need_convert_char:
                self.pynput_keyboard.press(KeyboardKey.shift_l)
                self.pynput_keyboard.press(
                    mapping_convert_char[need_convert_char.index(char)])
                self.pynput_keyboard.release(KeyboardKey.shift_l)
                self.pynput_keyboard.release(
                    mapping_convert_char[need_convert_char.index(char)])
            elif char == " ":
                self.pynput_keyboard.press(KeyboardKey.space)
                self.pynput_keyboard.release(KeyboardKey.space)
            else:
                self.pynput_keyboard.press(char)
                self.pynput_keyboard.release(char)
            time.sleep(0.01)


class TypeTextListView(ft.UserControl):

    def __init__(self, vm_mode_switch_btn: ft.Switch, trigger_snack_bar, save_path=""):
        super().__init__(expand=1)
        self.trigger_snack_bar = trigger_snack_bar
        self.save_path = self.get_save_path() if save_path == "" else save_path
        self.lv = ft.ListView(expand=1, spacing=10, padding=20)
        self.vm_mode_switch_btn = vm_mode_switch_btn

    def get_save_path(self):
        if platform.system() == 'Windows':
            return os.getenv('LOCALAPPDATA') + "\\Lazy_typewriter\\type_content.txt"
        elif platform.system() == 'Darwin':
            return os.getenv('HOME') + "/Library/Application Support/Lazy_typewriter/type_content.txt"

    def restore_saved_content(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, "r", encoding='utf-8') as f:
                for line in f.readlines():
                    self.lv.controls.append(TypeText(
                        self.lv, self.vm_mode_switch_btn, self.trigger_snack_bar, type_str_field_value=line.strip()))
        if self.lv.controls == []:
            self.lv.controls.append(TypeText(self.lv, self.vm_mode_switch_btn, self.trigger_snack_bar))
        self.update()

    def add_typing_text_field(self, e):
        self.lv.controls.insert(0, TypeText(self.lv, self.vm_mode_switch_btn, self.trigger_snack_bar))
        self.update()

    def save_content(self, e):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        with open(self.save_path, "w", encoding='utf-8') as f:
            for control in self.lv.controls:
                if isinstance(control, TypeText) and control.type_str_field.value != "":
                    f.write(control.type_str_field.value + "\n")
        
        self.trigger_snack_bar(e, "Saved")

    def build(self):
        return self.lv

def main(page: ft.Page):
    page.title = "Lazy typewriter"
    page.window_height = 343
    page.window_width = 500
    page.window_min_height = 343
    page.window_min_width = 500
    page.window_always_on_top = True
    page.bgcolor = ft.colors.GREY_800
    page.theme_mode = ft.ThemeMode.DARK

    vm_mode_switch_btn = ft.Switch(
        label="VM mode", label_position=ft.LabelPosition.LEFT, value=False, scale=0.9)
        
    def trigger_snack_bar(e, text):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
            show_close_icon=True,
            duration=500,
            bgcolor=ft.colors.GREEN_400,
        )
        page.snack_bar.open = True
        page.update()

    type_text_list_view = TypeTextListView(vm_mode_switch_btn, trigger_snack_bar)

    def pin_window(e):
        page.window_always_on_top = not page.window_always_on_top
        pin_icon.rotate = ft.Rotate(angle=44.5 if page.window_always_on_top else 0)
        page.update()
    
    pin_icon = ft.IconButton(ft.icons.PUSH_PIN, rotate=ft.Rotate(angle=44.5), on_click=pin_window)

    def add_typing_text_field(e):
        type_text_list_view.add_typing_text_field(e)

    def save_content(e):
        type_text_list_view.save_content(e)

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.KEYBOARD_OUTLINED),
        leading_width=40,
        title=ft.Text("Lazy typewriter"),
        center_title=False,
        bgcolor=ft.colors.BLACK45,
        actions=[
            vm_mode_switch_btn,
            ft.IconButton(ft.icons.ADD, on_click=add_typing_text_field),
            ft.IconButton(ft.icons.SAVE, on_click=save_content),
            pin_icon
        ],
    )
    page.add(type_text_list_view)
    type_text_list_view.restore_saved_content()


ft.app(target=main, assets_dir="assets")
