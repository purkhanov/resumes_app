import os
import argparse
import pdfplumber
from src.elastic_search import create_index, add_to_elastic


folder_path = "./static/resumes"

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:

            text += page.extract_text()

        return text


def parse_resumes_in_folder(folder_path, index_name):
    result = []
    count = 1
    for filname in os.listdir(folder_path):
        if filname.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filname)
            # print(f"Парсим резюме:  {filname}")

            resume = extract_text_from_pdf(pdf_path)

            link = "/static/resumes/" + filname

            res = add_to_elastic(index_name, resume, link)
            if res.status_code == 201:
                print(f"[*] {count} success {filname}")

            elif res.status_code >= 400:
                print("error to add ", filname)

            count += 1         

            result.append(resume)
    return result


def main():
    index_name = "resumes"

    parser = argparse.ArgumentParser(description = "Parse resumes.")
    parser.add_argument("--resumes-folder", type = str, required = False, default = folder_path, help = "Path to the folder containing resume files")
    parser.add_argument("--create-index", type = bool, required = True, help = "Create index to elasticsearch")
    
    args = parser.parse_args()
    folder_path_param = args.resumes_folder
    create_index_param = args.create_index

    if create_index_param:
        create_index(index_name)

    parse_resumes_in_folder(folder_path_param, index_name)


if __name__ == "__main__":
    main()
