import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger


# 📁 Папки
INPUT_ROOT = 'input'
OUTPUT_ROOT = 'output'
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# 📐 Страница
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40

# 🔤 Шрифт с кириллицей
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

# 🖋 Стили
title_style = ParagraphStyle(name='Title', fontName='DejaVu', fontSize=14, leading=16, spaceAfter=12)
cell_style = ParagraphStyle(name='Cell', fontName='DejaVu', fontSize=10, leading=12)

# 📄 Колонтитул
def add_footer(canvas_obj, doc, filename):
    canvas_obj.saveState()
    canvas_obj.setFont('DejaVu', 8)
    canvas_obj.drawString(MARGIN, 20, filename)
    canvas_obj.drawCentredString(PAGE_WIDTH / 2, 20, f"Стр. {doc.page}")
    canvas_obj.restoreState()

def create_pdf_from_csv(csv_path, pdf_path):
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')
    data = [df.columns.tolist()] + df.values.tolist()

    formatted_data = []
    for row in data:
        formatted_row = [Paragraph(str(cell), cell_style) for cell in row]
        formatted_data.append(formatted_row)

    title = os.path.splitext(os.path.basename(csv_path))[0]
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=MARGIN, leftMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=40)

    elements = [Paragraph(title, title_style), Spacer(1, 12)]

    col_count = len(formatted_data[0])
    col_widths = [30] + [(PAGE_WIDTH - 2 * MARGIN - 30) / (col_count - 1)] * (col_count - 1)

    table = Table(formatted_data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements, onFirstPage=lambda c, d: add_footer(c, d, title),
              onLaterPages=lambda c, d: add_footer(c, d, title))

def merge_pdfs(pdf_paths, output_path):
    merger = PdfMerger()
    for pdf_path in sorted(pdf_paths):
        merger.append(pdf_path)
        print(f'📎 Добавлен: {pdf_path}')
    merger.write(output_path)
    merger.close()
    print(f'✅ Объединённый PDF создан: {output_path}')

# 🔁 Обработка всех папок и CSV
all_generated_pdfs = []

for root, dirs, files in os.walk(INPUT_ROOT):
    rel_path = os.path.relpath(root, INPUT_ROOT)
    output_subfolder = os.path.join(OUTPUT_ROOT, rel_path)
    os.makedirs(output_subfolder, exist_ok=True)

    local_pdfs = []

    for filename in files:
        if filename.endswith('.csv'):
            csv_path = os.path.join(root, filename)
            pdf_filename = filename.replace('.csv', '.pdf')
            pdf_path = os.path.join(output_subfolder, pdf_filename)

            create_pdf_from_csv(csv_path, pdf_path)
            print(f'✅ PDF создан: {pdf_path}')
            local_pdfs.append(pdf_path)
            all_generated_pdfs.append(pdf_path)

    # 📎 Объединение PDF внутри текущей папки
    if local_pdfs:
        folder_name = os.path.basename(root)
        merged_local_path = os.path.join(output_subfolder, f'{folder_name}.pdf')
        merge_pdfs(local_pdfs, merged_local_path)
        all_generated_pdfs.append(merged_local_path)

# 📎 Финальное объединение всех PDF
final_combined_path = os.path.join(OUTPUT_ROOT, 'combined_output.pdf')
merge_pdfs(all_generated_pdfs, final_combined_path)