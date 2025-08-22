import React from "react";
import { Button } from "@/components/ui/button";

export default function FoodPagination({ pagination, page, setPage }) {
    if (pagination.total_pages <= 1) {
        return null;
    }

    return (
        <div className="flex items-center justify-between space-x-2 py-4">
            <p className="text-sm text-muted-foreground">
                Halaman {pagination.current_page} dari {pagination.total_pages}{" "}
                ({pagination.total} total)
            </p>
            <div className="space-x-2">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                >
                    Sebelumnya
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= pagination.total_pages}
                >
                    Selanjutnya
                </Button>
            </div>
        </div>
    );
}
