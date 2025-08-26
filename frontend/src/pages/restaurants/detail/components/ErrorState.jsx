import React from "react";
import { Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function ErrorState() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-background">
            <Card className="text-center p-8 max-w-md">
                <CardContent className="space-y-4">
                    <h2 className="text-2xl font-bold text-foreground">
                        Restaurant Not Found
                    </h2>
                    <p className="text-muted-foreground">
                        The restaurant you're looking for doesn't exist or has
                        been removed.
                    </p>
                    <Button asChild>
                        <Link to="/">
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Back to Home
                        </Link>
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}

export default ErrorState;
