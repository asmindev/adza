import UserProfile from "@/pages/profile/UserProfile";
import FoodsPage from "@/pages/admin/foods/FoodsPage";
import DashboardLayout from "@/layout/AdminLayout";
import UsersPage from "@/pages/admin/users/UsersPage";
import DashboardPage from "@/pages/admin/dashboard/DashboardPage";
import RestaurantsPage from "@/pages/admin/restaurants/RestaurantsPage";
import SettingsPage from "@/pages/admin/settings";
import { userContext } from "@/contexts/context";
import adminMiddleware from "@/middleware/admin_middleware";

const ADMIN_ROUTES = [
    {
        unstable_middleware: [adminMiddleware],
        path: "/dashboard",
        Component: DashboardLayout,
        loader: userLoader,
        children: [
            {
                index: true,
                Component: DashboardPage,
            },
            {
                path: "foods",
                Component: FoodsPage,
            },
            {
                path: "users",
                Component: UsersPage,
            },
            {
                path: "restaurants",
                Component: RestaurantsPage,
            },
            {
                path: "settings",
                Component: SettingsPage,
            },

            {
                path: "profile",
                Component: UserProfile,
            },
        ],
    },
];

async function timingMiddleware({ context }, next) {
    await next();
}

async function userLoader({ context }) {
    const user = context.get(userContext);
    console.log("Loaded user:", user);
    return user;
}

export default ADMIN_ROUTES;
