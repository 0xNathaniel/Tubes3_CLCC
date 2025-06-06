import mysql.connector
from mysql.connector import Error

def find_top_n_cv(n: int):
    try:
        koneksi = mysql.connector.connect(
            host='localhost',
            user='root',
            password='owen', 
            database='stima'
        )
    
        if koneksi.is_connected():
            cursor = koneksi.cursor(dictionary=True) 
            
            query = """
                SELECT 
                    *
                FROM 
                    ApplicantProfile ap
                INNER JOIN 
                    ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            """
            
            cursor.execute(query)
            
            combined_data = cursor.fetchall()

            for data_lamaran in combined_data:
                print(f"Nama: {data_lamaran['first_name']} {data_lamaran['last_name']}, "
                        f"Role: {data_lamaran['application_role']}, "
                        f"CV Path: {data_lamaran['cv_path']}")

    except Error as e:
        print(f"Error saat menghubungkan ke MySQL: {e}")

    finally:
        if 'koneksi' in locals() and koneksi.is_connected():
            if 'cursor' in locals():
                cursor.close()
            koneksi.close()
            print("Koneksi MySQL ditutup.")

if __name__ == "__main__":
    find_top_n_cv(5)