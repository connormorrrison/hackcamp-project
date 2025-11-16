"use client";

import { Button } from "@/components/ui/button";
import { DownloadIcon } from "lucide-react";

interface DownloadButtonProps {
  type: "resume" | "coverLetter";
  disabled?: boolean;
  downloadUrl?: string;
  fileName?: string;
  onClick?: () => void;
}

export function DownloadButton({
  type,
  disabled = false,
  downloadUrl,
  fileName,
  onClick
}: DownloadButtonProps) {
  const line2 = type === "resume" ? "Resume" : "Cover Letter";
  const defaultFileName = type === "resume" ? "optimized-resume.pdf" : "cover-letter.pdf";

  const handleClick = (e: React.MouseEvent) => {
    if (disabled || !downloadUrl) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <a
      href={disabled || !downloadUrl ? undefined : downloadUrl}
      download={fileName || defaultFileName}
      className={disabled ? "pointer-events-none opacity-50" : ""}
      onClick={handleClick}
    >
      <Button
        variant="outline"
        disabled={disabled}
          className={`w-48 h-48 rounded-3xl text-white flex flex-col items-center justify-center gap-4`}
    >
        <DownloadIcon className="w-6! h-6!" />
        <div className="flex flex-col items-center text-base font-normal">
          <span>Download</span>
          <span>{line2}</span>
        </div>
      </Button>
      </a>
  );
}
