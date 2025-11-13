import React from "react";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

export default function PageSizeSelector({ pageSize, onPageSizeChange }) {
    const pageSizeOptions = [5, 10, 20, 50, 100];

    return (
        <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Tampilkan:</span>
            <Select
                value={pageSize.toString()}
                onValueChange={(value) => onPageSizeChange(Number(value))}
            >
                <SelectTrigger className="w-[80px]">
                    <SelectValue placeholder={pageSize} />
                </SelectTrigger>
                <SelectContent>
                    {pageSizeOptions.map((size) => (
                        <SelectItem key={size} value={size.toString()}>
                            {size}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <span className="text-sm text-muted-foreground">
                data per halaman
            </span>
        </div>
    );
}
