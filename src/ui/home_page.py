import flet as ft

class HomePage:
    def __init__(self):
        self.search_algorithm = "KMP"  # Default algorithm
        self.top_matches = 5  # Default number of top matches
        
    def build(self, page):
        # Main title
        title = ft.Text("CV ATS - Applicant Tracking System", size=24, weight="bold")
        
        # Keyword input field
        self.keyword_input = ft.TextField(
            label="Enter keywords (separated by comma)",
            hint_text="e.g. Python, React, SQL",
            width=600
        )
        
        # Algorithm selection
        algorithm_text = ft.Text("Select Algorithm:")
        self.algorithm_toggle = ft.SegmentedButton(
            selected={self.search_algorithm},
            segments=[
                ft.Segment(value="KMP", label=ft.Text("KMP")),
                ft.Segment(value="BM", label=ft.Text("Boyer-Moore")),
            ],
            on_change=self.algorithm_changed
        )
        
        # Top matches selection
        top_matches_text = ft.Text("Top Matches:")
        self.top_matches_dropdown = ft.Dropdown(
            width=100,
            options=[
                ft.dropdown.Option(text="5", key="5"),
                ft.dropdown.Option(text="10", key="10"),
                ft.dropdown.Option(text="15", key="15"),
                ft.dropdown.Option(text="20", key="20"),
            ],
            value="5",
            on_change=self.top_matches_changed
        )
        
        # Search button
        search_button = ft.ElevatedButton(
            text="Search",
            icon="search",
            on_click=self.search_cvs
        )
        
        # Summary section for execution times
        self.summary_section = ft.Text("", size=14)
        
        # Results container
        self.results_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=400,
            spacing=10
        )
        
        # Create layout
        algorithm_row = ft.Row([algorithm_text, self.algorithm_toggle])
        top_matches_row = ft.Row([top_matches_text, self.top_matches_dropdown])
        controls_row = ft.Row([algorithm_row, top_matches_row, search_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Change this part: instead of page.add, use page.controls.extend
        if isinstance(page, ft.View):
            # For View objects in routing
            page.controls.extend([
                title,
                self.keyword_input,
                controls_row,
                self.summary_section,
                ft.Divider(),
                ft.Text("Search Results:", size=18, weight="bold"),
                self.results_container
            ])
        else:
            # For direct Page rendering
            page.add(
                title,
                self.keyword_input,
                controls_row,
                self.summary_section,
                ft.Divider(),
                ft.Text("Search Results:", size=18, weight="bold"),
                self.results_container
            )
    
    def algorithm_changed(self, e):
        # Function to handle algorithm selection change
        self.search_algorithm = list(self.algorithm_toggle.selected)[0]
    
    def top_matches_changed(self, e):
        # Function to handle top matches selection change
        self.top_matches = int(self.top_matches_dropdown.value)
    
    def search_cvs(self, e):
        # This will be implemented later
        self.summary_section.value = "Search functionality will be implemented later."
        self.summary_section.update()
        
        # Sample results for UI preview
        self.results_container.controls.clear()
        
        # Add sample CV cards
        for i in range(3):
            card_content = ft.Column([
                ft.Text(f"Sample Applicant {i+1}", weight="bold"),
                ft.Text("Position: Software Developer"),
                ft.Text(f"Matched Keywords: 3 of 5", weight="bold"),
                ft.Text("Sample matches:"),
                ft.Text("• Python: 5 occurrences"),
                ft.Text("• React: 2 occurrences"),
                ft.Text("• SQL: 1 occurrence"),
            ])
            
            # Buttons
            buttons_row = ft.Row([
                ft.ElevatedButton(
                    text="Summary",
                    icon="summarize",
                    on_click=lambda e, app_id=i: self.view_summary(e, app_id)
                ),
                ft.ElevatedButton(
                    text="View CV",
                    icon="description",
                    on_click=self.view_cv
                )
            ])
            
            card_content.controls.append(buttons_row)
            
            # Add card to results container
            self.results_container.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=card_content,
                        padding=10
                    ),
                    elevation=2
                )
            )
        
        self.results_container.update()
    
    def view_summary(self, e, application_id):
        # To be implemented - navigate to summary page
        e.page.go(f"/summary/{application_id}")
    
    def view_cv(self, e):
        # To be implemented - open CV file
        pass