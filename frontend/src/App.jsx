import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router";
import UserProvider from "@/contexts/UserContext";
import RootLayout from "@/layout/RootLayout";
import DashboardLayout from "@/layout/AdminLayout";
import FoodDetailPage from "@/pages/detail/FoodDetailPage";
import RestaurantDetailPage from "@/pages/restaurants/detail/RestaurantDetailPage";
import RestaurantsPage from "@/pages/restaurants/RestaurantsPage";
import RouteNavigationPage from "@/pages/navigation/RouteNavigationPage";
import DashboardPage from "@/pages/admin/dashboard/DashboardPage";
import Login from "./pages/auth/Login";
import { Toaster } from "sonner";
import { SWRConfig } from "swr";
import UserProfile from "./pages/profile/UserProfile";
import FoodsPage from "./pages/admin/foods/FoodsPage";
import UsersPage from "./pages/admin/users/UsersPage";
import AdminRestaurantsPage from "./pages/admin/restaurants/RestaurantsPage";
import SettingsPage from "./pages/admin/settings/SettingsPage";
import Home from "./pages/home/Home";
const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;

// Create the router configuration with React Router v7
export default function App() {
    // Create routes using the declarative API
    const router = createBrowserRouter([
        {
            path: "/",
            element: (
                <RootLayout>
                    <Home />
                </RootLayout>
            ),
        },
        {
            path: "/restaurants",
            element: (
                <RootLayout>
                    <RestaurantsPage />
                </RootLayout>
            ),
        },
        {
            path: "/food/:id",
            element: (
                <RootLayout>
                    <FoodDetailPage />
                </RootLayout>
            ),
        },
        {
            path: "/restaurant/:id",
            element: (
                <RootLayout>
                    <RestaurantDetailPage />
                </RootLayout>
            ),
        },
        {
            path: "/navigation/restaurant/:restaurantId",
            element: (
                <RootLayout>
                    <RouteNavigationPage />
                </RootLayout>
            ),
        },
        {
            path: "/navigation/food/:foodId",
            element: (
                <RootLayout>
                    <RouteNavigationPage />
                </RootLayout>
            ),
        },
        {
            path: "/dashboard",
            element: (
                <DashboardLayout>
                    <DashboardPage />
                </DashboardLayout>
            ),
        },
        {
            path: "/dashboard/foods",
            element: (
                <DashboardLayout>
                    <FoodsPage />
                </DashboardLayout>
            ),
        },
        {
            path: "/dashboard/users",
            element: (
                <DashboardLayout>
                    <UsersPage />
                </DashboardLayout>
            ),
        },
        {
            path: "/dashboard/restaurants",
            element: (
                <DashboardLayout>
                    <AdminRestaurantsPage />
                </DashboardLayout>
            ),
        },
        {
            path: "/dashboard/settings",
            element: (
                <DashboardLayout>
                    <SettingsPage />
                </DashboardLayout>
            ),
        },
        {
            path: "/login",
            element: <Login />,
        },
        {
            path: "/profile",
            element: (
                <RootLayout>
                    <UserProfile />
                </RootLayout>
            ),
        },
    ]);

    return (
        <>
            <SWRConfig
                value={{
                    revalidateOnFocus: false,
                    revalidateOnReconnect: false,
                    refreshWhenOffline: false,
                    refreshWhenHidden: false,
                    refreshInterval: 0,
                    shouldRetryOnError: false,
                    errorRetryCount: 3,
                    onErrorRetry: (
                        error,
                        key,
                        config,
                        revalidate,
                        { retryCount }
                    ) => {
                        // Don't retry on 404s
                        if (error.status === 404) return;

                        // Only retry up to 3 times
                        if (retryCount >= 3) return;
                    },
                    fetcher: (resource, init) => {
                        // Get authentication token from localStorage
                        const token = localStorage.getItem("token");

                        // Create headers
                        const headers = {
                            "Content-Type": "application/json",
                            ...(token && { Authorization: `Bearer ${token}` }),
                            ...(init?.headers || {}),
                        };

                        return fetch(`${BASE_API_URL}${resource}`, {
                            ...init,
                            headers,
                        }).then(async (res) => {
                            // Handle unauthorized responses
                            if (res.status === 401) {
                                localStorage.removeItem("user");
                                localStorage.removeItem("token");
                                // Only redirect if not already on the login page
                                if (
                                    !window.location.pathname.includes("/login")
                                ) {
                                    window.location.href = "/login";
                                }
                                throw new Error("Autentikasi diperlukan");
                            }

                            // Handle 404 Not Found errors
                            if (res.status === 404) {
                                const error = new Error(
                                    "Resource tidak ditemukan"
                                );
                                error.status = 404;
                                throw error;
                            }

                            // Try to parse response as JSON
                            let data;
                            try {
                                data = await res.json();
                            } catch {
                                // If JSON parsing fails, create an error with the status
                                const error = new Error(
                                    "Format respons tidak valid"
                                );
                                error.status = res.status;
                                throw error;
                            }

                            // Handle API errors
                            if (!res.ok) {
                                const error = new Error(
                                    data.message || "Terjadi kesalahan"
                                );
                                error.status = res.status;
                                error.info = data;
                                throw error;
                            }

                            return data;
                        });
                    },
                }}
            >
                <UserProvider>
                    <Toaster />
                    <RouterProvider router={router} />
                </UserProvider>
            </SWRConfig>
        </>
    );
}
