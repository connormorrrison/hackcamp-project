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
        result = None
        for i in range(2):
            result = subprocess.run(
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
            # PDF not created - show pdflatex output for debugging
            error_msg = f"PDF compilation failed. "
            if result:
                error_msg += f"Return code: {result.returncode}\n"

                # Check log file for detailed error
                log_name = Path(tex_filename).stem + '.log'
                log_path = os.path.join(temp_dir, log_name)
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                        # Find the actual error in the log
                        lines = log_content.split('\n')
                        error_lines = []
                        for i, line in enumerate(lines):
                            if '!' in line or 'Error' in line or 'error' in line:
                                # Include context around errors
                                start = max(0, i-2)
                                end = min(len(lines), i+5)
                                error_lines.extend(lines[start:end])
                        if error_lines:
                            error_msg += f"\nLog errors:\n" + '\n'.join(error_lines[:50])
                        else:
                            # Show last part of log if no specific errors found
                            error_msg += f"\nLast 2000 chars of log:\n{log_content[-2000:]}"

                if result.stderr:
                    error_msg += f"\n\nStderr:\n{result.stderr.decode('utf-8', errors='ignore')[:2000]}"
                if result.stdout:
                    error_msg += f"\n\nStdout:\n{result.stdout.decode('utf-8', errors='ignore')[:2000]}"
            raise Exception(error_msg)
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)