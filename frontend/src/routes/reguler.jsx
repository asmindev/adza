import RootLayout from "@/layout/RootLayout";
import Login from "@/pages/auth/Login";
import FoodDetailPage from "@/pages/detail/FoodDetailPage";
import Home from "@/pages/home/Home";
import RouteNavigationPage from "@/pages/navigation/RouteNavigationPage";
import UserProfile from "@/pages/profile/UserProfile";
import RestaurantDetail from "@/pages/restaurants/detail/RestaurantDetail";
import RestaurantDetailPage from "@/pages/restaurants/detail/RestaurantDetailPage";
import RestaurantsPage from "@/pages/restaurants/RestaurantsPage";

const REGULAR_ROUTES = [
    {
        Component: RootLayout,
        children: [
            {
                path: "/",
                index: true,
                Component: Home,
            },
            {
                path: "profile",
                Component: UserProfile,
            },
            {
                path: "food/:id",
                Component: FoodDetailPage,
            },
            {
                path: "restaurants",
                Component: RestaurantsPage,
            },
            {
                path: "restaurant/:id",
                Component: RestaurantDetailPage,
            },
            {
                path: "navigation/restaurant/:restaurantId",
                Component: RouteNavigationPage,
            },
            {
                path: "navigation/food/:foodId",
                Component: RouteNavigationPage,
            },
        ],
    },
    {
        path: "/login",
        Component: Login,
    },
];

export default REGULAR_ROUTES;
