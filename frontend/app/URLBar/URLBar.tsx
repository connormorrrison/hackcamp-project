"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface URLBarProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit: () => void;
}

export function URLBar({value, onChange, onSubmit}: URLBarProps) {
    const [url, setUrl] = useState("");
    const [isValid, setIsValid] = useState(true);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && isValid) {
            onSubmit();
        }
    }   

    // checks to see if the input is a url //
    function validateURL(value: string) {
        try {
            new URL(value);
            return true;
        } catch {
            return false;
        }
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
        const value = e.target.value;
        setUrl(value);
        setIsValid(validateURL(value) || value === "");
        onChange(e.target.value)
    }
    
    return (
        <div className="flex gap-4 w-full max=w=2xl">
            <Input 
            type="url"
            placeholder="Enter Job URL"
            value={url}
            onChange={handleChange}
            className={`flex-1 rounded-2xl h-12 text-base! ${!isValid ? "!border-red-500" : "border-gray-300"}`}
            onKeyDown={handleKeyDown}

            />
        <Button
        variant="outline"
        className="rounded-2xl h-12 text-base bg-blue-600! hover:bg-blue-700! text-white"
        onClick={isValid ? onSubmit : () => {}}
        disabled={!isValid}
        >
            Generate
        </Button>
        </div>
    )

};