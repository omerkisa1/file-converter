import os
import subprocess
import sys
from typing import List
from core.base_converter import BaseConverter


class DocumentConverter(BaseConverter):
    
    @property
    def supported_input_formats(self) -> List[str]:
        return ["pdf", "docx", "pptx", "txt", "html", "md"]
    
    @property
    def supported_output_formats(self) -> List[str]:
        return ["pdf", "docx"]
    
    def convert(self, input_path: str, output_format: str) -> str:
        input_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        output_format = output_format.lower().lstrip(".")
        
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted.{output_format}"
        
        if input_ext == "pdf" and output_format == "docx":
            return self._pdf_to_docx(input_path, output_path)
        elif input_ext == "docx" and output_format == "pdf":
            return self._docx_to_pdf(input_path, output_path)
        elif input_ext == "pptx" and output_format == "pdf":
            return self._pptx_to_pdf(input_path, output_path)
        elif input_ext == "txt" and output_format == "pdf":
            return self._txt_to_pdf(input_path, output_path)
        elif input_ext == "html" and output_format == "pdf":
            return self._html_to_pdf(input_path, output_path)
        elif input_ext == "md" and output_format == "pdf":
            return self._md_to_pdf(input_path, output_path)
        else:
            raise ValueError(f"Conversion from {input_ext} to {output_format} not supported")
    
    def _pdf_to_docx(self, input_path: str, output_path: str) -> str:
        from pdf2docx import Converter
        
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        
        return output_path
    
    def _docx_to_pdf(self, input_path: str, output_path: str) -> str:
        if sys.platform == "win32":
            try:
                from docx2pdf import convert
                convert(input_path, output_path)
                return output_path
            except Exception:
                pass
        
        try:
            output_dir = os.path.dirname(output_path) or "."
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", 
                 "--outdir", output_dir, input_path],
                check=True,
                capture_output=True
            )
            
            expected_output = os.path.join(
                output_dir, 
                os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            if expected_output != output_path and os.path.exists(expected_output):
                os.rename(expected_output, output_path)
            
            return output_path
        except FileNotFoundError:
            raise RuntimeError(
                "DOCX to PDF conversion requires either Microsoft Word (Windows) "
                "or LibreOffice (cross-platform) to be installed."
            )
    
    def _pptx_to_pdf(self, input_path: str, output_path: str) -> str:
        abs_input = os.path.abspath(input_path)
        abs_output = os.path.abspath(output_path)
        
        if sys.platform == "win32":
            try:
                import win32com.client
                import pythoncom
                
                pythoncom.CoInitialize()
                
                powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                
                presentation = powerpoint.Presentations.Open(abs_input, WithWindow=False)
                presentation.SaveAs(abs_output, 32)
                presentation.Close()
                powerpoint.Quit()
                
                pythoncom.CoUninitialize()
                
                return output_path
            except ImportError:
                pass
            except Exception as e:
                try:
                    powerpoint.Quit()
                except:
                    pass
                raise RuntimeError(f"PowerPoint conversion failed: {str(e)}")
        
        try:
            output_dir = os.path.dirname(output_path) or "."
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", 
                 "--outdir", output_dir, abs_input],
                check=True,
                capture_output=True,
                text=True
            )
            
            expected_output = os.path.join(
                output_dir, 
                os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            if expected_output != output_path and os.path.exists(expected_output):
                os.rename(expected_output, output_path)
            
            return output_path
        except FileNotFoundError:
            raise RuntimeError(
                "PPTX to PDF conversion requires either Microsoft PowerPoint (Windows) "
                "or LibreOffice (cross-platform) to be installed. "
                "Install pywin32: pip install pywin32"
            )

    def _txt_to_pdf(self, input_path: str, output_path: str) -> str:
        try:
            from fpdf import FPDF
        except ImportError:
            raise RuntimeError("TXT to PDF conversion requires fpdf2: pip install fpdf2")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)
        
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                pdf.multi_cell(0, 10, line.rstrip())
        
        pdf.output(output_path)
        return output_path
    
    def _html_to_pdf(self, input_path: str, output_path: str) -> str:
        try:
            from weasyprint import HTML
        except ImportError:
            raise RuntimeError("HTML to PDF conversion requires weasyprint: pip install weasyprint")
        
        HTML(filename=input_path).write_pdf(output_path)
        return output_path
    
    def _md_to_pdf(self, input_path: str, output_path: str) -> str:
        try:
            import markdown
            from weasyprint import HTML
        except ImportError:
            raise RuntimeError("Markdown to PDF requires: pip install markdown weasyprint")
        
        with open(input_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
        
        styled_html = f"""<!DOCTYPE html>
        <html><head><meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
        </style></head>
        <body>{html_content}</body></html>"""
        
        HTML(string=styled_html).write_pdf(output_path)
        return output_path
