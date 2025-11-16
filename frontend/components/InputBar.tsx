"use client"

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface InputBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function InputBar({ value, onChange, onSubmit }: InputBarProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      onSubmit();
    }
  };

  return (
    <div className="flex gap-4 w-full max-w-2xl">
      <Input
        type="text"
        placeholder="Enter a URL to a job application..."
        className="flex-1 rounded-2xl h-12 text-base!"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <Button
        variant="outline"
        className="rounded-2xl h-12 text-base bg-blue-600! hover:bg-blue-700! text-white"
        onClick={onSubmit}
      >
        Submit
      </Button>
    </div>
  );
}