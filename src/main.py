import flet as ft
from ui.home_page import HomePage

def main(page: ft.Page):
    page.title = "CLCC ATS Friendly CV Scanner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1600  
    page.window_height = 1000 
    page.window_maximized = True 
    page.padding = 10 
    page.scroll = ft.ScrollMode.AUTO 
    
    app_header = ft.AppBar(title=ft.Text("CLCC ATS Friendly CV Scanner", size=20, weight="bold"),bgcolor="#666666",color="white",toolbar_height=70)
    page.appbar = app_header
    home_page = HomePage()
    home_page.build(page, page)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)