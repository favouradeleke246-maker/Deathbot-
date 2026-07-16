from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import json
from modules.utils import logger

class ReportGenerator:
    @staticmethod
    def generate_pdf(data, filename='report.pdf'):
        """Generate a PDF report from target data."""
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            c.drawString(100, 750, "SpectraX Intelligence Report")
            y = 700
            for key, value in data.items():
                if isinstance(value, dict):
                    value = json.dumps(value)[:100]
                c.drawString(100, y, f"{key}: {str(value)[:100]}")
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            return {'success': True, 'file': filename}
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return {'success': False, 'error': str(e)}
