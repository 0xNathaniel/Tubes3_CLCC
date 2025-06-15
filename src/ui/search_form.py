import flet as ft

class SearchForm:
    def __init__(self, on_search, on_algorithm_changed, on_top_matches_changed):
        self.on_search = on_search
        self.on_algorithm_changed = on_algorithm_changed
        self.on_top_matches_changed = on_top_matches_changed
        self.search_algorithm = "kmp"
        
    def build(self):
        self.keyword_input = ft.TextField(
            label="Enter keywords (separated by comma)",
            hint_text="e.g. Python, React, SQL, nursing, accounting, marketing, finance",
            expand=True,
            height=60,
            text_size=16,
            border_radius=12,
            border_color="#666666"
        )
        
        algorithm_text = ft.Text("Select Search Algorithm:", weight="bold", size=16)
        self.algorithm_toggle = ft.SegmentedButton(
            expand=True,
            selected={self.search_algorithm},
            segments=[
                ft.Segment(value="kmp", label=ft.Text("KMP Algorithm", size=14)),
                ft.Segment(value="boyer_moore", label=ft.Text("Boyer-Moore", size=14)),
                ft.Segment(value="aho_corasick", label=ft.Text("Aho-Corasick", size=14)),
            ],
            on_change=self._handle_algorithm_change
        )
        
        top_matches_text = ft.Text("Number of Results:", weight="bold", size=16)
        self.top_matches_dropdown = ft.Dropdown(
            width=150,
            text_size=14,
            options=[
                ft.dropdown.Option(text="1", key="1"),
                ft.dropdown.Option(text="2", key="2"),  
                ft.dropdown.Option(text="5", key="5"),
                ft.dropdown.Option(text="10", key="10"),
                ft.dropdown.Option(text="15", key="15"),
                ft.dropdown.Option(text="20", key="20"),
                ft.dropdown.Option(text="30", key="30"),
                ft.dropdown.Option(text="50", key="50"),
                ft.dropdown.Option(text="100", key="100"),
                ft.dropdown.Option(text="1000", key="1000"),
            ],
            value="5",
            border_radius=10,
            on_change=self._handle_top_matches_change
        )
        
        self.search_button = ft.ElevatedButton(
            text="Search CVs",
            icon="search",
            width=180,
            height=50,
            bgcolor="#333333",
            color="white",
            on_click=self.on_search,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16))
        )
        
        controls_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        algorithm_text,
                        self.algorithm_toggle
                    ], spacing=10),
                    margin=ft.margin.only(bottom=15)
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            top_matches_text,
                            self.top_matches_dropdown
                        ], spacing=10),
                        expand=1
                    ),
                    ft.Container(
                        content=self.search_button,
                        expand=1,
                        alignment=ft.alignment.center_right
                    )
                ], spacing=20)
            ]),
            padding=20,
            bgcolor="#ffffff",
            border_radius=12,
            border=ft.border.all(1, "#cccccc")
        )
        
        return ft.Column([
            self.keyword_input,
            ft.Divider(height=20, color="transparent"),
            controls_container,
        ])
        
    def _handle_algorithm_change(self, e):
        self.search_algorithm = list(self.algorithm_toggle.selected)[0]
        self.on_algorithm_changed(self.search_algorithm)
        
    def _handle_top_matches_change(self, e):
        top_n = int(self.top_matches_dropdown.value)
        self.on_top_matches_changed(top_n)
        
    def set_searching_state(self, is_searching):
        if is_searching:
            self.search_button.text = "Searching..."
            self.search_button.disabled = True
        else:
            self.search_button.text = "Search CVs"
            self.search_button.disabled = False
            
        self.search_button.update()