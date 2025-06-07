import mysql.connector
from mysql.connector import Error
from algorithms.kmp import kmp
from algorithms.boyer_moore import boyer_moore
from algorithms.aho_corasick import aho_corasick
from algorithms.levenshtein import levenshtein_fuzzy_match
from utils.pdf_extractor import extract_cv_information, extract_words_from_pdf
from utils.rsa import get_rsa_instance, decrypt_data
import time
import pprint
import concurrent.futures

# Inisialisasi RSA konsisten dengan seeder
rsa_instance = get_rsa_instance()

def parse_encrypted_field(val):
    """Ubah string '123,456,789' menjadi list[int] [123,456,789]"""
    if isinstance(val, str):
        return [int(x) for x in val.split(',') if x.strip()]
    return val

def decrypt_applicant_row(row):
    """Dekripsi satu baris data profil applicant yang terenkripsi."""
    encrypted_fields = ['first_name', 'last_name', 'date_of_birth', 'address', 'phone_number']
    encrypted_dict = {}
    for key in encrypted_fields:
        encrypted_dict[key] = parse_encrypted_field(row[key])
    decrypted = decrypt_data(encrypted_dict, rsa_instance)
    decrypted['applicant_id'] = row['applicant_id']
    # Tambahkan field lain yang tidak dienkripsi jika ingin
    return decrypted

def extract_keywords(keywords: str):
    if not keywords:
        return []
    keyword_list = [keyword.strip().lower() for keyword in keywords.split(',')]
    unique_keywords = list(set(keyword_list))
    return unique_keywords

def process_cv_exact(args):
    data_lamaran, keyword_list, algorithm = args
    detail_id = data_lamaran['detail_id']
    if data_lamaran['cv_path'] is None:
        return detail_id, []

    cv_words = extract_words_from_pdf(data_lamaran['cv_path'])
    if not cv_words:
        return detail_id, []

    results = []
    if algorithm == "kmp":
        results = kmp(cv_words, keyword_list)
    elif algorithm == "boyer_moore":
        results = boyer_moore(cv_words, keyword_list)
    elif algorithm == "aho_corasick":
        results = aho_corasick(cv_words, keyword_list)
    
    return detail_id, results

def process_cv_fuzzy(args):
    data_lamaran, keywords_to_fuzzy = args
    detail_id = data_lamaran['detail_id']
    if data_lamaran['cv_path'] is None:
        return detail_id, []
        
    cv_words = extract_words_from_pdf(data_lamaran['cv_path'])
    if not cv_words:
        return detail_id, []

    results = levenshtein_fuzzy_match(cv_words, keywords_to_fuzzy)
    return detail_id, results

