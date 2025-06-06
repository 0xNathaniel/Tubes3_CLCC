import flet as ft

class SummaryPage:
    def __init__(self):
        pass
    
    def build(self, page, application_id=None):
        # Title
        title = ft.Text("Applicant Summary", size=24, weight="bold")
        
        # Back button
        back_button = ft.ElevatedButton(
            text="Back to Search",
            icon="arrow_back",
            on_click=lambda e: page.go("/")
        )
        
        # Container for applicant data
        applicant_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
        
        # Sample content for UI preview - to be replaced with real data later
        
        # Personal information section
        personal_info = ft.Container(
            content=ft.Column([
                ft.Text("Personal Information", size=20, weight="bold"),
                ft.Text("Name: John Doe", size=16),
                ft.Text("Email: john.doe@example.com", size=16),
                ft.Text("Phone: 123-456-7890", size=16),
                ft.Text("Address: 123 Main St, Anytown", size=16),
                ft.Text("Position Applied: Software Developer", size=16),
                ft.Text("Application Date: 2025-05-01", size=16),
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        # Summary section
        summary = ft.Container(
            content=ft.Column([
                ft.Text("Summary", size=20, weight="bold"),
                ft.Text("Experienced software developer with expertise in Python, React, and SQL. "
                        "5+ years of experience in building web applications and data pipelines.",
                        size=16),
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        # Skills section
        skills_column = ft.Column([
            ft.Text("Skills", size=20, weight="bold"),
            ft.Text("• Python", size=16),
            ft.Text("• React", size=16),
            ft.Text("• SQL", size=16),
            ft.Text("• Git", size=16),
            ft.Text("• Docker", size=16),
        ])
        
        skills = ft.Container(
            content=skills_column,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        # Work experience section
        work_exp_column = ft.Column([
            ft.Text("Work Experience", size=20, weight="bold"),
            ft.Text("Senior Developer at TechCorp", size=16, weight="bold"),
            ft.Text("Period: Jan 2022 - Present", size=16),
            ft.Divider(),
            ft.Text("Developer at WebSolutions", size=16, weight="bold"),
            ft.Text("Period: Mar 2018 - Dec 2021", size=16),
        ])
        
        work_experience = ft.Container(
            content=work_exp_column,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        # Education section
        education_column = ft.Column([
            ft.Text("Education", size=20, weight="bold"),
            ft.Text("BS in Computer Science - Example University", size=16, weight="bold"),
            ft.Text("Year: 2015-2019", size=16),
        ])
        
        education = ft.Container(
            content=education_column,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        # View CV button
        view_cv_button = ft.ElevatedButton(
            text="View Original CV",
            icon="description",
            on_click=self.view_cv
        )
        
        # Add all sections to applicant container
        applicant_container.controls.extend([
            personal_info,
            ft.Divider(),
            summary,
            ft.Divider(),
            skills,
            ft.Divider(),
            work_experience,
            ft.Divider(),
            education,
            ft.Divider(),
            view_cv_button
        ])
        
        # Change this part: instead of page.add, use page.controls.extend
        if isinstance(page, ft.View):
            # For View objects in routing
            page.controls.extend([
                title,
                back_button,
                ft.Divider(),
                applicant_container
            ])
        else:
            # For direct Page rendering
            page.add(
                title,
                back_button,
                ft.Divider(),
                applicant_container
            )
    
    def view_cv(self, e):
        # To be implemented - open CV file
        pass
    
    def load_applicant_data(self, application_id):
        # To be implemented - load real data based on application ID
        pass