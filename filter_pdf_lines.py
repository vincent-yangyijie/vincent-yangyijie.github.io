import sys
import pdfplumber

sys.path.append(r'C:\Users\BELLE\AppData\Roaming\Python\Python313\site-packages')
import pdfplumber
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO

def filter_lines_with_keyword(input_pdf, output_pdf, keyword):
    writer = PdfWriter()
    
    with pdfplumber.open(input_pdf) as plumb_pdf:
        reader = PdfReader(input_pdf)
        for page_num in range(len(plumb_pdf.pages)):
            page = plumb_pdf.pages[page_num]
            text = page.extract_text()
            
            if text:
                lines = text.split('\n')
                filtered_lines = [line for line in lines if keyword in line]
                
                if filtered_lines:
                    packet = BytesIO()
                    mediabox = reader.pages[page_num].mediabox
                    can = canvas.Canvas(packet, pagesize=(mediabox.width, mediabox.height))
                    y_position = can._pagesize[1] - 40  # 页面顶部边距
                    line_height = 12
                    
                    for line in filtered_lines:
                        if y_position < 40:  # 页面底部边距
                            can.showPage()
                            y_position = can._pagesize[1] - 40
                        can.drawString(40, y_position, line)
                        y_position -= line_height
                    
                    can.save()
                    packet.seek(0)
                    new_pdf = PdfReader(packet)
                    writer.add_page(new_pdf.pages[0])
    
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    print(f"成功生成PDF文件: {output_pdf}")

if __name__ == "__main__":
    input_path = "ref.pdf"
    output_path = "filtered_arxiv_lines.pdf"
    target_keyword = "arXiv"
    
    filter_lines_with_keyword(input_path, output_path, target_keyword)