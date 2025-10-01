import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UtensilsCrossed } from "lucide-react";

export default function EmptyState({ handleRefresh }) {
    return (
        <div className="flex flex-col justify-center items-center min-h-screen bg-gray-50">
            <Card className="max-w-md mx-auto shadow-lg border-none bg-white/90 backdrop-blur-sm">
                <CardHeader className="text-center">
                    <div className="flex justify-center mb-4">
                        <UtensilsCrossed className="w-20 h-20 text-gray-300 animate-pulse" />
                    </div>
                    <CardTitle className="text-2xl font-semibold text-gray-800">
                        No Recommendations Yet
                    </CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                    <p className="text-gray-500 text-base mb-6">
                        Start rating some foods to get personalized
                        recommendations tailored to your taste!
                    </p>
                    <Button
                        onClick={handleRefresh}
                        className="px-8 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 transform hover:scale-105"
                    >
                        Check Again
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
