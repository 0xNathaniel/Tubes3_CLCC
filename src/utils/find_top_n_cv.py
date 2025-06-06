import mysql.connector
from mysql.connector import Error
from algorithms.kmp import kmp
from algorithms.boyer_moore import boyer_moore
from algorithms.aho_corasick import aho_corasick
from algorithms.levenshtein import levenshtein_fuzzy_match
from utils.pdf_extractor import extract_text_from_pdf, extract_words_from_pdf
import time
import pprint
def extract_keywords(keywords: str):
    if not keywords:
        return []
    
    keyword_list = [keyword.strip().lower() for keyword in keywords.split(',')]
    unique_keywords = list(set(keyword_list))
    
    return unique_keywords

def find_top_n_cv(n : int, algorithm : str, keyword : str):
    try:
        koneksi = mysql.connector.connect(
            host='localhost',
            user='root',
            password='owen', 
            database='stima'
        )
    
        if koneksi.is_connected():
            cursor = koneksi.cursor(dictionary=True) 
            query = "SELECT * FROM ApplicantProfile ap INNER JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id"
            cursor.execute(query)
            combined_data = cursor.fetchall()
            
            top_n = {}
            exact_execution_times = 0
            fuzzy_execution_times = 0
            keyword_list = extract_keywords(keyword)
            
            global_keywords_found = [False] * len(keyword_list)
            

            for data_lamaran in combined_data:
                results = []
                if(algorithm == "kmp" and data_lamaran['cv_path'] is not None):
                    start_time = time.perf_counter()
                    results = kmp(extract_words_from_pdf(data_lamaran['cv_path']), keyword_list)
                    end_time = time.perf_counter() 
                    exact_execution_times += end_time - start_time
                elif(algorithm == "boyer_moore" and data_lamaran['cv_path'] is not None) :
                    start_time = time.perf_counter()
                    results = boyer_moore(extract_words_from_pdf(data_lamaran['cv_path']), keyword_list)
                    end_time = time.perf_counter()
                    exact_execution_times += end_time - start_time
                elif(algorithm == "aho_corasick" and data_lamaran['cv_path'] is not None) :
                    start_time = time.perf_counter()
                    results = aho_corasick(extract_words_from_pdf(data_lamaran['cv_path']), keyword_list)
                    end_time = time.perf_counter()
                    exact_execution_times += end_time - start_time
                
                
                for i, count in enumerate(results):
                    if count > 0:
                        global_keywords_found[i] = True
                
                
                total = sum(results)
                detail_id = data_lamaran['detail_id']

                if results :
                    top_n[detail_id] = {
                        'first_name': data_lamaran['first_name'], 
                        'last_name': data_lamaran['last_name'],
                        'application_role': data_lamaran['application_role'], 
                        'cv_path': data_lamaran['cv_path'],
                        'result': results, 
                        'total': total, 
                        'summary': ""
                    }

            fuzzy_map = {i: keyword_list[i] for i, found in enumerate(global_keywords_found) if not found}
            
            if fuzzy_map:
                keywords_to_fuzzy = list(fuzzy_map.values())
                
                for data_lamaran in combined_data:
                    detail_id = data_lamaran['detail_id']
                    
                    if detail_id in top_n and data_lamaran['cv_path'] is not None:
                        start_time = time.perf_counter()
                        fuzzy_results = levenshtein_fuzzy_match(data_lamaran['cv_path'], keywords_to_fuzzy)
                        end_time = time.perf_counter()
                        fuzzy_execution_times += end_time - start_time

                        if sum(fuzzy_results) > 0:
                            for original_index, fuzzy_count in zip(fuzzy_map.keys(), fuzzy_results):
                                if fuzzy_count > 0:
                                    top_n[detail_id]['result'][original_index] += fuzzy_count
                                    top_n[detail_id]['total'] += fuzzy_count

            top_n_sorted_list = sorted(top_n.items(), key=lambda item: item[1]['total'], reverse=True)[:n]
            
            top_n_sorted = {}
            for detail_id, cv_data in top_n_sorted_list:
                cv_data['summary'] = extract_text_from_pdf(cv_data['cv_path'])
                top_n_sorted[detail_id] = cv_data
            
            return {
                'top_n': top_n_sorted, # dictionary { detail_id: {first_name, last_name, application_role, cv_path, result, total, summary} }
                'exact_execution_time': exact_execution_times,
                'fuzzy_execution_time': fuzzy_execution_times,
                'total_cv' : len(combined_data),
            }

    except Error as e:
        print(f"Error saat menghubungkan ke MySQL: {e}")

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
        print(f"Waktu eksekusi Exact Match: {search_result['exact_execution_time']:.4f} detik")
        print(f"Waktu eksekusi Fuzzy Match: {search_result['fuzzy_execution_time']:.4f} detik")
    else:
        print("Tidak ada CV yang cocok dengan kriteria pencarian.")