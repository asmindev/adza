import React, { useState, useRef, useCallback } from "react";
import { X } from "lucide-react";
import { cn } from "@/pages/detail/components/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

export function TagInput({
    placeholder,
    tags,
    setTags,
    disabled,
    className,
    variant = "default",
    ...props
}) {
    const [inputValue, setInputValue] = useState("");
    const inputRef = useRef(null);

    const addTag = useCallback(
        (tag) => {
            const trimmedTag = tag.trim();
            if (trimmedTag && !tags.includes(trimmedTag)) {
                const newTags = [...tags, trimmedTag];
                setTags(newTags);
            }
        },
        [tags, setTags]
    );

    const removeTag = useCallback(
        (tagToRemove) => {
            const newTags = tags.filter((tag) => tag !== tagToRemove);
            setTags(newTags);
        },
        [tags, setTags]
    );

    const handleInputChange = useCallback((e) => {
        setInputValue(e.target.value);
    }, []);

    const handleKeyDown = useCallback(
        (e) => {
            if (e.key === "Enter" || e.key === ",") {
                e.preventDefault();
                addTag(inputValue);
                setInputValue("");
            } else if (
                e.key === "Backspace" &&
                !inputValue &&
                tags.length > 0
            ) {
                removeTag(tags[tags.length - 1]);
            }
        },
        [inputValue, addTag, removeTag, tags]
    );

    const handleBlur = useCallback(() => {
        if (inputValue) {
            addTag(inputValue);
            setInputValue("");
        }
    }, [inputValue, addTag]);

    return (
        <div
            className={cn(
                "flex flex-wrap gap-2 border rounded-md p-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
                className
            )}
            onClick={() => inputRef.current?.focus()}
        >
            {tags.map((tag) => (
                <Badge key={tag} variant={variant} className="text-sm h-7 px-3">
                    {tag}
                    {!disabled && (
                        <button
                            type="button"
                            className="ml-2 text-muted-foreground hover:text-foreground focus:outline-none"
                            onClick={() => removeTag(tag)}
                        >
                            <X className="h-3 w-3" />
                            <span className="sr-only">Remove {tag} tag</span>
                        </button>
                    )}
                </Badge>
            ))}
            <Input
                ref={inputRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                placeholder={tags.length === 0 ? placeholder : ""}
                disabled={disabled}
                className="border-0 p-0 text-sm focus-visible:ring-0 flex-1 min-w-[120px] h-7"
                {...props}
            />
        </div>
    );
}
