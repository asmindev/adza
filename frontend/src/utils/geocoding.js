/**
 * Utility functions for geocoding operations
 */

/**
 * Reverse geocoding using OpenStreetMap Nominatim API
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<string|null>} - Address string or null if failed
 */
export const reverseGeocode = async (latitude, longitude) => {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`,
            {
                headers: {
                    "User-Agent": "Adza Restaurant App/1.0",
                },
            }
        );

        if (response.ok) {
            const data = await response.json();
            return data.display_name || null;
        }

        return null;
    } catch (error) {
        console.error("Reverse geocoding error:", error);
        return null;
    }
};

/**
 * Forward geocoding using OpenStreetMap Nominatim API
 * @param {string} address - Address string to geocode
 * @returns {Promise<{lat: number, lon: number}|null>} - Coordinates or null if failed
 */
export const forwardGeocode = async (address) => {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
                address
            )}&format=json&limit=1`,
            {
                headers: {
                    "User-Agent": "Adza Restaurant App/1.0",
                },
            }
        );

        if (response.ok) {
            const data = await response.json();
            if (data.length > 0) {
                return {
                    lat: parseFloat(data[0].lat),
                    lon: parseFloat(data[0].lon),
                };
            }
        }

        return null;
    } catch (error) {
        console.error("Forward geocoding error:", error);
        return null;
    }
};

/**
 * Debounced reverse geocoding with confirmation dialog
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @param {Function} onAddressFound - Callback when address is found and confirmed
 * @param {Function} onError - Callback when error occurs
 * @param {Function} onLoading - Callback to handle loading state
 * @param {number} debounceMs - Debounce delay in milliseconds
 */
export const reverseGeocodeWithConfirmation = async (
    latitude,
    longitude,
    onAddressFound,
    onError,
    onLoading,
    debounceMs = 1000
) => {
    // Clear any existing timeout
    if (window.geocodingTimeout) {
        clearTimeout(window.geocodingTimeout);
    }

    // Set new timeout
    window.geocodingTimeout = setTimeout(async () => {
        onLoading(true);

        try {
            const address = await reverseGeocode(latitude, longitude);

            if (address) {
                // Show confirmation dialog
                const useAddress = window.confirm(
                    `Alamat ditemukan: "${address}"\n\nApakah Anda ingin menggunakan alamat ini?`
                );

                if (useAddress) {
                    onAddressFound(address);
                }
            } else {
                onError("Tidak dapat menemukan alamat untuk koordinat ini");
            }
        } catch (error) {
            console.error("Reverse geocoding with confirmation error:", error);
            onError("Gagal mendapatkan alamat dari koordinat");
        } finally {
            onLoading(false);
        }
    }, debounceMs);
};
