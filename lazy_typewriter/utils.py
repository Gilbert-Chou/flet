import flet as ft

def find_page(control: ft.Control) -> ft.Page:
    if isinstance(control, ft.View):
        return control.page
    return find_page(control.parent)

def trigger_snack_bar(control: ft.Control, text):
    snack_bar = ft.SnackBar(
        content=ft.Text(text, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
        show_close_icon=True,
        duration=500,
        bgcolor=ft.colors.GREEN_400,
    )
    snack_bar.open = True
    page = find_page(control)
    page.overlay.append(snack_bar)
    page.update()
