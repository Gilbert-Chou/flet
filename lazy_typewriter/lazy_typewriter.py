import os
import time
import keyboard
import platform
import flet as ft

from config_singleton import sys_config
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key as KeyboardKey

    
class SettingPopupMenuItem(ft.PopupMenuItem):

    def __init__(self, page: ft.Page, text: str, config_name: str, customized_on_click=None):
        check_icon = ft.Icon(ft.icons.CHECK if getattr(sys_config, config_name) else "", size=20) 
        container = ft.Container(
            content=ft.Row(
                [check_icon, ft.Text(text)],
                alignment=ft.MainAxisAlignment
            ),
        )
        def on_click(e):
            is_checked_now = not getattr(sys_config, config_name)
            setattr(sys_config, config_name, is_checked_now)
            check_icon.name = ft.icons.CHECK if is_checked_now else ""
            if customized_on_click:
                customized_on_click(e)
            page.update()

        return super().__init__(content=container, on_click=on_click, height=1, checked=None)

class TypeText(ft.Row):

    def __init__(self, lv: ft.ListView, trigger_snack_bar, type_str_field_value=""):
        super().__init__()
        self.lv = lv
        self.trigger_snack_bar = trigger_snack_bar
        self.type_str_field = ft.TextField(value=type_str_field_value, autofocus=True, cursor_color=ft.colors.BLACK,
                                           color=ft.colors.BLACK, text_align=ft.TextAlign.LEFT, expand=True, width=300, bgcolor=ft.colors.GREY_400)
        self.drag_icon = ft.Icon(ft.icons.DRAG_INDICATOR, scale=1.80)
        self.pynput_keyboard = KeyboardController()

        self.controls = [
            ft.Draggable(
                content=self.drag_icon,
                content_when_dragging=ft.Icon(ft.icons.DRAG_INDICATOR, scale=1.8, color=ft.colors.PRIMARY),
            ),
            self.type_str_field,
            ft.IconButton(ft.icons.KEYBOARD_RETURN, on_click=self.keyboard_type),
            ft.IconButton(ft.icons.DELETE, on_click=self.delete_text_field)
        ]

    def delete_text_field(self, e):
        for i, line in enumerate(self.lv.controls):
            if line.content.content.drag_icon == self.drag_icon:
                self.lv.controls.pop(i)
                break
        self.lv.update()

    def keyboard_type(self, e):
        if self.type_str_field.value == "":
            return
        if platform.system() == 'Windows':
            keyboard.press_and_release("alt+tab")
        elif platform.system() == 'Darwin':
            keyboard.press_and_release('command+tab')
        time.sleep(0.3)
        if getattr(sys_config, "vm_mode"):
            self._type_text_with_pynput(self.type_str_field.value)
        else:
            keyboard.write(self.type_str_field.value, delay=0.01)
        self.update()
        self.trigger_snack_bar(e, "Typed")

    def drag_accept(self, e: ft.DragTargetAcceptEvent):
        src = self.page.get_control(e.src_id)
        srcouce_index = None
        target_index = None

        for i, line in enumerate(self.lv.controls):
            if line.content.content.drag_icon == src.content:
                srcouce_index = i
            if line.content.content.drag_icon == self.drag_icon:
                target_index = i

        if srcouce_index is None or target_index is None:
            raise Exception("Can't find srcouce_index or target_index")

        if srcouce_index == target_index:
            self.lv.update()
            return

        for i, line in enumerate(self.lv.controls):
            if line.content.content.drag_icon == src.content:
                srcouce = self.lv.controls.pop(i)
                break

        self.lv.update()

        for i, line in enumerate(self.lv.controls):
            if line.content.content.drag_icon == self.drag_icon:
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
                self._slow_mode()
                self.pynput_keyboard.release(KeyboardKey.shift_l)
                self.pynput_keyboard.release(
                    mapping_convert_char[need_convert_char.index(char)])
                self._slow_mode()
            elif char == " ":
                self.pynput_keyboard.press(KeyboardKey.space)
                self.pynput_keyboard.release(KeyboardKey.space)
            else:
                self.pynput_keyboard.press(char)
                self.pynput_keyboard.release(char)
            time.sleep(0.01)
    
    def _slow_mode(self):
        if getattr(sys_config, "slow_mode"):
            time.sleep(getattr(sys_config, "slow_mode_time"))


class TypeTextListView(ft.ListView):

    def __init__(self: ft.Switch, trigger_snack_bar, save_path=""):
        super().__init__(expand=1)
        self.trigger_snack_bar = trigger_snack_bar
        self.save_path = self.get_save_path() if save_path == "" else save_path
        self.controls = []

    def get_save_path(self):
        if platform.system() == 'Windows':
            return os.getenv('LOCALAPPDATA') + "\\Lazy_typewriter\\type_content.txt"
        elif platform.system() == 'Darwin':
            return os.getenv('HOME') + "/Library/Application Support/Lazy_typewriter/type_content.txt"

    def restore_saved_content(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, "r", encoding='utf-8') as f:
                for line in f.readlines():
                    self.controls.append(self._new_drag_target(TypeText(
                        self, self.trigger_snack_bar, type_str_field_value=line.strip())))
        if self.controls == []:
            self.controls.append(self._new_drag_target(TypeText(self, self.trigger_snack_bar)))
        self.update()

    def add_typing_text_field(self, e):
        self.controls.insert(0, self._new_drag_target(TypeText(self, self.trigger_snack_bar)))
        self.update()

    def save_content(self, e):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        with open(self.save_path, "w", encoding='utf-8') as f:
            for control in self.controls:
                if isinstance(control, TypeText) and control.type_str_field.value != "":
                    f.write(control.type_str_field.value + "\n")
        
        self.trigger_snack_bar(e, "Saved")
    
    def _new_drag_target(self, content: TypeText):
        return ft.Container(
            ft.DragTarget(
                on_accept=content.drag_accept,
                content=content,
            ),
            padding=ft.padding.symmetric(vertical=3)
        )


def main(page: ft.Page):
    page.title = "Lazy typewriter"
    page.window.height = 343
    page.window.width = 500
    page.window.min_height = 343
    page.window.min_width = 500
    page.window.always_on_top = True
    page.bgcolor = ft.colors.GREY_800
    page.theme_mode = ft.ThemeMode.DARK
       
    def trigger_snack_bar(e, text):
        snack_bar = ft.SnackBar(
            content=ft.Text(text, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
            show_close_icon=True,
            duration=500,
            bgcolor=ft.colors.GREEN_400,
        )
        snack_bar.open = True
        page.overlay.append(snack_bar)
        page.update()

    type_text_list_view = TypeTextListView(trigger_snack_bar)

    def pin_window(e):
        page.window.always_on_top = not page.window.always_on_top

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
            ft.IconButton(ft.icons.ADD, on_click=add_typing_text_field),
            ft.IconButton(ft.icons.SAVE, on_click=save_content),
            ft.PopupMenuButton(
                items=[
                    SettingPopupMenuItem(page=page, text="VM mode", config_name="vm_mode"),
                    ft.PopupMenuItem(),  # divider
                    SettingPopupMenuItem(page=page, text="Pin", config_name="pin", customized_on_click=pin_window),
                    ft.PopupMenuItem(),  # divider
                    SettingPopupMenuItem(page=page, text="Slow mode", config_name="slow_mode"),
                ]
            ),
        ],
    )
    page.add(type_text_list_view)
    type_text_list_view.restore_saved_content()


ft.app(target=main, assets_dir="assets")
