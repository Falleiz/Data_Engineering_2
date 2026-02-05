import PyPDF2

pdf_path = r'TP1\Data_Engineering_-_S1-2_-_Resources\Lab1_PythonDataPipeline.pdf'
output_path = 'lab1_content.txt'

with open(pdf_path, 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    
    with open(output_path, 'w', encoding='utf-8') as output:
        for i, page in enumerate(reader.pages):
            output.write(f'--- Page {i+1} ---\n')
            output.write(page.extract_text())
            output.write('\n\n')

print(f"Contenu extrait dans {output_path}")
print(f"Nombre de pages: {len(reader.pages)}")
