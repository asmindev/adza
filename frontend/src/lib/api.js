import axios from "axios";
import useSWR, { mutate } from "swr";
import useSWRMutation from "swr/mutation";

const API_BASE_URL = import.meta.env.VITE_BASE_API_URL || "/api/v1";

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Add request interceptor for auth
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle common errors (401, 403, etc)
        if (error.response) {
            if (error.response.status === 401) {
                // Redirect to login or refresh token
                localStorage.removeItem("user");
                localStorage.removeItem("token");
                console.error("Unauthorized access");
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

// Helper for API requests that need token auth (for SWR)
export const fetchWithToken = async (url, options = {}) => {
    const token = localStorage.getItem("token");

    const headers = {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...(options.headers || {}),
    };

    const response = await fetch(`${API_BASE_URL}${url}`, {
        method: "GET", // Default to GET for SWR
        ...options,
        headers,
    });

    // Handle unauthorized
    if (response.status === 401) {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        window.location.href = "/login";
        throw new Error("Unauthorized - Please log in again");
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || "API request failed");
    }

    return data;
};

// Custom mutation function for POST requests
async function sendRequest(url, { arg }) {
    return fetchWithToken(url, {
        method: "POST",
        body: JSON.stringify(arg),
    });
}

// Helper for making authenticated API requests with mutation
async function fetchWithAuth(url, { arg }) {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_BASE_URL}${url}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(arg),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || "API request failed");
    }

    return data;
}

// API service with methods organized by domain (using axios)
export const apiService = {
    // Dashboard
    dashboard: {
        getStats: () => apiClient.get("/dashboard/stats"),
        getTopRatedFoods: () => apiClient.get("/recommendation/popular"),
        getRecentActivity: () => apiClient.get("/dashboard/recent-activity"),
    },

    // Foods
    foods: {
        getAll: (page = 1, limit = 10, search = "") =>
            apiClient.get(
                `/api/v1/foods?page=${page}&limit=${limit}&search=${search}`
            ),
        getRecommendation: () => apiClient.get("/api/v1/recommendation"),
        getPopular: () => apiClient.get("/api/v1/popular"),
        getById: (id) => apiClient.get(`/api/v1/foods/${id}`),
        create: (data) => {
            // kalau ada images, maka gunakan formData
            if (data.images) {
                const formData = new FormData();
                formData.append("name", data.name);
                formData.append("description", data.description);
                formData.append("price", data.price);
                formData.append("category", data.category_id);

                for (let i = 0; i < data.images.length; i++) {
                    formData.append("images", data.images[i].file);
                }
                return apiClient.post("/api/v1/foods", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                });
            }
            // kalau tidak ada images, maka gunakan json
            return apiClient.post("/api/v1/foods", data);
        },
        update: (id, data) => {
            if (data.images) {
                const formData = new FormData();
                data.images?.new_images?.map((img) =>
                    formData.append("new_images", img.file)
                );
                data.images?.deleted_image_ids?.map((id) =>
                    formData.append("deleted_image_ids", id)
                );
                delete data.images; // remove images from data
                Object.keys(data).forEach((key) => {
                    formData.append(key, data[key]);
                });
                console.log("formData", formData);

                return apiClient.put(`/api/v1/foods/${id}`, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                });
            } else {
                return apiClient.put(`/api/v1/foods/${id}`, data);
            }
        },
        delete: (id) => apiClient.delete(`/api/v1/foods/${id}`),
    },

    // Users
    users: {
        getAll: (page = 1, limit = 50, search = "") =>
            apiClient.get(
                `/api/v1/users?page=${page}&limit=${limit}&search=${search}`
            ),
        getById: (id) => apiClient.get(`/api/v1/users/${id}`),
        getMe: () => apiClient.get("/api/v1/me"),
        create: (data) => apiClient.post("/api/v1/users", data),
        update: (id, data) => apiClient.put(`/api/v1/users/${id}`, data),
        delete: (id) => apiClient.delete(`/api/v1/users/${id}`),
    },

    // Restaurants
    restaurants: {
        getAll: (page = 1, limit = 10, search = "") =>
            apiClient.get(
                `/api/v1/restaurants?page=${page}&limit=${limit}&search=${search}`
            ),
        getById: (id) => apiClient.get(`/api/v1/restaurants/${id}`),
        create: (data) => apiClient.post("/api/v1/restaurants", data),
        update: (id, data) => apiClient.put(`/api/v1/restaurants/${id}`, data),
        delete: (id) => apiClient.delete(`/api/v1/restaurants/${id}`),
    },

    // Reviews
    reviews: {
        getByFood: (foodId) => apiClient.get(`/api/v1/foods/${foodId}/reviews`),
        create: (foodId, data) =>
            apiClient.post(`/api/v1/foods/${foodId}/reviews`, data),
        delete: (id) => apiClient.delete(`/api/v1/reviews/${id}`),
    },

    // Categories
    categories: {
        getAll: (includeStats = false) =>
            apiClient.get(`/api/v1/categories?include_stats=${includeStats}`),
        getById: (id) => apiClient.get(`/api/v1/categories/${id}`),
        getMostFavorite: (limit = 10) =>
            apiClient.get(`/api/v1/categories/most-favorite?limit=${limit}`),
        create: (data) => apiClient.post("/api/v1/categories", data),
        update: (id, data) => apiClient.put(`/api/v1/categories/${id}`, data),
        delete: (id) => apiClient.delete(`/api/v1/categories/${id}`),
    },

    // User favorite categories
    userFavoriteCategories: {
        getMyFavorites: () => apiClient.get("/api/v1/me/favorite-categories"),
        addFavorites: (categoryIds) => {
            console.log("Adding favorites", categoryIds);
            return apiClient.post("/api/v1/me/favorite-categories", {
                category_ids: categoryIds,
            });
        },
        removeFromFavorites: (categoryId) =>
            apiClient.delete(`/api/v1/me/favorite-categories/${categoryId}`),
        checkIsFavorite: (categoryId) =>
            apiClient.get(`/api/v1/me/favorite-categories/${categoryId}/check`),
    }, // User onboarding
    onboarding: {
        complete: () => apiClient.put("/api/v1/me/onboarding"),
    },
};

