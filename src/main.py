import flet as ft
from ui.home_page import HomePage
from ui.summary_page import SummaryPage

def main(page: ft.Page):
    page.title = "CV ATS - Applicant Tracking System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    
    home_page = HomePage()
    summary_page = SummaryPage()
    
    def route_change(e):
        page.views.clear()
        
        route = page.route
        
        if route == "/" or route == "":
            # Home page
            view = ft.View("/", [])
            home_page.build(view)
            page.views.append(view)
        elif route.startswith("/summary/"):
            # Summary page
            try:
                application_id = int(route.split("/")[-1])
                view = ft.View(f"/summary/{application_id}", [])
                summary_page.build(view, application_id)
                page.views.append(view)
            except:
                page.go("/")
                return
        
        page.update()
    
    page.on_route_change = route_change
    
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)