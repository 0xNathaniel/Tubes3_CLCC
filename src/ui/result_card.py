import flet as ft

class ResultCard:
    def __init__(self, result, rank, keywords_string, on_view_summary, on_open_cv):
        self.result = result
        self.rank = rank
        self.keywords_string = keywords_string
        self.on_view_summary = on_view_summary
        self.on_open_cv = on_open_cv
        
    def build(self):
        first_name = self.result.get('first_name', 'N/A')
        last_name = self.result.get('last_name', 'N/A')
        application_role = self.result.get('application_role', 'N/A')
        total_matches = self.result.get('total', 0)
        keyword_results = self.result.get('result', [])
        cv_path = self.result.get('cv_path', '')
        
        keywords = [k.strip() for k in self.keywords_string.split(',')]
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
                        content=ft.Text(f"#{self.rank}", size=18, weight="bold", color="white"),
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
                        on_click=lambda _: self.on_view_summary(self.result),
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=14))
                    ),
                    ft.Container(width=15),
                    ft.ElevatedButton(
                        "Open CV File",
                        icon="open_in_new",
                        bgcolor="#666666",
                        color="white",
                        on_click=lambda _: self.on_open_cv(cv_path, f"{first_name} {last_name}"),
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
        
        return ft.Card(
            content=card_container,
            elevation=3,
            margin=ft.margin.only(bottom=12)
        )