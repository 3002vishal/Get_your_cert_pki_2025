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
    
    def __init__(self):
        self.temp_files = []
    
    def __del__(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    
    def _format_full_name(self, first_name: str, middle_name: str = "", last_name: str = "") -> str:
        """
        Format the full name from individual components
        
        Args:
            first_name: First name (required)
            middle_name: Middle name (optional)
            last_name: Last name (optional)
        
        Returns:
            Properly formatted full name
        """
        # Remove extra whitespace and filter out empty strings
        name_parts = [name.strip() for name in [first_name, middle_name, last_name] if name and name.strip()]
        return " ".join(name_parts)
    
    def method1_pymupdf_text_replacement(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 1: Direct text replacement using PyMuPDF (best for text-based PDFs)
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Find and replace text - supports multiple placeholder formats
                placeholders = ["{{name}}", "XXXX", "{name}", "[name]"]
                
                for placeholder in placeholders:
                    text_instances = page.search_for(placeholder)
                    
                    for inst in text_instances:
                        # Add redaction annotation to remove old text
                        redact = page.add_redact_annot(inst)
                        redact.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))  # White color
                        redact.update()
                    
                    # Apply redactions
                    if text_instances:
                        page.apply_redactions()
                    
                    # Add new text
                    for inst in text_instances:
                        page.insert_text(
                            point=(inst.x0, inst.y1 - 5),  # Adjust position slightly
                            text=full_name,
                            fontsize=27,
                            color=(0, 0, 0),  # Black color
                            fontname="helv"
                        )
            
            doc.save(output_path)
            doc.close()
            return True
            
        except Exception as e:
            print(f"Method 1 failed: {e}")
            return False

    def method2_overlay_approach(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 2: Overlay approach with bold font support
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
        
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Support multiple placeholder formats
                placeholders = ["XXXX"]
                
                for placeholder in placeholders:
                    text_instances = page.search_for(placeholder)
                    
                    for inst in text_instances:
                        # Calculate rectangle size based on name length
                        name_length = len(full_name)
                        width_extension = max(80, name_length * 8)  # Dynamic width
                        
                        # Cover old text
                        rect = fitz.Rect(inst.x0 - 5, inst.y0 - 3, inst.x1 + width_extension, inst.y1 + 3)
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                        # Try bold fonts
                        bold_fonts = ["helv-bold", "tiro-bold", "Times-Bold", "Arial-Bold"]
                        bold_success = False
                    
                        for font in bold_fonts:
                            try:
                                page.insert_text(
                                    point=(inst.x0, inst.y1 - 2),
                                    text=full_name,
                                    fontsize=36,
                                    color=(0, 0, 0),
                                    fontname=font
                                )
                                bold_success = True
                                print(f"✓ Used font: {font} for name: {full_name}")
                                break
                            except Exception:
                                continue
                    
                        # If bold fails, simulate bold with multiple text layers
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

    def method3_form_field_approach(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 3: Handle PDF forms (if the PDF has form fields)
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Check for form fields
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
    
    def method4_advanced_text_replacement(self, pdf_path: str, first_name: str, middle_name: str, last_name: str, output_path: str) -> bool:
        """
        Method 4: Advanced approach with better text matching and replacement
        """
        try:
            doc = fitz.open(pdf_path)
            full_name = self._format_full_name(first_name, middle_name, last_name)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get all text with detailed information
                blocks = page.get_text("dict")
                
                placeholders = ["{{name}}", "XXXX", "{name}", "[name]"]
                replacements_made = False
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                
                                # Check if any placeholder exists in this text
                                for placeholder in placeholders:
                                    if placeholder in text:
                                        # Get font information
                                        font_size = span["size"]
                                        font_flags = span["flags"]
                                        bbox = span["bbox"]
                                        
                                        # Remove old text
                                        redact_rect = fitz.Rect(bbox)
                                        redact = page.add_redact_annot(redact_rect)
                                        redact.set_colors(fill=(1, 1, 1))  # White fill
                                        redact.update()
                                        
                                        # Replace text
                                        new_text = text.replace(placeholder, full_name)
                                        
                                        # Store replacement info
                                        replacement_info = {
                                            'rect': bbox,
                                            'text': new_text,
                                            'fontsize': font_size,
                                            'flags': font_flags
                                        }
                                        replacements_made = True
                                        break  # Found placeholder, no need to check others
                
                if replacements_made:
                    # Apply redactions first
                    page.apply_redactions()
                    
                    # Re-analyze and add text
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
        Main function to edit PDF name - tries multiple methods for best compatibility
        
        Args:
            pdf_path: Path to input PDF
            first_name: First name (required)
            middle_name: Middle name (optional)
            last_name: Last name (optional)
            output_path: Optional output path, if None creates based on input name
            
        Returns:
            Path to the edited PDF file
        """
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            full_name_for_filename = self._format_full_name(first_name, middle_name, last_name).replace(" ", "_")
            output_path = f"{base_name}_{full_name_for_filename}_edited.pdf"
        
        # Try methods in order of effectiveness
        methods = [
            ("Overlay Approach", self.method2_overlay_approach),
            ("Direct Text Replacement", self.method1_pymupdf_text_replacement),
            ("Form Field Approach", self.method3_form_field_approach),
            ("Advanced Text Replacement", self.method4_advanced_text_replacement)
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
        
        Args:
            pdf_template_path: Path to template PDF
            name_list: List of tuples (first_name, middle_name, last_name) or (first_name, last_name)
            output_dir: Directory to save edited PDFs
        """
        if output_dir is None:
            output_dir = os.path.dirname(pdf_template_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for name_tuple in name_list:
            try:
                # Handle both 2-tuple (first, last) and 3-tuple (first, middle, last)
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





def create_simple_function_interface():
    """Simple function interface for easy integration"""
    
    def create_certificate(pdf_template_path: str, first_name: str, middle_name: str = "", last_name: str = "", output_path: str = None) -> str:
        """
        Simple function to create a personalized certificate
        
        Args:
            pdf_template_path: Path to your PDF template
            first_name: First name (required)
            middle_name: Middle name (optional)
            last_name: Last name (optional)
            output_path: Where to save (optional)
            
        Returns:
            Path to created certificate
        """
        editor = PDFNameEditor()
        return editor.edit_pdf_name(pdf_template_path, first_name, middle_name, last_name, output_path)
    
    return create_certificate


# Installation requirements
REQUIREMENTS = """
# Required packages (install with pip):
pip install PyMuPDF reportlab Pillow

# PyMuPDF is the main library for PDF manipulation
# reportlab is for creating PDF overlays if needed
# Pillow is for image processing support
"""

import sys
import io

if __name__ == "__main__":
    pdf_template = sys.argv[1]     # template path from Node.js
    full_name   = sys.argv[2]      # e.g. "Vishal Kumar"

    # Split into parts if you want first/middle/last
    parts = full_name.split()
    first = parts[0] if len(parts) > 0 else ""
    middle = parts[1] if len(parts) == 3 else ""
    last = parts[-1] if len(parts) > 1 else ""

    editor = PDFNameEditor()

    # Generate certificate in-memory
    output_path = "temp_output.pdf"
    editor.edit_pdf_name(pdf_template, first, middle, last, output_path)

    # Read the file and write bytes to stdout
    with open(output_path, "rb") as f:
        sys.stdout.buffer.write(f.read())
