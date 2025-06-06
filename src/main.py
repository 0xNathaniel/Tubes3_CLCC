import flet as ft
from ui.home_page import HomePage

def main(page: ft.Page):
    page.title = "CV ATS - Applicant Tracking System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 900
    page.padding = 20
    
    home_page = HomePage()
    
    def route_change(e):
        page.views.clear()
        
        route = page.route
        
        if route == "/" or route == "":
            view = ft.View(
                "/",
                [],
                appbar=ft.AppBar(
                    title=ft.Text("CV ATS - Home"),
                    bgcolor="#1976d2",
                    color="white"
                )
            )
            # Build home page content
            home_page.build(view)
            page.views.append(view)
        
        page.update()
    
    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)