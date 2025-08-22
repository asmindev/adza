import axios from "axios";

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
                console.error("Unauthorized access");
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

// API service with methods organized by domain
const apiService = {
    // Dashboard
    dashboard: {
        getStats: () => apiClient.get("/dashboard/stats"),
        getTopRatedFoods: () => apiClient.get("/recommendations/top-rated"),
        getRecentActivity: () => apiClient.get("/dashboard/recent-activity"),
    },

    // Foods
    foods: {
        getAll: (page = 1, limit = 10, search = "") =>
            apiClient.get(
                `/api/v1/foods?page=${page}&limit=${limit}&search=${search}`
            ),
        getById: (id) => apiClient.get(`/api/v1/foods/${id}`),
        create: (data) => {
            // kalau ada images, maka gunakan formData
            if (data.images) {
                console.log("data", data);
                const formData = new FormData();
                formData.append("name", data.name);
                formData.append("description", data.description);
                formData.append("price", data.price);
                formData.append("category", data.category_id);

                for (let i = 0; i < data.images.length; i++) {
                    formData.append("images", data.images[i].file);
                }
                console.log("formData", formData);
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
                // formData.append("name", data.name);
                // formData.append("description", data.description);
                // formData.append("price", data.price);
                // formData.append("category", data.category);
                // formData.append("status", data.status);
                delete data.images; // remove images from data
                Object.keys(data).forEach((key) => {
                    formData.append(key, data[key]);
                });
                console.log("formData", formData);

                apiClient.put(`/api/v1/foods/${id}`, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                });
            } else {
                apiClient.put(`/api/v1/foods/${id}`, data);
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
};

export default apiService;
