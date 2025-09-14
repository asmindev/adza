import RootLayout from "@/layout/RootLayout";
import Login from "@/pages/auth/Login";
import FoodDetailPage from "@/pages/detail/FoodDetailPage";
import Home from "@/pages/home/Home";
import Recommendation from "@/pages/recommendation/page";
import RouteNavigationPage from "@/pages/navigation/RouteNavigationPage";
import UserProfile from "@/pages/profile/UserProfile";
import RestaurantDetail from "@/pages/restaurants/detail/RestaurantDetail";
import RestaurantDetailPage from "@/pages/restaurants/detail/RestaurantDetailPage";
import RestaurantsPage from "@/pages/restaurants/RestaurantsPage";
import Popular from "@/pages/popular/page";
import onboardingMiddleware from "@/middleware/onboarding_middleware";
import OnboardingPage from "@/pages/onboarding/page";
import Register from "@/pages/auth/Register";
import auth, { profileLoader } from "@/middleware/authenticated_middleware";
import NotFound from "@/pages/NotFound";

const REGULAR_ROUTES = [
    {
        unstable_middleware: [auth],
        path: "/login",
        loader: profileLoader,
        Component: Login,
    },
    {
        unstable_middleware: [auth],
        loader: profileLoader,
        path: "/register",
        Component: Register,
    },
    {
        path: "/",
        Component: RootLayout,
        unstable_middleware: [onboardingMiddleware],
        // loader: userLoader,
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

            { path: "recommendation", Component: Recommendation },
            { path: "popular", Component: Popular },
            { path: "preferences", Component: OnboardingPage },
        ],
    },
    // 404 Catch-all route
    {
        path: "*",
        Component: NotFound,
    },
];

export default REGULAR_ROUTES;
