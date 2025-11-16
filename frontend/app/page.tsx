"use client"

import {URLBar} from "./URLBar/URLBar";
import { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { InputBar } from "@/components/InputBar";
import { ShimmeringText } from "@/components/ShimmeringText";
import { DownloadButton } from "@/components/DownloadButton";
import { Button1 } from "@/components/Button-1";
import { PDFUpload } from "./PDFUpload/PDFUpload";
import { generateAndConvertDocuments, convertLatexToPdf } from "@/lib/api";

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [documentsReady, setDocumentsReady] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const [file, setFile] = useState<File | null>(null);

  // Store generated documents
  const [resumePdfUrl, setResumePdfUrl] = useState<string | null>(null);
  const [coverLetterPdfUrl, setCoverLetterPdfUrl] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const canSubmit = jobDescription.trim().length > 0 && file != null;

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      if (resumePdfUrl) URL.revokeObjectURL(resumePdfUrl);
      if (coverLetterPdfUrl) URL.revokeObjectURL(coverLetterPdfUrl);
    };
  }, [resumePdfUrl, coverLetterPdfUrl]);

  const handleSubmit = async () => {
    if (!file || !jobDescription.trim()) return;

    setIsGenerating(true);
    setDocumentsReady(false);
    setError(null);

    try {
      // Call the API to generate and convert documents
      const result = await generateAndConvertDocuments(file, jobDescription);

      // Create blob URL for resume PDF
      const resumeUrl = URL.createObjectURL(result.resumePdf);
      setResumePdfUrl(resumeUrl);

      // Create blob URL for cover letter PDF
      const coverLetterUrl = URL.createObjectURL(result.coverLetterPdf);
      setCoverLetterPdfUrl(coverLetterUrl);

      // Store suggestions
      setSuggestions(result.suggestions);

      // Mark as ready
      setDocumentsReady(true);
    } catch (err) {
      console.error('Error generating documents:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate documents');
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex min-h-screen relative">
      <div className="absolute top-8 right-8 z-10">
        <PDFUpload 
        onFileSelect={setFile}/>
      </div>
      <div className="flex-1 flex flex-col justify-center items-center p-10 overflow-hidden">
        <div className="flex flex-col items-center justify-center w-full max-w-2xl transition-all ease-out duration-300">
          {!isGenerating && (
            <p className="text-2xl mb-10 text-foreground">Paste a job description to get started</p>
          )}

          <URLBar
          value={jobDescription}
          onChange={setJobDescription}
          onSubmit={handleSubmit}
          canSubmit={canSubmit} />
        
          <ShimmeringText isGenerating={isGenerating} documentsReady={documentsReady} />

          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500 rounded-lg text-red-500 max-w-md">
              <p className="font-semibold">Error:</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {isGenerating && (
            <div className="flex gap-4 mt-8">
              <DownloadButton
                type="resume"
                disabled={!documentsReady}
                downloadUrl={resumePdfUrl || undefined}
                fileName="optimized-resume.pdf"
              />
              <DownloadButton
                type="coverLetter"
                disabled={!documentsReady}
                downloadUrl={coverLetterPdfUrl || undefined}
                fileName="cover-letter.pdf"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

