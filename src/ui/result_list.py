import flet as ft
import math
from ui.result_card import ResultCard

class ResultList:
    def __init__(self, on_view_summary, on_open_cv):
        self.on_view_summary = on_view_summary
        self.on_open_cv = on_open_cv
        self.current_page = 1
        self.items_per_page = 20
        self.all_results = []
        
    def build(self):
        self.results_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            expand=True
        )
        
        self.pagination_container = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Search Results", size=24, weight="bold", color="#1a1a1a"),
                ft.Divider(height=10, color="transparent"),
                self.results_container,
                ft.Divider(height=10, color="transparent"),
                self.pagination_container
            ]),
            expand=True,
            padding=20
        )
    
    def clear(self):
        """Clear results and pagination"""
        self.results_container.controls.clear()
        self.pagination_container.controls.clear()
        self.pagination_container.visible = False
        self.pagination_container.update()
        self.results_container.update()
    
    def display_results(self, results, keywords_string):
        self.all_results = results
        self.keywords_string = keywords_string
        self.current_page = 1
        
        self.update_pagination()
        self.display_current_page()
    
    def display_current_page(self):
        self.results_container.controls.clear()
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_results))
        
        current_page_results = self.all_results[start_idx:end_idx]
        
        for i, result in enumerate(current_page_results):
            rank = start_idx + i + 1
            result_card = ResultCard(
                result, 
                rank, 
                self.keywords_string,
                self.on_view_summary,
                self.on_open_cv
            )
            self.results_container.controls.append(result_card.build())
        
        self.results_container.update()
    
    def update_pagination(self):
        self.pagination_container.controls.clear()
        
        total_pages = math.ceil(len(self.all_results) / self.items_per_page)
        
        if total_pages <= 1:
            self.pagination_container.visible = False
            self.pagination_container.update()
            return
            
        self.pagination_container.visible = True
        
        prev_button = ft.IconButton(
            icon="chevron_left",
            tooltip="Previous page",
            on_click=self._go_to_prev_page,
            disabled=self.current_page == 1
        )
        
        next_button = ft.IconButton(
            icon="chevron_right",
            tooltip="Next page",
            on_click=self._go_to_next_page,
            disabled=self.current_page == total_pages
        )
        
        page_info = ft.Text(f"Page {self.current_page} of {total_pages}")
        
        self.pagination_container.controls.extend([
            prev_button,
            page_info,
            next_button
        ])
        
        self.pagination_container.update()
    
    def _go_to_prev_page(self, _):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination()
    
    def _go_to_next_page(self, _):
        total_pages = math.ceil(len(self.all_results) / self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination()
    
    def show_no_results(self):
        no_results_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", size=50),
                    ft.Text("No matching CVs found", weight="bold", size=20),
                    ft.Text("Try different keywords or adjust your search criteria", size=14, color="#666666"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            ),
            elevation=3
        )
        self.results_container.controls.append(no_results_card)
        self.results_container.update()
    
    def show_error(self, error_message):
        error_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("❌", size=50),
                    ft.Text("Search Error", weight="bold", size=20, color="#333333"),
                    ft.Text(f"Error: {error_message}", size=14, color="#555555", text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            ),
            elevation=3
        )
        self.results_container.controls.append(error_card)
        self.results_container.update()