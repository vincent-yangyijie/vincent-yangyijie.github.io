import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

def extract_pages_with_keywords(input_pdf, output_pdf, keywords):
    try:
        with pdfplumber.open(input_pdf) as pdf:
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if all(keyword in text for keyword in keywords):
                    writer.add_page(reader.pages[page_num])
            
            with open(output_pdf, 'wb') as f:
                writer.write(f)
        
        print(f"成功生成PDF文件: {output_pdf}，共{len(writer.pages)}页")
    except Exception as e:
        print(f"处理出错: {str(e)}")

if __name__ == "__main__":
    input_path = "ref.pdf"
    output_path = "extracted_arxiv_2025.pdf"
    target_keywords = ["arXiv", "2025"]
    
    extract_pages_with_keywords(input_path, output_path, target_keywords)