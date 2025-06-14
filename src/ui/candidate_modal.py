import flet as ft

class CandidateModal:
    def __init__(self, on_close):
        self.on_close = on_close
        self.content_container = None
    
    def build(self):
        self.content_container = ft.Column([])
        
        return ft.Stack([
            ft.Container(
                expand=True,
                bgcolor="rgba(0,0,0,0.5)", 
                on_click=lambda _: self.on_close()
            ),
            
            # Modal content
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
                                    on_click=lambda _: self.on_close()
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            
                            ft.Divider(),
                            
                            # Content container that will be populated with candidate details
                            ft.Container(
                                content=self.content_container, 
                                expand=True
                            )
                        ])
                    ),
                    elevation=15
                ),
                alignment=ft.alignment.center
            )
        ])

    def update_content(self, result_data, keywords_string):
        first_name = result_data.get('first_name', 'N/A')
        last_name = result_data.get('last_name', 'N/A')
        application_role = result_data.get('application_role', 'N/A')
        total_matches = result_data.get('total', 0)
        cv_summary = result_data.get('summary', 'Summary not available')
        keyword_results = result_data.get('result', [])
        
        keywords = [k.strip() for k in keywords_string.split(',')]
        keyword_matches = []
        for i, count in enumerate(keyword_results):
            if i < len(keywords) and count > 0:
                keyword_name = keywords[i]
                keyword_matches.append((keyword_name, count))
        
        match_percentage = 0
        if keywords and len(keyword_matches) > 0:
            match_percentage = min(100, int((len(keyword_matches) / len(keywords)) * 100))
        
        self.content_container.controls = [
            self._create_candidate_header(first_name, last_name, application_role),
            self._create_stats_row(total_matches, match_percentage, len(keyword_matches), len(keywords)),
            self._create_keyword_matches_section(keyword_matches),
            self._create_cv_summary_section(cv_summary),
            self._create_footer()
        ]
    
    def _create_candidate_header(self, first_name, last_name, application_role):
        return ft.Container(
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
        )
    
    def _create_stats_row(self, total_matches, match_percentage, matched_keywords, total_keywords):
        return ft.Container(
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
                                f"{matched_keywords}/{total_keywords}", 
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
        )
    
    def _create_keyword_matches_section(self, keyword_matches):
        return ft.Container(
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
                        self._create_keyword_chip(keyword, count)
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
        )
    
    def _create_keyword_chip(self, keyword, count):
        """Create a keyword chip showing match count"""
        # Calculate strength for visual indication of relevance
        strength = min(5, max(1, int((count / max(1, count * 2)) * 5)))
        
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
    
    def _create_cv_summary_section(self, cv_summary):
        return ft.Container(
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
        )
    
    def _create_footer(self):
        return ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    "Close",
                    icon="close",
                    on_click=lambda _: self.on_close(),
                    style=ft.ButtonStyle(
                        color="#666666",
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                ),
            ], spacing=10, alignment=ft.MainAxisAlignment.END),
            margin=ft.margin.only(top=15)
        )