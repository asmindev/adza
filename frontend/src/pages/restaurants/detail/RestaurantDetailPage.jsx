import React from "react";
import { useParams } from "react-router";
import RestaurantDetail from "./RestaurantDetail";

export default function RestaurantDetailPage() {
    const params = useParams();
    const id = params.id;

    return <RestaurantDetail restaurantId={id} />;
}