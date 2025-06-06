import flet as ft
from utils.find_top_n_cv import find_top_n_cv

class HomePage:
    def __init__(self):
        self.search_algorithm = "kmp"  
        self.top_matches = 5
        self.page = None
        
    def build(self, page):
        self.page = page
        
        title = ft.Text("CV ATS - Applicant Tracking System", size=28, weight="bold", color="#0d47a1")
        subtitle = ft.Text("Find the best candidates using advanced string matching algorithms", size=16, italic=True)
        
        self.keyword_input = ft.TextField(
            label="Enter keywords (separated by comma)",
            hint_text="e.g. Python, React, SQL, nursing, accounting",
            width=700,
            border_radius=10
        )
        
        algorithm_text = ft.Text("Select Search Algorithm:", weight="bold")
        self.algorithm_toggle = ft.SegmentedButton(
            width=450,
            selected={self.search_algorithm},
            segments=[
                ft.Segment(value="kmp", label=ft.Text("KMP Algorithm")),
                ft.Segment(value="boyer_moore", label=ft.Text("Boyer-Moore")),
                ft.Segment(value="aho_corasick", label=ft.Text("Aho-Corasick")),
            ],
            on_change=self.algorithm_changed
        )
        
        top_matches_text = ft.Text("Number of Results:", weight="bold")
        self.top_matches_dropdown = ft.Dropdown(
            width=120,
            options=[
                ft.dropdown.Option(text="5", key="5"),
                ft.dropdown.Option(text="10", key="10"),
                ft.dropdown.Option(text="15", key="15"),
                ft.dropdown.Option(text="20", key="20"),
            ],
            value="5",
            border_radius=10,
            on_change=self.top_matches_changed
        )
        
        self.search_button = ft.ElevatedButton(
            text="Search CVs",
            icon="search",
            width=150,
            height=40,
            bgcolor="#1976d2",
            color="white",
            on_click=self.search_cvs
        )
        
        self.summary_section = ft.Text("", size=14, color="#757575")
        
        self.results_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=500,
            spacing=15
        )
        
        algorithm_row = ft.Row([algorithm_text, self.algorithm_toggle], spacing=20)
        top_matches_row = ft.Row([top_matches_text, self.top_matches_dropdown], spacing=20)
        controls_row = ft.Row(
            [algorithm_row, top_matches_row, self.search_button], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True
        )
        
        page.controls.extend([
            ft.Container(
                content=ft.Column([
                    title,
                    subtitle,
                    ft.Divider(height=20, color="transparent"),
                    self.keyword_input,
                    ft.Divider(height=10, color="transparent"),
                    controls_row,
                    ft.Divider(height=10, color="transparent"),
                    self.summary_section,
                ]),
                padding=20,
                bgcolor="#e3f2fd",
                border_radius=15
            ),
            ft.Divider(),
            ft.Text("Search Results", size=20, weight="bold"),
            self.results_container
        ])
    
    def get_page(self):
        return self.page
    
    def algorithm_changed(self, e):
        self.search_algorithm = list(self.algorithm_toggle.selected)[0]
        print(f"Algorithm changed to: {self.search_algorithm}")
    
    def top_matches_changed(self, e):
        self.top_matches = int(self.top_matches_dropdown.value)
        print(f"Top matches changed to: {self.top_matches}")
    
    def search_cvs(self, e):
        if not self.keyword_input.value or not self.keyword_input.value.strip():
            self.show_error_snackbar("Please enter keywords to search.")
            return
        
        self.search_button.text = "Searching..."
        self.search_button.disabled = True
        self.summary_section.value = "Searching CVs... Please wait."
        self.summary_section.update()
        self.search_button.update()
        
        self.results_container.controls.clear()
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
            
            self.summary_section.value = (
                f"Search completed! Found {len(top_n_results)} matching CVs from {total_cv} total CVs. "
                f"Exact match: {exact_time:.3f}s, Fuzzy match: {fuzzy_time:.3f}s"
            )
            
            self.current_search_results = search_results
            
            if top_n_results:
                for i, result in enumerate(top_n_results):
                    self.create_result_card(result, i + 1)
                    
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
            # Reset button state
            self.search_button.text = "Search CVs"
            self.search_button.disabled = False
            self.search_button.update()
            self.summary_section.update()
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
        
        # Create card content
        header = ft.Row([
            ft.Container(
                content=ft.Text(f"#{rank}", size=18, weight="bold", color="white"),
                bgcolor="#1976d2",
                border_radius=20,
                width=40,
                height=40,
                alignment=ft.alignment.center
            ),
            ft.Column([
                ft.Text(f"{first_name} {last_name}", weight="bold", size=18),
                ft.Text(f"Applied for: {application_role}", size=14, color="#757575"),
            ], spacing=2)
        ], spacing=15)
        
        matches_info = ft.Container(
            content=ft.Text(f"Total Matches: {total_matches}", size=16, weight="bold"),
            bgcolor="#c8e6c9",
            padding=10,
            border_radius=8
        )
        
        keyword_section = ft.Column([
            ft.Text("Keyword Matches:", weight="bold", size=14),
        ])
        
        if keyword_matches:
            for match in keyword_matches:
                keyword_section.controls.append(
                    ft.Text(match, size=13, color="#1565c0")
                )
        else:
            keyword_section.controls.append(
                ft.Text("No specific keyword matches found", size=13, italic=True)
            )
        
        buttons_row = ft.Row([
            ft.ElevatedButton(
                text="View Summary",
                icon="summarize",
                bgcolor="#4caf50",
                color="white",
                on_click=lambda e, res=result: self.show_summary_popup(res)
            ),
            ft.ElevatedButton(
                text="View CV Details",
                icon="description",
                bgcolor="#ff9800",
                color="white",
                on_click=lambda e, res=result: self.view_cv_details(res),
                disabled=not cv_path
            )
        ], spacing=10)
        
        card_content = ft.Column([
            header,
            ft.Divider(),
            matches_info,
            keyword_section,
            ft.Divider(),
            buttons_row
        ], spacing=10)
        
        card = ft.Card(
            content=ft.Container(
                content=card_content,
                padding=20
            ),
            elevation=5
        )
        
        self.results_container.controls.append(card)
    
    def create_no_results_card(self):
        no_results_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🔍", size=50),
                    ft.Text("No matching CVs found", weight="bold", size=18),
                    ft.Text("Try different keywords or check your search criteria.", size=14),
                    ft.Text("Suggestions:", weight="bold", size=14),
                    ft.Text("• Use more common job-related terms", size=12),
                    ft.Text("• Try broader skill categories", size=12),
                    ft.Text("• Check for typos in keywords", size=12),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            ),
            elevation=2
        )
        self.results_container.controls.append(no_results_card)
    
    def create_error_card(self, error_message):
        error_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("❌", size=50),
                    ft.Text("Search Error", weight="bold", size=18, color="#d32f2f"),
                    ft.Text(f"Error: {error_message}", size=14, color="#c62828")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30
            ),
            elevation=2
        )
        self.results_container.controls.append(error_card)
    
    def show_summary_popup(self, result_data):
        try:
            first_name = result_data.get('first_name', 'N/A')
            last_name = result_data.get('last_name', 'N/A')
            application_role = result_data.get('application_role', 'N/A')
            total_matches = result_data.get('total', 0)
            cv_summary = result_data.get('summary', 'Summary not available')
            cv_path = result_data.get('cv_path', '')
            
            print(f"Opening summary popup for: {first_name} {last_name}")
            print(f"Summary content: {cv_summary}")
            
            summary_content = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Personal Information", size=16, weight="bold", color="#1565c0"),
                        ft.Text(f"Full Name: {first_name} {last_name}", size=14),
                        ft.Text(f"Position Applied: {application_role}", size=14),
                        ft.Text(f"Total Matches: {total_matches}", size=14, color="#4caf50"),
                    ]),
                    padding=10,
                    bgcolor="#f8f9fa",
                    border_radius=8,
                    margin=ft.margin.only(bottom=10)
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("CV Summary", size=16, weight="bold", color="#f57c00"),
                        ft.Container(
                            content=ft.Text(
                                cv_summary if cv_summary and cv_summary.strip() else "No summary available for this CV.",
                                size=12,
                                selectable=True
                            ),
                            padding=10,
                            bgcolor="#ffffff",
                            border_radius=5,
                            border=ft.border.all(1, "#e0e0e0"),
                            height=200
                        ),
                    ]),
                    padding=10,
                    bgcolor="#fff3e0",
                    border_radius=8,
                    margin=ft.margin.only(bottom=10)
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("CV File Information", size=16, weight="bold", color="#388e3c"),
                        ft.Text(f"CV Status: {'Available' if cv_path else 'Not Available'}", size=14),
                        ft.Text(f"File Path: {cv_path if cv_path else 'N/A'}", size=12, selectable=True) if cv_path else ft.Container(),
                    ]),
                    padding=10,
                    bgcolor="#e8f5e8",
                    border_radius=8
                ),
                
            ], scroll=ft.ScrollMode.AUTO, spacing=0)
            
            # Create dialog
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Summary - {first_name} {last_name}", size=18, weight="bold"),
                content=ft.Container(
                    content=summary_content,
                    width=600,
                    height=450
                ),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda e: self.close_dialog()
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page = self.get_page()
            page.dialog = dialog
            dialog.open = True
            page.update()
            print("Summary popup opened successfully")
            
        except Exception as e:
            print(f"Error opening summary popup: {e}")
            self.show_error_dialog(f"Failed to open summary: {str(e)}")
    
    def show_error_dialog(self, message):
        """Show error dialog"""
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error", color="#d32f2f"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.close_dialog())
            ],
        )
        
        page = self.get_page()
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()
    
    def view_cv_details(self, result):
        """View detailed CV information"""
        cv_path = result.get('cv_path', '')
        summary = result.get('summary', '')
        first_name = result.get('first_name', '')
        last_name = result.get('last_name', '')
        
        if cv_path and summary:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"CV Details - {first_name} {last_name}"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"CV Path: {cv_path}", size=12, color="#757575"),
                        ft.Divider(),
                        ft.Text("CV Summary:", weight="bold"),
                        ft.Container(
                            content=ft.Text(summary, selectable=True, size=12),
                            bgcolor="#f5f5f5",
                            padding=10,
                            border_radius=5,
                            height=350
                        )
                    ], scroll=ft.ScrollMode.AUTO),
                    width=700,
                    height=500,
                    padding=10
                ),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        else:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("CV Information"),
                content=ft.Text("No CV details available for this applicant."),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        
        page = self.get_page()
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def close_dialog(self):
        """Close the current dialog"""
        try:
            page = self.get_page()
            if page and hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
                page.dialog = None
                page.update()
                print("Dialog closed successfully")
        except Exception as e:
            print(f"Error closing dialog: {e}")
    
    def show_success_snackbar(self, message):
        try:
            page = self.get_page()
            if hasattr(page, 'show_snack_bar'):
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message), bgcolor="#4caf50")
                )
            else:
                print(f"SUCCESS: {message}")
        except Exception as e:
            print(f"SUCCESS: {message}")
    
    def show_error_snackbar(self, message):
        try:
            page = self.get_page()
            if hasattr(page, 'show_snack_bar'):
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message), bgcolor="#f44336")
                )
            else:
                print(f"ERROR: {message}")
        except Exception as e:
            print(f"ERROR: {message}")
    
    def show_info_snackbar(self, message):
        try:
            page = self.get_page()
            if hasattr(page, 'show_snack_bar'):
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message), bgcolor="#2196f3")
                )
            else:
                print(f"INFO: {message}")
        except Exception as e:
            print(f"INFO: {message}")