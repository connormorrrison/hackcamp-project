"use client";

import { Input } from "@/components/ui/input";
import { useState } from "react";

export function URLBar() {
    const [url, setUrl] = useState("");
    const [isValid, setIsValid] = useState(true);
    

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
    }
    
    return (
        <Input 
        type="url"
        placeholder="Enter Job URL"
        value={url}
        onChange={handleChange}
        className={ !isValid ? "!border-red-500" : "border-gray-300"}

        />
    )

};