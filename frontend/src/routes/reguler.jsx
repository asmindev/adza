import RootLayout from "@/layout/RootLayout";
import Login from "@/pages/auth/Login";
import FoodDetailPage from "@/pages/detail/FoodDetailPage";
import Home from "@/pages/home/Home";
import RouteNavigationPage from "@/pages/navigation/RouteNavigationPage";
import UserProfile from "@/pages/profile/UserProfile";
import RestaurantDetailPage from "@/pages/restaurants/detail/RestaurantDetailPage";

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
                path: "restaurants/:id",
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
