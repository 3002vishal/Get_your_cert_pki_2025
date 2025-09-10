from pdfeditor import PDFNameEditor
editor  = PDFNameEditor()

output_path = editor.edit_pdf_name(
    pdf_path = "./vikash.pdf",
    first_name = "jhon",
    last_name = "doe"
)