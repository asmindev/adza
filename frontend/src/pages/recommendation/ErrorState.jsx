import React from "react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Link } from "react-router";

export default function ErrorState({ error, handleRefresh }) {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center pb-4">
                    <div className="flex justify-center mb-4">
                        <div className="p-3 bg-red-100 rounded-full">
                            <AlertTriangle className="w-8 h-8 text-red-600" />
                        </div>
                    </div>
                    <CardTitle className="text-xl font-semibold text-gray-900">
                        Tidak Dapat Memuat Rekomendasi
                    </CardTitle>
                </CardHeader>

                <CardContent className="text-center space-y-4">
                    <p className="text-gray-600 text-sm">
                        Tidak ada rekomendasi yang ditemukan.
                    </p>
                </CardContent>
                <CardFooter className="text-center flex justify-center pt-0">
                    <Button
                        onClick={handleRefresh}
                        className="flex items-center justify-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Try again
                    </Button>
                    <Link to="/popular">
                        <Button
                            variant="outline"
                            className="w-full ml-2 flex items-center justify-center gap-2"
                        >
                            See Popular Foods
                        </Button>
                    </Link>
                </CardFooter>
            </Card>
        </div>
    );
}
