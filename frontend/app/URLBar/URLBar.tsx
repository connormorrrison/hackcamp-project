"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface URLBarProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit: () => void;
    canSubmit: boolean;
}

export function URLBar({value, onChange, onSubmit, canSubmit}: URLBarProps) {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && canSubmit) {
            onSubmit();
        }
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
        onChange(e.target.value);
    }

    return (
        <div className="flex gap-4 w-full max-w-2xl">
            <Input
                type="text"
                placeholder="Paste job description here..."
                value={value}
                onChange={handleChange}
                className="flex-1 rounded-2xl h-12 text-base!"
                onKeyDown={handleKeyDown}
            />
            <Button
                variant="outline"
                className="rounded-2xl h-12 text-base bg-blue-600! hover:bg-blue-700! text-white"
                onClick={canSubmit ? onSubmit : undefined}
                disabled={!canSubmit}
            >
                Generate
            </Button>
        </div>
    )
};