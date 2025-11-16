import { Button } from "@/components/ui/button";
import { DownloadIcon } from "lucide-react";

interface DownloadButtonProps {
  type: "resume" | "coverLetter";
  disabled?: boolean;
}

export function DownloadButton({ type, disabled = false }: DownloadButtonProps) {
  const line2 = type === "resume" ? "Resume" : "Cover Letter";

  return (
    <Button
      variant="outline"
      disabled={disabled}
      className={`w-48 h-48 rounded-3xl text-white flex flex-col items-center justify-center gap-4 ${
        disabled
          ? "cursor-not-allowed opacity-50"
          : ""
      }`}
    >
      <DownloadIcon className="w-6! h-6!" />
      <div className="flex flex-col items-center text-base font-normal">
        <span>Download</span>
        <span>{line2}</span>
      </div>
    </Button>
  );
}
