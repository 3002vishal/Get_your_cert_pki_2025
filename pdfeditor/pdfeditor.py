import os
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
from PIL import Image, ImageDraw, ImageFont
import tempfile
from typing import Tuple, Optional
import io

class PDFNameEditor:
    """
    A comprehensive PDF editor that can replace placeholder names with actual names
    Supports first name, middle name, and last name as separate arguments
    """
    
    def _init_(self):
        self.temp_files = []
    
    def _del_(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    # def _format_full_name(self, first_name: str, middle_name: str = "", last_name: list=[]) -> str:
    #     """
    #     Format the full name from individual components
    #     """
    #     name_parts = [name.strip() for name in [first_name, middle_name, last_name] if name and name.strip()]
    #     return " ".join(name_parts)
    def _format_full_name(self, first_name: str, middle_name: str = "", last_name=None) -> str:
        """
        Format the full name from individual components.
        Supports last_name as a string or a list of strings.
        """
        if isinstance(last_name, list):  
            # join all last names with space
            last_name = " ".join([ln.strip() for ln in last_name if ln and ln.strip()])
        elif isinstance(last_name, str):
            last_name = last_name.strip()
        else:
            last_name = ""

        name_parts = [name.strip() for name in [first_name, middle_name, last_name] if name and name.strip()]
        return " ".join(name_parts)

    
    def _choose_reportlab_font(self, py_font_alias: str) -> str:
        """Map PyMuPDF font alias to a ReportLab font name for width measurement."""
        mapping = {
            "helv": "Helvetica",
            "helv-bold": "Helvetica-Bold",
            "Times-Bold": "Times-Bold",
            "Arial-Bold": "Helvetica-Bold",
            "tiro-bold": "Helvetica-Bold"
        }
        return mapping.get(py_font_alias, "Helvetica")

    def _calc_font_and_x_for_center(self, page, text: str, max_fontsize: int, min_fontsize: int,
                                    margin_ratio: float, reportlab_font: str) -> Tuple[int, float, float]:
        """
        Determine the largest fontsize (between max and min) such that text_width <= page_width - margins.
        Returns (fontsize, text_width, x_start).
        """
        page_width = page.rect.width
        margin = page_width * margin_ratio
        usable_width = max(10, page_width - 2 * margin)

        fontsize = max_fontsize
        text_width = 0.0

        while fontsize >= min_fontsize:
            text_width = pdfmetrics.stringWidth(text, reportlab_font, fontsize)
            if text_width <= usable_width:
                break
            fontsize -= 1

        x_start = (page_width - text_width) / 2.0
        return fontsize, text_width, x_start

    def _draw_centered_text(self, page, text: str, y: float,
                            max_fontsize: int = 36, min_fontsize: int = 10,
                            margin_ratio: float = 0.05, py_font_alias: str = "helv"):
        """
        Draw text centered horizontally on the page at vertical position y.
        """
        reportlab_font = self._choose_reportlab_font(py_font_alias)

        fontsize, text_width, x_start = self._calc_font_and_x_for_center(
            page, text, max_fontsize, min_fontsize, margin_ratio, reportlab_font
        )

        y_baseline_offset_ratio = 0.25
        y_baseline = max(0, y - (fontsize * y_baseline_offset_ratio))

        pymupdf_fontname = py_font_alias if py_font_alias in ("helv", "helv-bold", "Times-Bold", "Arial-Bold") else "helv"

        page.insert_text(
            point=(x_start, y_baseline),
            text=text,
            fontsize=fontsize,
            fontname=pymupdf_fontname,
            color=(0, 0, 0)
        )

    # def method1_pymupdf_text_replacement(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 1: Direct text replacement using PyMuPDF
        
        """
        print("fdlkjljfsalkdfasjlkjalsdjflkdsadjfljalfjlajfalfjlasfj")
        try:
            
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                placeholders = ["{{name}}", "XXXX", "{name}", "[name]"]
                
                for placeholder in placeholders:
                    text_instances = page.search_for(placeholder)
                    
                    for inst in text_instances:
                        redact = page.add_redact_annot(inst)
                        redact.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))
                        redact.update()
                    
                    if text_instances:
                        page.apply_redactions()
                    
                    for inst in text_instances:
                        self._draw_centered_text(page, full_name, y=inst.y1)
            
            doc.save(output_path)
            doc.close()
            return True
            
        except Exception as e:
            print(f"Method 1 failed: {e}")
            return False

        """
        Method 2: Overlay approach with bold font support
        """        
        print('inside 2')

        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                placeholders = ["XXXX"]
                
                for placeholder in placeholders:
                    text_instances = page.search_for(placeholder)
                    
                    for inst in text_instances:
                        name_length = len(full_name)
                        width_extension = max(80, name_length * 8)
                        
                        rect = fitz.Rect(inst.x0 - 5, inst.y0 - 3, inst.x1 + width_extension, inst.y1 + 3)
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                        bold_fonts = ["helv-bold", "tiro-bold", "Times-Bold", "Arial-Bold"]
                        bold_success = False
                    
                        for font in bold_fonts:
                            try:
                                self._draw_centered_text(page, full_name, y=inst.y1)
                                bold_success = True
                                print(f"✓ Used font: {font} for name: {full_name}")
                                break
                            except Exception:
                                continue
                    
                        if not bold_success:
                            print(f"⚠ Bold fonts failed, simulating bold for: {full_name}")
                            offsets = [(0, 0), (0.3, 0), (0, 0.3), (0.3, 0.3)]
                            for dx, dy in offsets:
                                page.insert_text(
                                    point=(inst.x0 + dx, inst.y1 - 2 + dy),
                                    text=full_name,
                                    fontsize=36,
                                    color=(0, 0, 0)
                                )
        
            doc.save(output_path)
            doc.close()
            return True
        
        except Exception as e:
            print(f"Method 2 failed: {e}")
            return False    

    def method2_overlay_approach(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 2: Overlay approach with automatic centering and font scaling.
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                placeholders = ["XXXX", "{{name}}", "{name}", "[name]"]

                for placeholder in placeholders:
                    text_instances = page.search_for(placeholder)

                    for inst in text_instances:
                        name_length = len(full_name)
                        width_extension = max(80, name_length * 8)
                        rect = fitz.Rect(inst.x0 - 5, inst.y0 - 3, inst.x1 + width_extension, inst.y1 + 3)

                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

                        bold_fonts = ["Times-Bold"]
                        bold_success = False

                        for font_alias in bold_fonts:
                            try:
                                self._draw_centered_text(
                                    page,
                                    full_name,
                                    y=inst.y1 - 2,
                                    max_fontsize=36,
                                    min_fontsize=10,
                                    margin_ratio=0.06,
                                    py_font_alias=font_alias
                                )
                                bold_success = True
                                print(f"✓ Used font (approx): {font_alias} for name: {full_name}")
                                break
                            except Exception:
                                continue

                        if not bold_success:
                            print(f"⚠ Bold fonts failed / unexpected error; falling back to simple centered text for: {full_name}")
                            self._draw_centered_text(
                                page,
                                full_name,
                                y=inst.y1 - 2,
                                max_fontsize=28,
                                min_fontsize=8,
                                margin_ratio=0.06,
                                py_font_alias="helv"
                            )

            doc.save(output_path)
            doc.close()
            return True

        except Exception as e:
            print(f"Method 2 failed: {e}")
            return False

    # def method3_form_field_approach(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 3: Handle PDF forms (if the PDF has form fields)
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                widgets = page.widgets()
                
                for widget in widgets:
                    if widget.field_name and "name" in widget.field_name.lower():
                        widget.field_value = full_name
                        widget.update()
            
            doc.save(output_path, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
            return True
            
        except Exception as e:
            print(f"Method 3 failed: {e}")
            return False
    
    # def method4_advanced_text_replacement(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 4: Advanced approach with better text matching and replacement
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")
                
                placeholders = ["{{name}}", "XXXX", "{name}", "[name]"]
                replacements_made = False
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                for placeholder in placeholders:
                                    if placeholder in text:
                                        font_size = span["size"]
                                        font_flags = span["flags"]
                                        bbox = span["bbox"]
                                        
                                        redact_rect = fitz.Rect(bbox)
                                        redact = page.add_redact_annot(redact_rect)
                                        redact.set_colors(fill=(1, 1, 1))
                                        redact.update()
                                        
                                        new_text = text.replace(placeholder, full_name)
                                        replacement_info = {
                                            'rect': bbox,
                                            'text': new_text,
                                            'fontsize': font_size,
                                            'flags': font_flags
                                        }
                                        replacements_made = True
                                        break
                
                if replacements_made:
                    page.apply_redactions()
                    
                    blocks = page.get_text("dict")
                    for block in blocks["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    text = span["text"]
                                    for placeholder in placeholders:
                                        if placeholder in text:
                                            bbox = span["bbox"]
                                            font_size = span["size"]
                                            new_text = text.replace(placeholder, full_name)
                                            
                                            page.insert_text(
                                                point=(bbox[0], bbox[3]),
                                                text=new_text,
                                                fontsize=font_size,
                                                color=(0, 0, 0)
                                            )
                                            break
            
            doc.save(output_path)
            doc.close()
            return True
            
        except Exception as e:
            print(f"Method 4 failed: {e}")
            return False
    
    def edit_pdf_name(self, pdf_path: str, first_name: str, middle_name: str = "", last_name: str = "", output_path: str = None) -> str:
        """
        Main function to edit PDF name
        """
        print('inside edit_pdf_name')
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            full_name_for_filename = self.format_full_name(first_name, middle_name, last_name).replace(" ", "")
            output_path = f"{base_name}_{full_name_for_filename}_edited.pdf"
        
        methods = [
             
           
            # ("Direct Text Replacement", self.method1_pymupdf_text_replacement),
            ("Overlay Approach", self.method2_overlay_approach),
           
            #("Direct Text Replacement", self.method1_pymupdf_text_replacement)
            # ("Form Field Approach", self.method3_form_field_approach),
            # ("Advanced Text Replacement", self.method4_advanced_text_replacement),
            
            
            
        ]
        
        full_name = self._format_full_name(first_name, middle_name, last_name)
        print(f"Creating certificate for: {full_name}")
        
        for method_name, method_func in methods:
            print(f"Trying {method_name}...")
            if method_func(pdf_path, first_name, middle_name, last_name, output_path):
                print(f"Success with {method_name}!")
                return output_path
        
        raise Exception("All methods failed to edit the PDF")
    
    def batch_process_certificates(self, pdf_template_path: str, name_list: list, output_dir: str = None):
        """
        Process multiple certificates with different names
        """
        if output_dir is None:
            output_dir = os.path.dirname(pdf_template_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for name_tuple in name_list:
            try:
                if len(name_tuple) == 2:
                    first_name, last_name = name_tuple
                    middle_name = ""
                elif len(name_tuple) == 3:
                    first_name, middle_name, last_name = name_tuple
                else:
                    raise ValueError(f"Invalid name tuple length: {len(name_tuple)}. Expected 2 or 3 elements.")
                
                full_name = self._format_full_name(first_name, middle_name, last_name)
                safe_filename = full_name.replace(" ", "_").replace(".", "")
                
                output_path = os.path.join(output_dir, f"certificate_{safe_filename}.pdf")
                edited_path = self.edit_pdf_name(pdf_template_path, first_name, middle_name, last_name, output_path)
                results.append({"name": full_name, "status": "success", "path": edited_path})
                print(f"✓ Created certificate for {full_name}")
            except Exception as e:
                full_name = self._format_full_name(*name_tuple) if len(name_tuple) <= 3 else str(name_tuple)
                results.append({"name": full_name, "status": "failed", "error": str(e)})
                print(f"✗ Failed to create certificate for {full_name}: {e}")
        
        return results


    # def create_simple_function_interface():
    #     """Simple function interface for easy integration"""
        
    #     def create_certificate(pdf_template_path: str, first_name: str, middle_name: str = "", last_name: str = "", output_path: str = None) -> str:
    #         editor = PDFNameEditor()
    #         return editor.edit_pdf_name(pdf_template_path, first_name, middle_name, last_name, output_path)

    #     return create_certificate


REQUIREMENTS = """
# Required packages (install with pip):
pip install PyMuPDF reportlab Pillow
"""

import sys
import io

if __name__ == "__main__":
    pdf_template = sys.argv[1]
    full_name   = sys.argv[2]
    print("="*50)
    print('inside pdfeditor')
    print("="*50)

    parts = full_name.split()
    # first = parts[0] if len(parts) > 0 else ""
    first =parts[0]
    middle = parts[1] if len(parts) >1 else ""
    last = parts[2:] if len(parts) > 2 else ""

    editor = PDFNameEditor()
    output_path = os.path.join(os.path.dirname(__file__),"temp_output.pdf")
    editor.edit_pdf_name(pdf_template, first, middle, last, output_path)

    with open(output_path, "rb") as f:
        sys.stdout.buffer.write(f.read())
