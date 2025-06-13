import flet as ft
from utils.find_top_n_cv_encrypted import find_top_n_cv
from utils.open_cv_details import open_cv_details
import os
import math

class HomePage:
    def __init__(self):
        self.search_algorithm = "kmp"  
        self.top_matches = 5
        self.page = None
        self.modal_visible = False
        self.current_page = 1
        self.items_per_page = 20
        self.all_results = []
        
    def build(self, view, page):
        self.page = page
        
        # Title
        title = ft.Text("CLCC ATS Friendly CV Scanner", 
                    size=32, weight="bold", color="#1a1a1a")
        subtitle = ft.Text("String matching using KMP, Boyer-Moore, and Aho-Corasick algorithms", 
                        size=18, italic=True, color="#4a4a4a")
        
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
            on_change=self.algorithm_changed
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
            on_change=self.top_matches_changed
        )
        
        self.search_button = ft.ElevatedButton(
            text="Search CVs",
            icon="search",
            width=180,
            height=50,
            bgcolor="#333333",
            color="white",
            on_click=self.search_cvs,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=16))
        )
        
        self.summary_section = ft.Text("", size=16, color="#555555", weight="w500")
        self.results_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            expand=True
        )
        
        self.pagination_container = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False
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
        
        header_section = ft.Container(
            content=ft.Column([
                title,
                subtitle,
                ft.Divider(height=30, color="transparent"),
                self.keyword_input,
                ft.Divider(height=20, color="transparent"),
                controls_container,
                ft.Divider(height=15, color="transparent"),
                self.summary_section,
            ]),
            padding=30,
            bgcolor="#f5f5f5",
            border_radius=15,
            margin=ft.margin.only(bottom=20)
        )
        
        results_section = ft.Container(
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
        
        self.modal_overlay = ft.Stack([
            ft.Container(
                expand=True,
                bgcolor="rgba(0,0,0,0.5)", 
                on_click=lambda _: self.hide_modal()
            ),
            
            ft.Container(
                width=550,
                content=ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Candidate Summary", size=18, weight="bold"),
                                ft.IconButton(
                                    icon="close", 
                                    icon_color="black",
                                    on_click=lambda _: self.hide_modal()
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            
                            ft.Divider(),
                            
                            ft.Container(
                                content=ft.Column([]),
                                expand=True
                            )
                        ])
                    ),
                    elevation=15
                ),
                alignment=ft.alignment.center
            )
        ])
        
        self.modal_overlay.visible = False
        
        main_stack = ft.Stack([
            ft.Column([
                header_section,
                results_section
            ], expand=True),
            
            self.modal_overlay
        ])
        
        view.controls.append(main_stack)
    
    def algorithm_changed(self, _):
        self.search_algorithm = list(self.algorithm_toggle.selected)[0]
    
    def top_matches_changed(self, e):
        self.top_matches = int(self.top_matches_dropdown.value)
    
    def search_cvs(self, _):
        if not self.keyword_input.value or not self.keyword_input.value.strip():
            self.show_error_snackbar("Please enter keywords to search.")
            return
        
        self.search_button.text = "Searching..."
        self.search_button.disabled = True
        self.summary_section.value = "Searching CVs... Please wait."
        self.summary_section.update()
        self.search_button.update()
        
        self.results_container.controls.clear()
        self.pagination_container.controls.clear()
        self.pagination_container.visible = False
        self.pagination_container.update()
        self.results_container.update()
        
        try:
            print(f"Searching with: algorithm={self.search_algorithm}, keywords={self.keyword_input.value}, n={self.top_matches}")
            
            search_results = find_top_n_cv(
                n=self.top_matches,
                algorithm=self.search_algorithm,
                keyword=self.keyword_input.value
            )
            
            print(f"Search results: {search_results}")
            
            total_cv = search_results.get('total_cv', 0)
            exact_time = search_results.get('exact_execution_time', 0)
            fuzzy_time = search_results.get('fuzzy_execution_time', 0)
            top_n_results = search_results.get('top_n', [])
            
            self.all_results = top_n_results
            self.current_page = 1
            
            self.summary_section.value = (
                f"Search completed! Found {len(top_n_results)} matching CVs from {total_cv} total CVs. "
                f"Exact match: {exact_time:.3f}s, Fuzzy match: {fuzzy_time:.3f}s"
            )
            
            if top_n_results:
                self.update_pagination()
                self.display_current_page()
                self.show_success_snackbar(f"Found {len(top_n_results)} matching CVs!")
            else:
                self.create_no_results_card()
                self.show_info_snackbar("No matching CVs found. Try different keywords.")
                
        except Exception as ex:
            print(f"Search error: {str(ex)}")
            self.summary_section.value = f"Error occurred during search: {str(ex)}"
            self.create_error_card(str(ex))
            self.show_error_snackbar("Search failed. Please try again.")
        
        finally:
            self.search_button.text = "Search CVs"
            self.search_button.disabled = False
            self.search_button.update()
            self.summary_section.update()
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
            on_click=self.go_to_prev_page,
            disabled=self.current_page == 1
        )
        
        next_button = ft.IconButton(
            icon="chevron_right",
            tooltip="Next page",
            on_click=self.go_to_next_page,
            disabled=self.current_page == total_pages
        )
        
        page_info = ft.Text(f"Page {self.current_page} of {total_pages}")
        
        self.pagination_container.controls.extend([
            prev_button,
            page_info,
            next_button
        ])
        
        self.pagination_container.update()
    
    def go_to_prev_page(self, _):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination()
    
    def go_to_next_page(self, _):
        total_pages = math.ceil(len(self.all_results) / self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination()
    
    def display_current_page(self):
        self.results_container.controls.clear()
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_results))
        
        current_page_results = self.all_results[start_idx:end_idx]
        
        for i, result in enumerate(current_page_results):
            rank = start_idx + i + 1
            self.create_result_card(result, rank)
        
        self.results_container.update()
    
    def create_result_card(self, result, rank):
        first_name = result.get('first_name', 'N/A')
        last_name = result.get('last_name', 'N/A')
        application_role = result.get('application_role', 'N/A')
        total_matches = result.get('total', 0)
        keyword_results = result.get('result', [])
        cv_path = result.get('cv_path', '')
        
        keywords = [k.strip() for k in self.keyword_input.value.split(',')]
        keyword_matches = []
        for i, count in enumerate(keyword_results):
            if i < len(keywords) and count > 0:
                keyword_name = keywords[i]
                keyword_matches.append(f"• {keyword_name}: {count} matches")
        
        keyword_controls = [ft.Text("Keywords:", weight="bold", size=14, color="#333333")]
        
        if keyword_matches:
            for match in keyword_matches[:4]:
                keyword_controls.append(ft.Text(match, size=13, color="#555555"))
            
            if len(keyword_matches) > 4:
                keyword_controls.append(
                    ft.Text(f"... and {len(keyword_matches) - 4} more", size=12, color="#777777")
                )
        else:
            keyword_controls.append(
                ft.Text("No keyword matches", size=13, italic=True, color="#777777")
            )
        
        card_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"#{rank}", size=18, weight="bold", color="white"),
                        bgcolor="#333333",
                        border_radius=20,
                        width=45,
                        height=45,
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text(f"{first_name} {last_name}", weight="bold", size=18),
                        ft.Text(f"Applied for: {application_role}", size=14, color="#666666"),
                    ], spacing=5, expand=True),
                    ft.Container(
                        content=ft.Text(f"{total_matches}", size=16, weight="bold", color="white"),
                        bgcolor="#555555",
                        border_radius=12,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6)
                    )
                ], spacing=15),
                ft.Divider(height=10),
                ft.Column(keyword_controls, spacing=4),
                ft.Divider(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        "View Summary",
                        icon="info",
                        bgcolor="#333333",
                        color="white",
                        on_click=lambda _, res=result: self.show_candidate_summary_modal(res),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=14))
                    ),
                    ft.Container(width=15),
                    ft.ElevatedButton(
                        "Open CV File",
                        icon="open_in_new",
                        bgcolor="#666666",
                        color="white",
                        on_click=lambda _, path=cv_path, name=f"{first_name} {last_name}": self.open_cv_file(path, name),
                        disabled=not cv_path,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=14))
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=12),
            padding=20,
            border_radius=12,
            bgcolor="#ffffff",
            border=ft.border.all(1, "#cccccc")
        )
        
        card = ft.Card(
            content=card_container,
            elevation=3,
            margin=ft.margin.only(bottom=12)
        )
        
        self.results_container.controls.append(card)
    
    def open_cv_file(self, cv_path, candidate_name):
        try:
            if not cv_path:
                self.show_error_snackbar("No CV file path available.")
                return
            
            if cv_path.startswith('../'):
                current_dir = os.path.dirname(os.path.abspath(__file__)) 
                project_root = os.path.dirname(os.path.dirname(current_dir))
                absolute_path = os.path.join(project_root, cv_path.replace('../', ''))
            else:
                absolute_path = os.path.abspath(cv_path)
            
            absolute_path = os.path.normpath(absolute_path)
            
            print(f"Original path: {cv_path}")
            print(f"Absolute path: {absolute_path}")
            print(f"File exists: {os.path.exists(absolute_path)}")
            
            if not os.path.exists(absolute_path):
                self.show_error_snackbar(f"CV file not found: {os.path.basename(cv_path)}")
                return
            
            success = open_cv_details(absolute_path)
            
            if success:
                self.show_success_snackbar(f"Opening CV for {candidate_name}")
            else:
                self.show_error_snackbar(f"Failed to open CV file for {candidate_name}")
                
        except Exception as e:
            print(f"Error opening CV file: {e}")
            self.show_error_snackbar("Failed to open CV file.")
    
    def show_candidate_summary_modal(self, result_data):
        try:
            first_name = result_data.get('first_name', 'N/A')
            last_name = result_data.get('last_name', 'N/A')
            application_role = result_data.get('application_role', 'N/A')
            total_matches = result_data.get('total', 0)
            cv_summary = result_data.get('summary', 'Summary not available')
            keyword_results = result_data.get('result', [])
            
            keywords = [k.strip() for k in self.keyword_input.value.split(',')]
            keyword_matches = []
            for i, count in enumerate(keyword_results):
                if i < len(keywords) and count > 0:
                    keyword_name = keywords[i]
                    keyword_matches.append((keyword_name, count))
            
            modal_content = self.modal_overlay.controls[1].content.content.content.controls[2].content
            
            match_percentage = 0
            if keywords and len(keyword_matches) > 0:
                match_percentage = min(100, int((len(keyword_matches) / len(keywords)) * 100))
            
            modal_content.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"{first_name} {last_name}", 
                            size=24, 
                            weight="bold", 
                            color="#1a1a1a"
                        ),
                        ft.Text(
                            f"{application_role}", 
                            size=16, 
                            color="#666666"
                        ),
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(15),
                    bgcolor="#f5f5f5",
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Total Matches", size=12, color="#666666"),
                                ft.Row([
                                    ft.Icon(name="star", color="#333333", size=18),
                                    ft.Text(
                                        f"{total_matches}", 
                                        size=20, 
                                        weight="bold", 
                                        color="#333333"
                                    )
                                ], spacing=5)
                            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                            border_radius=8,
                            bgcolor="#f0f0f0",
                            expand=1,
                            height=70,
                            alignment=ft.alignment.center
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Match Rate", size=12, color="#666666"),
                                ft.Row([
                                    ft.Icon(name="percent", color="#444444", size=18),
                                    ft.Text(
                                        f"{match_percentage}%", 
                                        size=20, 
                                        weight="bold", 
                                        color="#444444"
                                    )
                                ], spacing=5)
                            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                            border_radius=8,
                            bgcolor="#eeeeee",
                            expand=1,
                            height=70,
                            alignment=ft.alignment.center
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Keywords", size=12, color="#666666"),
                                ft.Row([
                                    ft.Icon(name="tag", color="#555555", size=18),
                                    ft.Text(
                                        f"{len(keyword_matches)}/{len(keywords)}", 
                                        size=20, 
                                        weight="bold", 
                                        color="#555555"
                                    )
                                ], spacing=5)
                            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                            border_radius=8,
                            bgcolor="#ececec",
                            expand=1,
                            height=70,
                            alignment=ft.alignment.center
                        ),
                    ], spacing=10),
                    margin=ft.margin.only(bottom=20)
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="search", color="#333333", size=18),
                            ft.Text(
                                "Keyword Matches", 
                                size=16, 
                                weight="bold", 
                                color="#333333"
                            )
                        ], spacing=8),
                        
                        ft.Divider(height=1, color="#cccccc"),
                        
                        ft.GridView(
                            runs_count=2,
                            max_extent=200,
                            child_aspect_ratio=3.0,
                            spacing=5,
                            run_spacing=5,
                            padding=5,
                            controls=[
                                self._create_keyword_chip(keyword, count, total_matches)
                                for keyword, count in keyword_matches
                            ] if keyword_matches else [
                                ft.Container(
                                    content=ft.Text(
                                        "No specific keyword matches found", 
                                        size=14, 
                                        italic=True, 
                                        color="#777777"
                                    ),
                                    padding=10
                                )
                            ]
                        )
                    ], spacing=10),
                    padding=15,
                    bgcolor="#f5f5f5",
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="description", color="#444444", size=18),
                            ft.Text(
                                "CV Summary", 
                                size=16, 
                                weight="bold", 
                                color="#444444"
                            )
                        ], spacing=8),
                        
                        ft.Divider(height=1, color="#cccccc"),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    cv_summary if cv_summary and cv_summary.strip() and cv_summary != 'Summary not available' 
                                    else "No detailed summary available for this CV.",
                                    size=14,
                                    selectable=True,
                                    color="#333333"
                                )
                            ], scroll=ft.ScrollMode.AUTO),
                            height=500,
                            padding=10,
                            bgcolor="#ffffff",
                            border_radius=8,
                            border=ft.border.all(1, "#cccccc"),
                        )
                    ], spacing=10),
                    padding=15,
                    bgcolor="#f8f8f8",
                    border_radius=12,
                    margin=ft.margin.only(bottom=20)
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.OutlinedButton(
                            "Close",
                            icon="close",
                            on_click=lambda _: self.hide_modal(),
                            style=ft.ButtonStyle(
                                color="#666666",
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.END),
                    margin=ft.margin.only(top=15)
                )
            ]
            self.modal_overlay.visible = True
            self.page.update()
            
        except Exception as e:
            print(f"Error showing candidate summary modal: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_snackbar("Failed to load candidate summary.")
    
    def _create_keyword_chip(self, keyword, count, total_matches):
        strength = min(5, max(1, int((count / max(1, total_matches)) * 5)))
        
        colors = {
            1: "#f0f0f0",
            2: "#e0e0e0",
            3: "#d0d0d0",
            4: "#c0c0c0",
            5: "#b0b0b0"
        }
        text_colors = {
            1: "#666666",
            2: "#555555",
            3: "#444444",
            4: "#333333",
            5: "#222222"
        }
        
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    keyword,
                    size=13,
                    weight="w500",
                    color=text_colors[strength]
                ),
                ft.Container(
                    content=ft.Text(
                        str(count),
                        size=12,
                        weight="bold",
                        color=text_colors[strength]
                    ),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2)
                )
            ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=colors[strength],
            border_radius=15,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            height=32
        )
    
    def hide_modal(self):
        self.modal_overlay.visible = False
        self.page.update()
    
    def view_cv_details(self, result):
        cv_path = result.get('cv_path', '')
        summary = result.get('summary', '')
        first_name = result.get('first_name', '')
        last_name = result.get('last_name', '')
        
        if cv_path:
            try:
                if cv_path.startswith('../'):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(current_dir))
                    absolute_path = os.path.join(project_root, cv_path.replace('../', ''))
                    absolute_path = os.path.normpath(absolute_path)
                else:
                    absolute_path = os.path.abspath(cv_path)
                
                from utils.pdf_extractor import extract_cv_information, extract_text_from_pdf
                full_text = extract_text_from_pdf(absolute_path)
                formatted_cv = extract_cv_information(full_text)
            except Exception as e:
                print(f"Error extracting PDF: {e}")
                formatted_cv = summary
        else:
            formatted_cv = summary
        
        modal_content = self.modal_overlay.controls[1].content.content.content.controls[2].content
        
        modal_content.controls = [
            ft.Text(f"CV Details - {first_name} {last_name}", size=16, weight="bold"),
            ft.Text(f"CV Path: {cv_path}", size=12, color="#666666"),
            ft.Divider(),
            ft.Text("Complete CV Information:", weight="bold", size=14),            
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        formatted_cv if formatted_cv else "No CV details available for this applicant.",
                        selectable=True, 
                        size=11
                    )
                ], scroll=ft.ScrollMode.AUTO),
                bgcolor="#f5f5f5",
                padding=15,
                border_radius=8,
                height=350,
            ),
            
            ft.Container(
                content=ft.ElevatedButton(
                    text="Close",
                    on_click=lambda _: self.hide_modal(),
                    style=ft.ButtonStyle(
                        bgcolor="#cccccc",
                        color="#1a1a1a"
                    ),
                    width=100
                ),
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(top=15)
            )
        ]
        
        self.modal_overlay.visible = True
        self.page.update()
    
    def create_no_results_card(self):
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
    
    def create_error_card(self, error_message):
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
    
    def show_success_snackbar(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#555555")
                )
            else:
                print(f"SUCCESS: {message}")
        except Exception as _:
            print(f"SUCCESS: {message}")
    
    def show_error_snackbar(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#333333")
                )
            else:
                print(f"ERROR: {message}")
        except Exception as _:
            print(f"ERROR: {message}")
    
    def show_info_snackbar(self, message):
        try:
            if hasattr(self.page, 'show_snack_bar'):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message, size=14), bgcolor="#666666")
                )
            else:
                print(f"INFO: {message}")
        except Exception as _:
            print(f"INFO: {message}")