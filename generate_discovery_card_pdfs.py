import os
import markdown2
import pdfkit
import zipfile

MARKDOWN_DIR = "reports"
PDF_DIR = os.path.join(MARKDOWN_DIR, "pdf")
ZIP_FILE = os.path.join(MARKDOWN_DIR, "discovery_cards_bundle.zip")

def generate_pdfs():
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

    pdf_paths = []

    for fname in os.listdir(MARKDOWN_DIR):
        if fname.endswith(".md"):
            md_path = os.path.join(MARKDOWN_DIR, fname)
            pdf_filename = fname.replace(".md", ".pdf")
            pdf_path = os.path.join(PDF_DIR, pdf_filename)

            with open(md_path, "r", encoding="utf-8") as f:
                html = markdown2.markdown(f.read())

            # Convert to PDF (requires wkhtmltopdf installed)
            pdfkit.from_string(html, pdf_path)
            pdf_paths.append(pdf_path)
            print(f"✅ PDF generated: {pdf_path}")

    # Create zip
    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        for path in pdf_paths:
            zipf.write(path, arcname=os.path.basename(path))
    print(f"📦 All PDFs zipped to: {ZIP_FILE}")

if __name__ == "__main__":
    generate_pdfs()
