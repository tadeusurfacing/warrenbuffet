from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd

def exportar_pdf(df):
    """
    Função para exportar o DataFrame para um arquivo PDF.
    df: DataFrame com os dados.
    Retorna: Uma tupla (sucesso, mensagem), onde sucesso é um booleano e mensagem é uma string.
    """
    try:
        output_file = "relatorio_investimentos.pdf"
        c = canvas.Canvas(output_file, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(100, 800, "Relatório de Investimentos")
        y = 750
        for index, row in df.iterrows():
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 800
            text = f"{row['Papel']}: R$ {row['Valor Atual']:.2f} (Rentabilidade: {row['Rentabilidade']})"
            c.drawString(100, y, text)
            y -= 20
        c.save()
        return True, f"PDF exportado com sucesso: {output_file}"
    except Exception as e:
        return False, f"Erro ao exportar PDF: {str(e)}"
