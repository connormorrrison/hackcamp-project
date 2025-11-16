"use client";

import { Button } from "@/components/ui/button";
import { useRef, useState } from "react";
import { ArrowUpIcon } from "lucide-react"

export function PDFUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
        const selectedFile = e.target.files?.[0];

        // case where there's no file selected
        if (!selectedFile) {
            setFile(null);
            setError("");
            return;
    
        }

        // case where the file type is NOT a .pdf
        if (selectedFile.type !== "application/pdf") {
            setFile(null);
            setError("Upload a PDF file");
            return;
        }

        // case where th efile is greater than 10MB in bytes
        const maxSize = 10 * 1024 * 1024; 
        if (selectedFile.size > maxSize) {
            setFile(null);
            setError("File size must be less than 10MB");
            return;
        }

        // if all things check out, save the file
        setFile(selectedFile);
        setError('');

    }

    function handleButtonClick() {
        fileInputRef.current?.click();
    }

    return(
        <div> 
            <input 
            ref={fileInputRef}
            type='file'
            accept=".pdf, application/pdf"
            onChange={handleFileChange}
            className="hidden"/>
            <Button 
            onClick={handleButtonClick}
            className="rounded-2xl h-12 text-base"
            variant="outline" >
                {file ? file.name : "Upload Resume"}
                <ArrowUpIcon />
            </Button>
        </div>
    )
}