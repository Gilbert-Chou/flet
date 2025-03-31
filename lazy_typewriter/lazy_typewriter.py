import time
import keyboard
import platform
import flet as ft

from utils import trigger_snack_bar, find_page
from config_singleton import sys_config, data_config
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

    def __init__(self, type_str_field_value=""):
        super().__init__()
        self.type_str_field = ft.TextField(value=type_str_field_value, cursor_color=ft.colors.BLACK,
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
    
    @property
    def text_value(self):
        return self.type_str_field.value

    def delete_text_field(self, e):
        for i, line in enumerate(self.get_list_view().controls):
            if self._check_typetext_container_instance(line) and line.get_drag_icon() == self.drag_icon:
                self.get_list_view().controls.pop(i)
                break
        self.get_list_view().update()

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
        trigger_snack_bar(self.parent, "Typed")

    def get_list_view(self) -> ft.Control:

        def find_parent(control: ft.Control):
            if isinstance(control, TypeTextExpansionPanelList):
                return control
            return find_parent(control.parent)

        return find_parent(self.parent)

    def drag_accept(self, e: ft.DragTargetAcceptEvent):
        src = self.page.get_control(e.src_id)
        srcouce_index = None
        target_index = None

        for i, line in enumerate(self.get_list_view().controls):
            if self._check_typetext_container_instance(line) and line.get_drag_icon() == src.content:
                srcouce_index = i
            if self._check_typetext_container_instance(line) and line.get_drag_icon() == self.drag_icon:
                target_index = i

        if srcouce_index is None or target_index is None:
            raise Exception("Can't find srcouce_index or target_index")

        if srcouce_index == target_index:
            self.get_list_view().update()
            return

        for i, line in enumerate(self.get_list_view().controls):
            if self._check_typetext_container_instance(line) and line.get_drag_icon() == src.content:
                srcouce = self.get_list_view().controls.pop(i)
                break

        self.get_list_view().update()

        for i, line in enumerate(self.get_list_view().controls):
            if self._check_typetext_container_instance(line) and line.get_drag_icon() == self.drag_icon:
                if srcouce_index > target_index:
                    self.get_list_view().controls.insert(i, srcouce)
                else:
                    self.get_list_view().controls.insert(i+1, srcouce)
                break

        self.get_list_view().update()
    
    def _check_typetext_container_instance(self, line: ft.Control):
        return isinstance(line, TypeTextExpansionPanel)

    def _type_text_with_pynput(self, type_str: str):
        need_convert_char = "~!@#$%^&*()_+{}|:\"<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        mapping_convert_char = "`1234567890-=[]\\;',./abcdefghijklmnopqrstuvwxyz"
        for char in type_str:
            if not char.isascii():
                continue
            if char in need_convert_char:
                self._slow_mode()
                self.pynput_keyboard.press(KeyboardKey.shift_l)
                self.pynput_keyboard.press(
                    mapping_convert_char[need_convert_char.index(char)])
                self._slow_mode()
                self.pynput_keyboard.release(KeyboardKey.shift_l)
                self.pynput_keyboard.release(
                    mapping_convert_char[need_convert_char.index(char)])
            elif char == " ":
                self.pynput_keyboard.press(KeyboardKey.space)
                self.pynput_keyboard.release(KeyboardKey.space)
            else:
                self.pynput_keyboard.press(char)
                self.pynput_keyboard.release(char)
            self._slow_mode(0.02)
            time.sleep(0.01)

    def _slow_mode(self, hard_sleep_time: int = None):
        if getattr(sys_config, "slow_mode"):
            time.sleep(hard_sleep_time if hard_sleep_time else getattr(sys_config, "slow_mode_time"))


class TypeTextExpansionPanel(ft.ExpansionPanel):

    def __init__(self, text: str = "", note: str = "", color: str = ft.colors.BLACK45):
        super().__init__()
        self.type_text = TypeText(type_str_field_value=text.strip())
        new_content = ft.Container(
            ft.DragTarget(
                on_accept=self.type_text.drag_accept,
                content=self.type_text,
            ),
            padding=ft.padding.symmetric(vertical=3)
        )
        self.bgcolor = color
        self.header = ft.ListTile(title=new_content)
        self.note = ft.Text(note.strip(), expand=True)

        self.content = ft.ListTile(
            content_padding=ft.padding.only(left=50, right=10),
            title=ft.Container(
                content=ft.Row(
                    [
                        self.note,
                        ft.Row(
                            [
                                ft.IconButton(ft.icons.COLOR_LENS, on_click=self._change_color),
                                ft.IconButton(ft.icons.MODE_OUTLINED, on_click=self._edit_note),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
        )

    @property
    def text_value(self) -> str:
        return self.type_text.text_value
    
    @property
    def note_value(self) -> str:
        return self.note.value

    def get_list_view(self) -> ft.ExpansionPanelList:
        
        def find_parent(control: ft.Control):
            if isinstance(control, TypeTextExpansionPanelList):
                return control
            return find_parent(control.parent)

        return find_parent(self)

    def get_drag_icon(self):
        return self.type_text.drag_icon

    def _change_color(self, e):
        colors = [
            ft.colors.BLACK45,
            ft.colors.GREEN_900,
            ft.colors.BLUE_900,
            ft.colors.RED_900,
        ]
        self.bgcolor = colors[(colors.index(self.bgcolor) + 1) % len(colors)]
        self.update()
    
    def _edit_note(self, e):

        page = find_page(self.parent)

        def handle_close(e):
            if e.control.text == "Save":
                self.note.value = note_field.value
                self.get_list_view().update()
                trigger_snack_bar(self.get_list_view().parent, "Changed")
            page.close(dialog)

        text_field_width = page.window.width * 0.8
        text_field_width = text_field_width if text_field_width < 800 else 800
        note_field = ft.TextField(value=self.note.value, multiline=True, cursor_color=ft.colors.BLACK, color=ft.colors.BLACK, text_align=ft.TextAlign.LEFT, expand=True, width=text_field_width, bgcolor=ft.colors.GREY_400)
        dialog = ft.AlertDialog(
            modal=True,
            content=note_field,
            actions=[
                ft.TextButton(text="Cancel", on_click=handle_close),
                ft.TextButton(text="Save", on_click=handle_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dialog)


class TypeTextExpansionPanelList(ft.ExpansionPanelList):

    def __init__(self):
        super().__init__()
        self.controls = []
        self.expand_icon_color = ft.colors.AMBER
        self.divider_color = ft.colors.AMBER

    def add_typing_text_field(self, e):
        self.controls.insert(0, TypeTextExpansionPanel())
        self.update()

    def restore_saved_content(self):
        for line in data_config.load_type_content():
            self.controls.append(TypeTextExpansionPanel(line['content'], line['note'], line["color"]))
        if self.controls == []:
            self.controls.append(TypeTextExpansionPanel())
        self.update()

    def save_content(self, e):
        content = []
        for control in self.controls:
            if isinstance(control, TypeTextExpansionPanel):
                type_content = control.text_value
                if type_content != "":
                    note = control.note_value if control.note_value else ""
                    content.append({"content": type_content, "note": note, "color": control.bgcolor})

        data_config.save_type_content(content)
        trigger_snack_bar(self.parent, "Saved")


def main(page: ft.Page):
    page.title = "Lazy typewriter"
    page.window.height = 470
    page.window.width = 500
    page.window.min_height = 470
    page.window.min_width = 500
    page.window.always_on_top = getattr(sys_config, "pin")
    page.bgcolor = ft.colors.GREY_800
    page.theme_mode = ft.ThemeMode.DARK

    type_text_list_view = TypeTextExpansionPanelList()
    main_list_view = ft.ListView(controls=[type_text_list_view], expand=True) # use ListView to make the ExpansionPanelList scrollable

    def pin_window(e):
        page.window.always_on_top = not page.window.always_on_top

    def add_typing_text_field(e):
        type_text_list_view.add_typing_text_field(e)
        main_list_view.scroll_to(0)

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

    page.add(main_list_view)
    type_text_list_view.restore_saved_content()


ft.app(target=main, assets_dir="assets")
