from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        now = datetime.today().date()
        
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Polizeipräsidium", border=0, align="C")
        self.ln(10)  # move down before content starts
        self.set_font("Helvetica", "B", 10)
        self.cell(0,10, now.strftime("%d/%m/%Y"), border=0, align="C")
        self.ln(15)  # move down before content starts


def convert_df_to_pdf(df):
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    
        # Calculate perfect vertical column widths dynamically
    # 210mm (A4 width) - 20mm (default left/right margins) = 190mm writable space
    writable_width = 190
    col_width = writable_width / len(df.columns)
    row_height = 8  # Fixed cell height in millimeters
    
    # Render Table Header
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.set_fill_color(230, 230, 230) # Soft grey header background
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1, align="C", fill=True)
    pdf.ln()


    
    # Render Table Rows
    pdf.set_font("Helvetica", style="", size=10)
    for _, row in df.iterrows():
        for item in row:
            # Clean text strings to avoid character rendering drops
            clean_text = str(item).replace('\n', ' ').replace('\r', '')
            pdf.cell(col_width, row_height, clean_text, border=1, align="L")
        pdf.ln()

    pdf_output_bytes = bytes(pdf.output(dest='S'))
    return pdf_output_bytes