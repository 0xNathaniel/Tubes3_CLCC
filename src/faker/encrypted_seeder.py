import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from utils.rsa import get_rsa_instance, encrypt_data

fake = Faker()
Faker.seed(42)

# Dapatkan path absolut folder script ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke folder project root (misal: .../Tubes3_CLCC)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Path output dan data
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "encrypted_data.sql")
NUM_APPLICANTS = 200
BASE_CV_PATH = os.path.join(PROJECT_ROOT, "data", "cv")
ACTUAL_CV_PATH = BASE_CV_PATH  # Gunakan path absolut ke folder cv

# Inisialisasi RSA (gunakan p dan q yang sama dengan dekripsi)
rsa_instance = get_rsa_instance()

ROLES = []
for item in os.listdir(ACTUAL_CV_PATH):
    if os.path.isdir(os.path.join(ACTUAL_CV_PATH, item)):
        ROLES.append(item)

available_pdfs = {}
used_detail_ids = set()

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

def format_encrypted(val):
    if isinstance(val, list):
        return ','.join(map(str, val))
    return val

def create_sql_file():
    applicants = []
    applications = []

    # Generate and encrypt applicant profile
    for i in range(1, NUM_APPLICANTS + 1):
        raw_applicant = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'date_of_birth': generate_date_of_birth(),
            'address': fake.address().replace('\n', ', '),
            'phone_number': generate_phone_number()
        }
        encrypted_applicant = encrypt_data(raw_applicant, rsa_instance)
        encrypted_applicant['applicant_id'] = i  # ID tidak dienkripsi
        applicants.append(encrypted_applicant)

    # Generate application detail (tidak dienkripsi)
    for i in range(1, NUM_APPLICANTS + 1):
        num_applications = random.randint(1, 3)
        used_roles = []
        for _ in range(num_applications):
            available_roles = [r for r in ROLES if r not in used_roles]
            if not available_roles:
                break
            role = random.choice(available_roles)
            used_roles.append(role)
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

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("-- Drop tables if they exist (to avoid errors)\n")
        f.write("DROP TABLE IF EXISTS ApplicationDetail;\n")
        f.write("DROP TABLE IF EXISTS ApplicantProfile;\n\n")

        f.write("-- Create ApplicantProfile table\n")
        f.write("CREATE TABLE ApplicantProfile (\n")
        f.write("    applicant_id INT NOT NULL PRIMARY KEY,\n")
        f.write("    first_name TEXT DEFAULT NULL,\n")
        f.write("    last_name TEXT DEFAULT NULL,\n")
        f.write("    date_of_birth TEXT DEFAULT NULL,\n")
        f.write("    address TEXT DEFAULT NULL,\n")
        f.write("    phone_number TEXT DEFAULT NULL\n")
        f.write(");\n\n")

        f.write("-- Create ApplicationDetail table\n")
        f.write("CREATE TABLE ApplicationDetail (\n")
        f.write("    detail_id INT NOT NULL PRIMARY KEY,\n")
        f.write("    applicant_id INT NOT NULL,\n")
        f.write("    application_role VARCHAR(100) DEFAULT NULL,\n")
        f.write("    cv_path TEXT,\n")
        f.write("    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)\n")
        f.write(");\n\n")

        f.write("-- ApplicantProfile data (encrypted)\n")
        f.write("INSERT INTO ApplicantProfile (applicant_id, first_name, last_name, date_of_birth, address, phone_number) VALUES\n")
        for i, applicant in enumerate(applicants):
            f.write(f"({applicant['applicant_id']}, "
                    f"'{format_encrypted(applicant['first_name'])}', "
                    f"'{format_encrypted(applicant['last_name'])}', "
                    f"'{format_encrypted(applicant['date_of_birth'])}', "
                    f"'{format_encrypted(applicant['address'])}', "
                    f"'{format_encrypted(applicant['phone_number'])}')")
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

        # Tambahkan instruksi dekripsi
        f.write("\n-- Decryption Instructions:\n")
        f.write("-- Use the following RSA keys to decrypt the data:\n")
        f.write(f"-- Public Key (n, e): {rsa_instance.public_key}\n")
        f.write(f"-- Private Key (n, d): {rsa_instance.private_key}\n")
        f.write("-- Encrypted fields are stored as comma-separated integers\n")
        f.write("-- Use the decrypt_data function from utils.rsa to decrypt\n")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    create_sql_file()
    print(f"SQL data generated successfully in {OUTPUT_FILE}")
    print(f"mysql -u username -p database_name < {OUTPUT_FILE}")