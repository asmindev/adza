import useSWR, { mutate } from "swr";
import useSWRMutation from "swr/mutation";

const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;
// Helper for API requests that need token auth
export const fetchWithToken = async (url, options = {}) => {
    const token = localStorage.getItem("token");

    const headers = {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...(options.headers || {}),
    };

    const response = await fetch(`${BASE_API_URL}${url}`, {
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

    const response = await fetch(`${BASE_API_URL}${url}`, {
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

// Custom hooks
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
            const response = await fetch(url, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(arg),
                credentials: "include",
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || "Failed to update profile");
            }

            return response.json();
        },
        {
            onSuccess: () => {
                // Revalidate user profile data after successful update
                mutate("/api/v1/me");
            },
        }
    );
}