// SWR Custom hooks
export function useAuthenticatedSWR(key) {
    return useSWR(key, null); // Uses the global fetcher from SWRConfig
}

export function useAuthenticatedMutation(key) {
    return useSWRMutation(key, sendRequest);
}

// Custom hooks for food-related mutations
export function useRateFood() {
    return useSWRMutation(`/api/v1/ratings`, fetchWithAuth);
}

export function useSubmitReview() {
    return useSWRMutation(`/api/v1/reviews`, fetchWithAuth);
}

export function useToggleFavorite(foodId) {
    return useSWRMutation(`/api/v1/foods/${foodId}/favorite`, fetchWithAuth);
}

// Profile API hooks
export function useUpdateProfile() {
    return useSWRMutation(
        "/api/v1/me",
        async (url, { arg }) => {
            // Try to get user ID from localStorage first
            const storedUser = localStorage.getItem("user");
            let userId;

            if (storedUser) {
                try {
                    const user = JSON.parse(storedUser);
                    userId = user.id;
                } catch (error) {
                    console.warn("Failed to parse stored user data:", error);
                }
            }

            // If no user ID in localStorage, fetch from API
            if (!userId) {
                const currentUserResponse = await apiService.users.getMe();
                userId = currentUserResponse.data.id;

                if (!userId) {
                    throw new Error("User ID not found. Please log in again.");
                }
            }

            // Use the apiService users.update method with the user ID
            const response = await apiService.users.update(userId, arg);
            return response;
        },
        {
            onSuccess: () => {
                // Revalidate user profile data after successful update
                mutate("/api/v1/me");
            },
        }
    );
}

// Export default as the main API service
export default apiService;
