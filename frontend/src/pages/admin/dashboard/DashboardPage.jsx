import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import useSWR from "swr";

// Import sections
import DashboardHeader from "./sections/DashboardHeader";
import StatsSection from "./sections/StatsSection";
import ChartsSection from "./sections/ChartsSection";
import QuickActionsSection from "./sections/QuickActionsSection";

export default function DashboardPage() {
    const {
        data: statsData,
        isLoading,
        error,
    } = useSWR("/api/v1/dashboard/stats");

    // Use error state to conditionally show an error message or fallback data
    const stats = error
        ? {
              totalFoods: 0,
              totalUsers: 0,
              totalReviews: 0,
              averageRating: 0,
              error: true,
          }
        : statsData?.data || {
              totalFoods: 0,
              totalUsers: 0,
              totalReviews: 0,
              averageRating: 0,
          };

    return (
        <div className="space-y-6 w-full">
            {/* Dashboard Header */}
            <DashboardHeader />

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Ikhtisar</TabsTrigger>
                    <TabsTrigger value="actions">Tindakan Cepat</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    {/* Stats Section */}
                    <StatsSection stats={stats} />

                    {/* Charts Section */}
                    <ChartsSection isLoading={isLoading} stats={stats} />
                </TabsContent>

                <TabsContent value="actions" className="space-y-4">
                    {/* Quick Actions Section */}
                    <QuickActionsSection />
                </TabsContent>
            </Tabs>
        </div>
    );
}

const breadcrumbs = [{ label: "Dashboard" }];

DashboardPage.breadcrumbs = breadcrumbs;
