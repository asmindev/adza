import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

export default function FoodTabs({
    activeTab,
    setActiveTab,
    allFoods,
    recommendedFoods,
    topRatedFoods,
    isLoading,
    toggleFavorite,
    favorites,
}) {
    return (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="all" className="flex items-center gap-2">
                    Semua Makanan
                </TabsTrigger>
                <TabsTrigger
                    value="recommended"
                    className="flex items-center gap-2"
                >
                    Rekomendasi
                </TabsTrigger>
                <TabsTrigger
                    value="top-rated"
                    className="flex items-center gap-2"
                >
                    Top Rated
                </TabsTrigger>
            </TabsList>

            <TabsContent value="all">
                <AllFoodsTab
                    foods={allFoods}
                    isLoading={isLoading}
                    onToggleFavorite={toggleFavorite}
                    favorites={favorites}
                />
            </TabsContent>

            <TabsContent value="recommended">
                <RecommendedTab
                    foods={recommendedFoods}
                    isLoading={isLoading}
                    onToggleFavorite={toggleFavorite}
                    favorites={favorites}
                />
            </TabsContent>

            <TabsContent value="top-rated">
                <TopRatedTab
                    foods={topRatedFoods}
                    isLoading={isLoading}
                    onToggleFavorite={toggleFavorite}
                    favorites={favorites}
                />
            </TabsContent>
        </Tabs>
    );
}

// Import the existing tab components
import AllFoodsTab from "../AllFoodsTab";
import RecommendedTab from "../RecommendedTab";
import TopRatedTab from "../TopRatedTab";
