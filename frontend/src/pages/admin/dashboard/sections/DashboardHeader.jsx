import React from "react";

export default function DashboardHeader() {
    return (
        <div className="flex flex-col md:flex-row justify-between items-center">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
                Selamat datang di dashboard manajemen makanan Anda
            </p>
        </div>
    );
}
