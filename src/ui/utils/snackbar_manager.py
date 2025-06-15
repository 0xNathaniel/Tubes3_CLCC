import flet as ft

class SnackbarManager:
    def __init__(self, page):
        self.page = page
        
    def show_success(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#555555")
                )
            else:
                print(f"SUCCESS: {message}")
        except Exception as _:
            print(f"SUCCESS: {message}")
    
    def show_error(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#333333")
                )
            else:
                print(f"ERROR: {message}")
        except Exception as _:
            print(f"ERROR: {message}")
    
    def show_info(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#666666")
                )
            else:
                print(f"INFO: {message}")
        except Exception as _:
            print(f"INFO: {message}")