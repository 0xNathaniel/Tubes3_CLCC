import os
import random
from datetime import datetime, timedelta
from faker import Faker
import glob

fake = Faker()
Faker.seed(42)

OUTPUT_FILE = "../database/seed_data.sql"
NUM_APPLICANTS = 200
BASE_CV_PATH = "../data/cv"
ACTUAL_CV_PATH = "c:/Users/kenne/TubesSTIMA3/data/cv"

ROLES = []
for item in os.listdir(ACTUAL_CV_PATH):
    if os.path.isdir(os.path.join(ACTUAL_CV_PATH, item)):
        ROLES.append(item)

# Cache untuk menyimpan PDF yang tersedia untuk setiap role
available_pdfs = {}
used_detail_ids = set() # prevent duplication

def generate_date_of_birth():
    today = datetime.now()
    max_age = 55
    min_age = 21
    days = random.randint(min_age * 365, max_age * 365)
    return (today - timedelta(days=days)).strftime('%Y-%m-%d')

def generate_phone_number():
    prefix = random.choice(['8', '81', '82', '83', '85', '87', '88', '89'])
    return f"{prefix}{random.randint(1000000, 9999999)}"

def get_available_pdfs_for_role(role):
    if role not in available_pdfs:
        pdf_path = os.path.join(ACTUAL_CV_PATH, role)
        if os.path.exists(pdf_path):
            pdfs = glob.glob(os.path.join(pdf_path, "*.pdf"))
            available_pdfs[role] = [os.path.basename(pdf) for pdf in pdfs]
        else:
            available_pdfs[role] = [f"placeholder_{i}.pdf" for i in range(1, 6)]
    
    return available_pdfs[role]

def create_sql_file():
    applicants = []
    applications = []
    
    for i in range(1, NUM_APPLICANTS + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = generate_date_of_birth()
        address = fake.address().replace('\n', ', ')
        phone = generate_phone_number()
        
        applicants.append({
            'applicant_id': i,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob,
            'address': address,
            'phone_number': phone
        })
    
    for i in range(1, NUM_APPLICANTS + 1):
        # 1-3 aplikasi per orang
        num_applications = random.randint(1, 3)
        used_roles = []
        
        for _ in range(num_applications):
            available_roles = [r for r in ROLES if r not in used_roles]
            if not available_roles:
                break
                
            role = random.choice(available_roles)
            used_roles.append(role)
            
            #dapetin PDF yang ada di path bnrn
            pdfs = get_available_pdfs_for_role(role)
            cv_filename = random.choice(pdfs)
            
            try:
                detail_id = int(cv_filename.split('.')[0])
                while detail_id in used_detail_ids:
                    detail_id = random.randint(10000000, 99999999)
                used_detail_ids.add(detail_id)
            except ValueError:
                detail_id = random.randint(10000000, 99999999)
                while detail_id in used_detail_ids:
                    detail_id = random.randint(10000000, 99999999)
                used_detail_ids.add(detail_id)
                
            cv_path = f"../data/cv/{role}/{cv_filename}"
            
            applications.append({
                'detail_id': detail_id,
                'applicant_id': i,
                'application_role': role,
                'cv_path': cv_path
            })
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write("-- Drop tables if they exist (to avoid errors)\n")
        f.write("DROP TABLE IF EXISTS ApplicationDetail;\n")
        f.write("DROP TABLE IF EXISTS ApplicantProfile;\n\n")
        
        f.write("-- Create ApplicantProfile table\n")
        f.write("CREATE TABLE ApplicantProfile (\n")
        f.write("    applicant_id INT NOT NULL PRIMARY KEY,\n")
        f.write("    first_name VARCHAR(50) DEFAULT NULL,\n")
        f.write("    last_name VARCHAR(50) DEFAULT NULL,\n")
        f.write("    date_of_birth DATE DEFAULT NULL,\n")
        f.write("    address VARCHAR(255) DEFAULT NULL,\n")
        f.write("    phone_number VARCHAR(20) DEFAULT NULL\n")
        f.write(");\n\n")
        
        f.write("-- Create ApplicationDetail table\n")
        f.write("CREATE TABLE ApplicationDetail (\n")
        f.write("    detail_id INT NOT NULL PRIMARY KEY,\n")
        f.write("    applicant_id INT NOT NULL,\n")
        f.write("    application_role VARCHAR(100) DEFAULT NULL,\n")
        f.write("    cv_path TEXT,\n")
        f.write("    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)\n")
        f.write(");\n\n")
        
        f.write("-- ApplicantProfile data\n")
        f.write("INSERT INTO ApplicantProfile (applicant_id, first_name, last_name, date_of_birth, address, phone_number) VALUES\n")
        
        for i, applicant in enumerate(applicants):
            f.write(f"({applicant['applicant_id']}, '{applicant['first_name']}', '{applicant['last_name']}', "
                   f"'{applicant['date_of_birth']}', '{applicant['address']}', '{applicant['phone_number']}')")
            
            if i < len(applicants) - 1:
                f.write(",\n")
            else:
                f.write(";\n\n")
        
        f.write("-- ApplicationDetail data\n")
        f.write("INSERT INTO ApplicationDetail (detail_id, applicant_id, application_role, cv_path) VALUES\n")
        
        for i, application in enumerate(applications):
            f.write(f"({application['detail_id']}, {application['applicant_id']}, "
                   f"'{application['application_role']}', '{application['cv_path']}')")
            
            if i < len(applications) - 1:
                f.write(",\n")
            else:
                f.write(";\n")
        
if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    create_sql_file()
    print(f"SQL data generated successfully in {OUTPUT_FILE}")
    print(f"mysql -u username -p database_name < {OUTPUT_FILE}")