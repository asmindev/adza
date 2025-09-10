import React, { useState, useEffect } from "react";
import { UserContext } from "./UserContextDefinition";
import { toast } from "sonner";

export default function UserProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check if user is already logged in (from localStorage) when the app loads
    useEffect(() => {
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (error) {
                console.error("Failed to parse stored user data:", error);
                localStorage.removeItem("user");
                localStorage.removeItem("token");
            }
        }
        setLoading(false);
    }, []);

    // Login function that now makes an actual API call
    const login = async (credentials) => {
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BASE_API_URL}/api/v1/auth/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(credentials),
                }
            );

            const result = await response.json();

            if (response.ok) {
                // Extract user data and token from the response
                const { user, token } = result.data;

                // Store user and token in state and localStorage
                setUser(user);
                localStorage.setItem("user", JSON.stringify(user));
                localStorage.setItem("token", token);

                toast.success("Login successful!");
                return { success: true };
            } else {
                return {
                    success: false,
                    message: result.message || "Login failed",
                };
            }
        } catch (error) {
            console.error("Login error:", error);
            return {
                success: false,
                message: "An error occurred during login",
            };
        }
    };

    // Logout function
    const logout = () => {
        console.log("User logged out");

        setUser(null);

        localStorage.removeItem("user");
        localStorage.removeItem("token");
        console.log("User logged out");

        // Call logout API if needed
        // AuthApi.logout();

        return { success: true };
    };

    // Register function (for future implementation)
    const register = async (userData) => {
        try {
            // This would be replaced with an actual API call in a real application
            // Example: const response = await api.post('/auth/register', userData);

            // Simulating an API response
            const mockRegisterCall = () => {
                return new Promise((resolve) => {
                    setTimeout(() => {
                        // For demo purposes, always succeed
                        resolve({
                            success: true,
                            user: {
                                id: "2",
                                username: userData.username,
                                name: userData.name || "New User",
                            },
                        });
                    }, 800);
                });
            };

            const response = await mockRegisterCall();

            if (response.success) {
                setUser(response.user);
                localStorage.setItem("user", JSON.stringify(response.user));
                return { success: true };
            } else {
                return {
                    success: false,
                    message: response.message || "Registration failed",
                };
            }
        } catch (error) {
            console.error("Registration error:", error);
            return {
                success: false,
                message: "An error occurred during registration",
            };
        }
    };

    // Check if user is authenticated
    const isAuthenticated = () => {
        return !!user;
    };

    // The context value that will be provided
    const contextValue = {
        user,
        setUser,
        loading,
        login,
        logout,
        register,
        isAuthenticated,
    };

    return (
        <UserContext.Provider value={contextValue}>
            {children}
        </UserContext.Provider>
    );
}
