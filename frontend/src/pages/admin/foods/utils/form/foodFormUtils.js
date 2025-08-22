/**
 * Form utilities for food management
 */

/**
 * Default form values for food forms
 */
export const defaultFoodFormValues = {
    name: "",
    description: "",
    category: "",
    price: 0,
    restaurant_id: "",
    ingredients: [],
    status: "active",
};

/**
 * Maps food data to form values
 * @param {object} foodData - Food data from API
 * @returns {object} - Form values
 */
export const mapFoodDataToFormValues = (foodData) => {
    if (!foodData) return defaultFoodFormValues;

    return {
        name: foodData.name || "",
        description: foodData.description || "",
        category: foodData.category || "",
        price: foodData.price || 0,
        restaurant_id: foodData.restaurant_id || "",
        ingredients: foodData.ingredients || [],
        status: foodData.status || "active",
    };
};

/**
 * Validates required fields for food form
 * @param {object} data - Form data
 * @param {boolean} hasImages - Whether images are present
 * @returns {object} - { isValid, errors }
 */
export const validateFoodForm = (data, hasImages = true) => {
    const errors = [];

    if (!data.name?.trim()) {
        errors.push("Nama makanan harus diisi");
    }

    if (!data.restaurant_id) {
        errors.push("Silakan pilih restoran");
    }

    if (hasImages && !hasImages) {
        errors.push("Silakan tambahkan minimal satu gambar");
    }

    if (!data.category?.trim()) {
        errors.push("Kategori harus diisi");
    }

    if (!data.price || data.price <= 0) {
        errors.push("Harga harus lebih dari 0");
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};

/**
 * Status options for food
 */
export const foodStatusOptions = [
    { value: "active", label: "Aktif" },
    { value: "inactive", label: "Tidak Aktif" },
    { value: "pending", label: "Tertunda" },
];
