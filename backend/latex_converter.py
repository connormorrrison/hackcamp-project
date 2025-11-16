def convert_tex_to_pdf_direct(tex_file_path, cls_file_path=None, additional_files=None):
    """
    Directly convert TeX to PDF and return the PDF bytes
    Can be imported and used in other Python files
    """
    import os
    import subprocess
    import tempfile
    import shutil
    from pathlib import Path
    
    if not os.path.exists(tex_file_path):
        raise FileNotFoundError(f"TeX file not found: {tex_file_path}")
    
    if cls_file_path and not os.path.exists(cls_file_path):
        raise FileNotFoundError(f"Class file not found: {cls_file_path}")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Copy files to temp directory
        tex_filename = os.path.basename(tex_file_path)
        temp_tex_path = os.path.join(temp_dir, tex_filename)
        shutil.copy2(tex_file_path, temp_tex_path)
        
        if cls_file_path:
            cls_filename = os.path.basename(cls_file_path)
            temp_cls_path = os.path.join(temp_dir, cls_filename)
            shutil.copy2(cls_file_path, temp_cls_path)
        
        if additional_files:
            for file_path in additional_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    shutil.copy2(file_path, os.path.join(temp_dir, filename))
        
        # Compile TeX to PDF
        for _ in range(2):
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 
                 '-output-directory', temp_dir, temp_tex_path],
                cwd=temp_dir,
                capture_output=True,
                timeout=30
            )
        
        # Read the PDF file
        pdf_name = Path(tex_filename).stem + '.pdf'
        pdf_path = os.path.join(temp_dir, pdf_name)
        
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            return pdf_bytes
        else:
            raise Exception("PDF compilation failed")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)