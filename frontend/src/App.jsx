import React from "react";
import { RouterProvider } from "react-router/dom";
import UserProvider from "@/contexts/UserContext";
import { Toaster } from "sonner";
import { SWRConfig } from "swr";
import router from "./routes";
const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;

// Create the router configuration with React Router v7
export default function App() {
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
