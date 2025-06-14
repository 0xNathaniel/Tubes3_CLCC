import flet as ft
from utils.find_top_n_cv_encrypted import find_top_n_cv

from ui.search_form import SearchForm
from ui.result_list import ResultList
from ui.candidate_modal import CandidateModal
from ui.utils.snackbar_manager import SnackbarManager

class HomePage:
    def __init__(self):
        self.page = None
        self.search_algorithm = "kmp"
        self.top_matches = 5
        self.all_results = []
        self.keyword_input = None
        
    def build(self, view, page):
        self.page = page
        self.snackbar_manager = SnackbarManager(page)
        
        title = ft.Text("CLCC ATS Friendly CV Scanner", size=32, weight="bold", color="#1a1a1a")
        subtitle = ft.Text("String matching using KMP, Boyer-Moore, and Aho-Corasick algorithms", 
                        size=18, italic=True, color="#4a4a4a")
        
        self.search_form = SearchForm(
            on_search=self.search_cvs,
            on_algorithm_changed=self.algorithm_changed,
            on_top_matches_changed=self.top_matches_changed
        )
        
        self.result_list = ResultList(
            on_view_summary=self.show_candidate_summary_modal,
            on_open_cv=self.open_cv_file
        )
        
        self.candidate_modal = CandidateModal(
            on_close=self.hide_modal
        )
        
        search_form_ui = self.search_form.build()
        self.keyword_input = self.search_form.keyword_input
        self.summary_section = ft.Text("", size=16, color="#555555", weight="w500")
        
        header_section = ft.Container(
            content=ft.Column([
                title,
                subtitle,
                ft.Divider(height=30, color="transparent"),
                search_form_ui,
                ft.Divider(height=15, color="transparent"),
                self.summary_section,
            ]),
            padding=30,
            bgcolor="#f5f5f5",
            border_radius=15,
            margin=ft.margin.only(bottom=20)
        )
        
        results_section = self.result_list.build()
        
        self.modal_overlay = self.candidate_modal.build()
        self.modal_overlay.visible = False
        
        main_stack = ft.Stack([
            ft.Column([
                header_section,
                results_section
            ], expand=True),
            self.modal_overlay
        ])
        
        view.controls.append(main_stack)
    
    def algorithm_changed(self, algorithm):
        self.search_algorithm = algorithm
    
    def top_matches_changed(self, top_n):
        self.top_matches = top_n
    
    def search_cvs(self, _):
        if not self.keyword_input.value or not self.keyword_input.value.strip():
            self.snackbar_manager.show_error("Please enter keywords to search.")
            return

        self.search_form.set_searching_state(True)
        self.summary_section.value = "Searching CVs... Please wait."
        self.summary_section.update()
        
        self.result_list.clear()
        
        try:
            print(f"Searching with: algorithm={self.search_algorithm}, keywords={self.keyword_input.value}, n={self.top_matches}")
            
            search_results = find_top_n_cv(
                n=self.top_matches,
                algorithm=self.search_algorithm,
                keyword=self.keyword_input.value
            )
            
            total_cv = search_results.get('total_cv', 0)
            exact_time = search_results.get('exact_execution_time', 0)
            fuzzy_time = search_results.get('fuzzy_execution_time', 0)
            top_n_results = search_results.get('top_n', [])
            
            self.all_results = top_n_results
            
            self.summary_section.value = (
                f"Search completed! Found {len(top_n_results)} matching CVs from {total_cv} total CVs. "
                f"Exact match: {exact_time:.3f}s, Fuzzy match: {fuzzy_time:.3f}s"
            )
            
            if top_n_results:
                self.result_list.display_results(top_n_results, self.keyword_input.value)
                self.snackbar_manager.show_success(f"Found {len(top_n_results)} matching CVs!")
            else:
                self.result_list.show_no_results()
                self.snackbar_manager.show_info("No matching CVs found. Try different keywords.")
                
        except Exception as ex:
            print(f"Search error: {str(ex)}")
            self.summary_section.value = f"Error occurred during search: {str(ex)}"
            self.result_list.show_error(str(ex))
            self.snackbar_manager.show_error("Search failed. Please try again.")
        
        finally:
            self.search_form.set_searching_state(False)
            self.summary_section.update()
    
    def show_candidate_summary_modal(self, result_data):
        try:
            self.candidate_modal.update_content(result_data, self.keyword_input.value)
            self.modal_overlay.visible = True
            self.page.update()
        except Exception as e:
            print(f"Error showing candidate summary modal: {e}")
            import traceback
            traceback.print_exc()
            self.snackbar_manager.show_error("Failed to load candidate summary.")
    
    def hide_modal(self):
        self.modal_overlay.visible = False
        self.page.update()
    
    def open_cv_file(self, cv_path, candidate_name):
        try:
            from utils.open_cv_details import open_cv_details
            import os
            
            if not cv_path:
                self.snackbar_manager.show_error("No CV file path available.")
                return
            
            if cv_path.startswith('../'):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                absolute_path = os.path.join(project_root, cv_path.replace('../', ''))
            else:
                absolute_path = os.path.abspath(cv_path)
            
            absolute_path = os.path.normpath(absolute_path)
            
            if not os.path.exists(absolute_path):
                self.snackbar_manager.show_error(f"CV file not found: {os.path.basename(cv_path)}")
                return
            
            success = open_cv_details(absolute_path)
            
            if success:
                self.snackbar_manager.show_success(f"Opening CV for {candidate_name}")
            else:
                self.snackbar_manager.show_error(f"Failed to open CV file for {candidate_name}")
                
        except Exception as e:
            print(f"Error opening CV file: {e}")
            self.snackbar_manager.show_error("Failed to open CV file.")