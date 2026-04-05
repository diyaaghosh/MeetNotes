from fpdf import FPDF

def clean_text(text):
    return text.replace("•", "-")  

def generate_pdf(summary, bullets, output_file):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Meeting Notes", ln=True, align="C")

    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Summary", ln=True)

    pdf.set_font("Arial", size=12)

    if isinstance(summary, list):
        summary = " ".join(summary)

    summary = clean_text(summary)   
    pdf.multi_cell(0, 8, summary)

    pdf.ln(5)

    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Key Points", ln=True)

    pdf.set_font("Arial", size=12)

    for b in bullets:
        b = clean_text(b)  
        pdf.multi_cell(0, 8, "- " + b)

    pdf.output(output_file)