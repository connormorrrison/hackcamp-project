// API service layer for backend communication

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

export interface GenerateResponse {
  result: {
    optimized_resume: string;  // LaTeX code
    optimized_cover_letter: string;  // Text
    resume_suggestions: string[];  // Array of suggestions
  };
}

export interface ErrorResponse {
  error: string;
  details?: string;
  raw_output?: string;
}

/**
 * Generate optimized resume and cover letter using OpenAI
 */
export async function generateDocuments(
  resumeFile: File,
  jobDescription: string
): Promise<GenerateResponse> {
  const formData = new FormData();
  formData.append('resume_pdf', resumeFile);
  formData.append('jobDescription', jobDescription);

  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.error || 'Failed to generate documents');
  }

  return response.json();
}

/**
 * Convert LaTeX code to PDF
 */
export async function convertLatexToPdf(
  latexContent: string,
  filename: string = 'document.pdf'
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/convert-latex-to-pdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ latex_content: latexContent }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Failed to convert LaTeX to PDF' }));
    throw new Error(error.error || 'Failed to convert LaTeX to PDF');
  }

  return response.blob();
}

/**
 * Helper function to download a blob as a file
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Complete flow: generate documents and convert to PDFs
 */
export async function generateAndConvertDocuments(
  resumeFile: File,
  jobDescription: string
): Promise<{
  resumePdf: Blob;
  coverLetterPdf: Blob;
  suggestions: string[];
}> {
  // Step 1: Generate optimized content
  const generateResult = await generateDocuments(resumeFile, jobDescription);

  // Step 2: Convert LaTeX resume to PDF
  const resumePdf = await convertLatexToPdf(
    generateResult.result.optimized_resume,
    'optimized-resume.pdf'
  );

  // Step 3: Convert LaTeX cover letter to PDF
  const coverLetterPdf = await convertLatexToPdf(
    generateResult.result.optimized_cover_letter,
    'cover-letter.pdf'
  );

  return {
    resumePdf,
    coverLetterPdf,
    suggestions: generateResult.result.resume_suggestions,
  };
}