def find_top_n_cv(n : int, algorithm : str, keyword : str):
    try:
        koneksi = mysql.connector.connect(
            host='0.tcp.ap.ngrok.io', user='remote_user', password='owen', database='stima_encrypted', port=16096
        )
        if koneksi.is_connected():
            cursor = koneksi.cursor(dictionary=True) 
            query = "SELECT * FROM ApplicantProfile ap INNER JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id"
            cursor.execute(query)
            all_cv_data = cursor.fetchall()
            
            # Dekripsi data profil applicant
            for row in all_cv_data:
                decrypted = decrypt_applicant_row(row)
                row['first_name'] = decrypted['first_name']
                row['last_name'] = decrypted['last_name']
                row['date_of_birth'] = decrypted['date_of_birth']
                row['address'] = decrypted['address']
                row['phone_number'] = decrypted['phone_number']
                # applicant_id tetap plaintext

            keyword_list = extract_keywords(keyword)
            if not keyword_list:
                return {'top_n': [], 'exact_execution_time': 0, 'fuzzy_execution_time': 0, 'total_cv': 0}

            exact_execution_times = 0
            fuzzy_execution_times = 0
            
            processed_results = {
                data['detail_id']: {
                    'first_name': data['first_name'], 'last_name': data['last_name'],
                    'application_role': data['application_role'], 'cv_path': data['cv_path'],
                    'result': [0] * len(keyword_list), 'total': 0, 'summary': ""
                } for data in all_cv_data
            }

            global_keywords_found = [False] * len(keyword_list)
            
            start_exact_time = time.perf_counter()
            with concurrent.futures.ProcessPoolExecutor() as executor:
                exact_match_args = [(data, keyword_list, algorithm) for data in all_cv_data]
                results_iterator = executor.map(process_cv_exact, exact_match_args)
                
                for detail_id, exact_results in results_iterator:
                    if exact_results:
                        for i, count in enumerate(exact_results):
                            if count > 0:
                                global_keywords_found[i] = True
                                processed_results[detail_id]['result'][i] += count
                                processed_results[detail_id]['total'] += count
            exact_execution_times = time.perf_counter() - start_exact_time

            fuzzy_map = {i: keyword_list[i] for i, found in enumerate(global_keywords_found) if not found}
            
            start_fuzzy_time = time.perf_counter()
            if fuzzy_map:
                keywords_to_fuzzy = list(fuzzy_map.values())
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    fuzzy_match_args = [(data, keywords_to_fuzzy) for data in all_cv_data]
                    results_iterator = executor.map(process_cv_fuzzy, fuzzy_match_args)

                    for detail_id, fuzzy_results in results_iterator:
                        if sum(fuzzy_results) > 0:
                            for original_index, fuzzy_count in zip(fuzzy_map.keys(), fuzzy_results):
                                if fuzzy_count > 0:
                                    processed_results[detail_id]['result'][original_index] += fuzzy_count
                                    processed_results[detail_id]['total'] += fuzzy_count
            fuzzy_execution_times = time.perf_counter() - start_fuzzy_time

            final_results = [data for data in processed_results.values() if data['total'] > 0]
            sorted_results = sorted(final_results, key=lambda item: item['total'], reverse=True)
            top_n_final = sorted_results[:n]
            
            for result_data in top_n_final:
                if result_data['cv_path']:
                    try:
                        from utils.pdf_extractor import extract_text_from_pdf
                        pdf_text = extract_text_from_pdf(result_data['cv_path'])
                        if pdf_text:
                            result_data['summary'] = extract_cv_information(pdf_text)
                        else:
                            result_data['summary'] = "Could not extract text from PDF file."
                    except Exception as e:
                        print(f"Error extracting CV info for {result_data['cv_path']}: {e}")
                        result_data['summary'] = f"Error extracting CV information: {str(e)}"
                else:
                    result_data['summary'] = "No CV file available."

            return {
                'top_n': top_n_final,
                'exact_execution_time': exact_execution_times,
                'fuzzy_execution_time': fuzzy_execution_times,
                'total_cv': len(all_cv_data)
            }

    except Error as e:
        print(f"Error saat menghubungkan ke MySQL: {e}")
        return {'top_n': [], 'exact_execution_time': 0, 'fuzzy_execution_time': 0, 'total_cv': 0}

    finally:
        if 'koneksi' in locals() and koneksi.is_connected():
            if 'cursor' in locals():
                cursor.close()
            koneksi.close()

if __name__ == "__main__":
    JUMLAH_CV_TAMPIL = 1
    ALGORITMA = "kmp"
    KEYWORDS = "nursing"

    search_result = find_top_n_cv(JUMLAH_CV_TAMPIL, ALGORITMA, KEYWORDS)

    if search_result and search_result['top_n']:
        print("--- TOP CV DITEMUKAN ---")
        pprint.pprint(search_result['top_n'])
        
        print("\n--- RINGKASAN PENCARIAN ---")
        print(f"Total CV dipindai: {search_result['total_cv']}")
        print(f"Waktu eksekusi Exact Match (paralel): {search_result['exact_execution_time']:.4f} detik")
        print(f"Waktu eksekusi Fuzzy Match (paralel): {search_result['fuzzy_execution_time']:.4f} detik")
    else:
        print("Tidak ada CV yang cocok dengan kriteria pencarian.")