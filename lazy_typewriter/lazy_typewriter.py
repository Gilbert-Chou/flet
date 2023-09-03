import os
import time
import keyboard
import platform
import flet as ft

class TypeText(ft.UserControl):
    def __init__(self, lv: ft.ListView, type_str_field_value=""):
        super().__init__()
        self.type_str_field_value = type_str_field_value
        self.lv = lv

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
        keyboard.write(self.type_str_field.value, delay=0.01)
        self.update()

    def build(self):
        self.type_str_field = ft.TextField(value=self.type_str_field_value, autofocus=True, cursor_color=ft.colors.BLACK,
                                           color=ft.colors.BLACK, text_align=ft.TextAlign.LEFT, width=300, bgcolor=ft.colors.GREY_400)
        return ft.Row(
            [
                self.type_str_field,
                ft.IconButton(ft.icons.KEYBOARD_RETURN,
                              on_click=self.keyboard_type),
                ft.IconButton(ft.icons.DELETE, on_click=self.delete_text_field)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

class TypeTextListView(ft.UserControl):

    def __init__(self, save_path=""):
        super().__init__()
        self.save_path = self.get_save_path() if save_path == "" else save_path
        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

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
                        self.lv, type_str_field_value=line.strip()))
        if self.lv.controls == []:
            self.lv.controls.append(TypeText(self.lv))
        self.update()

    def add_typing_text_field(self, e):
        self.lv.controls.append(TypeText(self.lv))
        self.update()

    def save_content(self, e):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        with open(self.save_path, "w", encoding='utf-8') as f:
            for control in self.lv.controls:
                if isinstance(control, TypeText) and control.type_str_field.value != "":
                    f.write(control.type_str_field.value + "\n")

    def build(self):
        return self.lv

def main(page: ft.Page):
    page.title = "Lazy typewriter"
    page.window_height = 343
    page.window_width = 470
    page.window_min_height = 343
    page.window_min_width = 470
    page.window_always_on_top = True
    page.bgcolor = ft.colors.GREY_800

    type_text_list_view = TypeTextListView()

    def pin_window(e):
        page.window_always_on_top = not page.window_always_on_top
        page.update()

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
            ft.IconButton(ft.icons.PUSH_PIN, on_click=pin_window)
        ],
    )
    page.add(type_text_list_view)
    type_text_list_view.restore_saved_content()

ft.app(target=main, assets_dir="assets")
