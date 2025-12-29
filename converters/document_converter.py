import os
import subprocess
import sys
from typing import List
from core.base_converter import BaseConverter


class DocumentConverter(BaseConverter):
    
    @property
    def supported_input_formats(self) -> List[str]:
        return ["pdf", "docx", "pptx"]
    
    @property
    def supported_output_formats(self) -> List[str]:
        return ["pdf", "docx", "pptx"]
    
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

