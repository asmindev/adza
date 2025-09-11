import React, { useState, useRef, useEffect } from "react";
import { Check, ChevronDown, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function MultiSelect({
    options = [],
    value = [],
    onChange,
    placeholder = "Pilih kategori...",
    className,
    disabled = false,
}) {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const dropdownRef = useRef(null);
    const inputRef = useRef(null);

    // Filter options based on search term
    const filteredOptions = options.filter((option) =>
        option.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Get selected options for display
    const selectedOptions = options.filter((option) =>
        value.includes(option.id)
    );

    // Handle option toggle
    const handleToggle = (optionId) => {
        const newValue = value.includes(optionId)
            ? value.filter((id) => id !== optionId)
            : [...value, optionId];
        onChange(newValue);
    };

    // Handle remove selected option
    const handleRemove = (optionId, e) => {
        e.stopPropagation();
        const newValue = value.filter((id) => id !== optionId);
        onChange(newValue);
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target)
            ) {
                setIsOpen(false);
                setSearchTerm("");
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className={cn("relative", className)} ref={dropdownRef}>
            {/* Main trigger button */}
            <Button
                type="button"
                variant="outline"
                onClick={() => setIsOpen(!isOpen)}
                disabled={disabled}
                className={cn(
                    "w-full justify-between text-left font-normal",
                    !selectedOptions.length && "text-muted-foreground"
                )}
            >
                <div className="flex flex-wrap gap-1 flex-1">
                    {selectedOptions.length === 0 ? (
                        <span>{placeholder}</span>
                    ) : (
                        <>
                            {selectedOptions.slice(0, 2).map((option) => (
                                <Badge
                                    key={option.id}
                                    variant="secondary"
                                    className="text-xs"
                                    onClick={(e) => handleRemove(option.id, e)}
                                >
                                    {option.name}
                                    <X className="ml-1 h-3 w-3" />
                                </Badge>
                            ))}
                            {selectedOptions.length > 2 && (
                                <Badge variant="secondary" className="text-xs">
                                    +{selectedOptions.length - 2} lainnya
                                </Badge>
                            )}
                        </>
                    )}
                </div>
                <ChevronDown className="h-4 w-4 opacity-50" />
            </Button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-md">
                    {/* Search input */}
                    <div className="p-2 border-b">
                        <input
                            ref={inputRef}
                            type="text"
                            placeholder="Cari kategori..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    {/* Options list */}
                    <div className="max-h-60 overflow-y-auto">
                        {filteredOptions.length === 0 ? (
                            <div className="p-2 text-sm text-muted-foreground text-center">
                                Tidak ada kategori ditemukan
                            </div>
                        ) : (
                            filteredOptions.map((option) => {
                                const isSelected = value.includes(option.id);
                                return (
                                    <div
                                        key={option.id}
                                        className={cn(
                                            "flex items-center justify-between px-2 py-1.5 cursor-pointer hover:bg-accent hover:text-accent-foreground text-sm",
                                            isSelected && "bg-accent"
                                        )}
                                        onClick={() => handleToggle(option.id)}
                                    >
                                        <span>{option.name}</span>
                                        {isSelected && (
                                            <Check className="h-4 w-4" />
                                        )}
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
