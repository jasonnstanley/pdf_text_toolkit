import img2pdf
import os

def convert_jpgs_to_pdfs():
    # Get all .jpg files in current directory
    jpg_files = [f for f in os.listdir('.') if f.lower().endswith('.jpg')]

    if not jpg_files:
        print("No .jpg files found in current directory.")
        return

    for jpg in jpg_files:
        pdf_name = os.path.splitext(jpg)[0] + ".pdf"
        try:
            with open(pdf_name, "wb") as f:
                f.write(img2pdf.convert(jpg))
            print(f"✅ Converted: {jpg} → {pdf_name}")
        except Exception as e:
            print(f"❌ Failed to convert {jpg}: {e}")

if __name__ == "__main__":
    convert_jpgs_to_pdfs()
