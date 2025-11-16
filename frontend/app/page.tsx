"use client"

import {URLBar} from "./URLBar/URLBar";
import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { InputBar } from "@/components/InputBar";
import { ShimmeringText } from "@/components/ShimmeringText";
import { DownloadButton } from "@/components/DownloadButton";
import { Button1 } from "@/components/Button-1";
import { PDFUpload } from "./PDFUpload/PDFUpload";

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [documentsReady, setDocumentsReady] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const [isValidUrl, setIsValidUrl] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const canSubmit = isValidUrl && file != null;

  const handleSubmit = () => {
    if (inputValue.trim()) {
      setIsGenerating(true);
      setDocumentsReady(false);

      // After 5 seconds, mark documents as ready
      setTimeout(() => {
        setDocumentsReady(true);
      }, 5000);
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
            <p className="text-2xl mb-10 text-foreground">Enter a job URL to get started</p>
          )}

          <URLBar 
          value={inputValue}
          onChange={setInputValue}
          onSubmit={handleSubmit}
          setIsValidUrl={setIsValidUrl}
          canSubmit={canSubmit} />
        
          <ShimmeringText isGenerating={isGenerating} documentsReady={documentsReady} />
          {isGenerating && (
            <div className="flex gap-4 mt-8">
              <DownloadButton type="resume" disabled={!documentsReady} />
              <DownloadButton type="coverLetter" disabled={!documentsReady} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

