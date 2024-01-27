from PyPDF2 import PdfReader


def parse_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = pdf_reader.pages[1].extract_text()
        
    return text
