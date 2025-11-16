"use client"

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { TextShimmer } from "@/components/motion-primitives/text-shimmer";

export function ChatArea() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = () => {
    if (inputValue.trim()) {
      setIsGenerating(true);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    // This parent div is already doing the vertical centering with `justify-center`
    <div className="flex-1 flex flex-col justify-center items-center p-10 overflow-hidden">
      
      {/* Wrapper for animation */}
      <div
        className={`
          flex flex-col items-center justify-center w-full max-w-2xl
          transition-all ease-out
          duration-300
        `}
        // We removed the ${isGenerating ? "-translate-y-20" : "translate-y-0"}
        // Now, the parent's "justify-center" will keep this whole block
        // centered vertically as it grows.
      >
        {/* Input bar */}
        <div className="flex gap-4 w-full">
          <Input
            type="text"
            placeholder="Enter a URL to a job application..."
            className="flex-1 rounded-2xl h-12 text-base!"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <Button
            variant="outline"
            className="rounded-2xl h-12 text-base bg-blue-600! hover:bg-blue-700! text-white"
            onClick={handleSubmit}
          >
            Submit
          </Button>
        </div>

        {/* Generating text */}
        <div
          className={`
            text-center transition-all duration-300 ease-out
            ${isGenerating
              ? "opacity-100 max-h-12 mt-8"
              : "opacity-0 max-h-0 mt-0"
            }
          `}
        >
          <TextShimmer className="text-lg">Generating your documents...</TextShimmer>
        </div>
      </div>
    </div>
  );
}