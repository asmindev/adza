// Map Service untuk menangani lokasi dan routing dengan rate limiting
class MapService {
    constructor() {
        this.baseUrl = "https://router.project-osrm.org";
        this.geocodingUrl = "https://nominatim.openstreetmap.org";

        // Rate limiting
        this.lastRequestTime = 0;
        this.minRequestInterval = 1000; // 1 detik minimum antara request
        this.requestQueue = [];
        this.isProcessingQueue = false;
    }

    /**
     * Rate limiting helper
     */
    async rateLimitedRequest(requestFn) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ requestFn, resolve, reject });
            this.processQueue();
        });
    }

    async processQueue() {
        if (this.isProcessingQueue || this.requestQueue.length === 0) {
            return;
        }

        this.isProcessingQueue = true;

        while (this.requestQueue.length > 0) {
            const now = Date.now();
            const timeSinceLastRequest = now - this.lastRequestTime;

            if (timeSinceLastRequest < this.minRequestInterval) {
                const waitTime = this.minRequestInterval - timeSinceLastRequest;
                await new Promise((resolve) => setTimeout(resolve, waitTime));
            }

            const { requestFn, resolve, reject } = this.requestQueue.shift();
            this.lastRequestTime = Date.now();

            try {
                const result = await requestFn();
                resolve(result);
            } catch (error) {
                reject(error);
            }
        }

        this.isProcessingQueue = false;
    }

    /**
     * Mendapatkan lokasi pengguna saat ini
     * @returns {Promise<{lat: number, lng: number}>}
     */
    async getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(
                    new Error("Geolocation tidak didukung oleh browser ini")
                );
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    });
                },
                (error) => {
                    let errorMessage = "Tidak dapat mengakses lokasi";
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = "Akses lokasi ditolak oleh pengguna";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = "Informasi lokasi tidak tersedia";
                            break;
                        case error.TIMEOUT:
                            errorMessage = "Permintaan lokasi timeout";
                            break;
                    }
                    reject(new Error(errorMessage));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000, // Increase timeout to 10 seconds
                    maximumAge: 60000, // Cache location for 1 minute
                }
            );
        });
    }

    /**
     * Mencari rute dari lokasi asal ke tujuan menggunakan OSRM dengan rate limiting
     * @param {number} fromLat - Latitude asal
     * @param {number} fromLng - Longitude asal
     * @param {number} toLat - Latitude tujuan
     * @param {number} toLng - Longitude tujuan
     * @returns {Promise<Object>} Data rute
     */
    async getRoute(fromLat, fromLng, toLat, toLng) {
        return this.rateLimitedRequest(async () => {
            try {
                const url = `${this.baseUrl}/route/v1/driving/${fromLng},${fromLat};${toLng},${toLat}?overview=full&geometries=geojson&steps=true`;

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

                const response = await fetch(url, {
                    signal: controller.signal,
                    mode: "cors",
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(
                        `HTTP ${response.status}: Gagal mendapatkan rute`
                    );
                }

                const data = await response.json();

                if (
                    data.code !== "Ok" ||
                    !data.routes ||
                    data.routes.length === 0
                ) {
                    throw new Error("Tidak ada rute yang ditemukan");
                }

                const route = data.routes[0];
                return {
                    coordinates: route.geometry.coordinates,
                    distance: route.distance, // dalam meter
                    duration: route.duration, // dalam detik
                    steps: route.legs[0]?.steps || [],
                    geometry: route.geometry,
                };
            } catch (error) {
                if (error.name === "AbortError") {
                    throw new Error("Permintaan timeout, silakan coba lagi");
                }
                console.error("Error getting route:", error);
                throw error;
            }
        });
    }

    /**
     * Geocoding - mengkonversi alamat menjadi koordinat dengan rate limiting
     * @param {string} address - Alamat yang akan dikonversi
     * @returns {Promise<Array>} Array hasil geocoding
     */
    async geocodeAddress(address) {
        return this.rateLimitedRequest(async () => {
            try {
                const encodedAddress = encodeURIComponent(address);
                const url = `${this.geocodingUrl}/search?format=json&q=${encodedAddress}&limit=5&countrycodes=id`;

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 10000);

                const response = await fetch(url, {
                    signal: controller.signal,
                    headers: {
                        "User-Agent": "FoodRecommendationApp/1.0",
                    },
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error("Gagal melakukan geocoding");
                }

                const data = await response.json();
                return data.map((item) => ({
                    lat: parseFloat(item.lat),
                    lng: parseFloat(item.lon),
                    displayName: item.display_name,
                    address: item.address,
                }));
            } catch (error) {
                if (error.name === "AbortError") {
                    throw new Error("Permintaan timeout, silakan coba lagi");
                }
                console.error("Error geocoding address:", error);
                throw error;
            }
        });
    }

    /**
     * Reverse geocoding - mengkonversi koordinat menjadi alamat dengan rate limiting
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @returns {Promise<Object>} Informasi alamat
     */
    async reverseGeocode(lat, lng) {
        return this.rateLimitedRequest(async () => {
            try {
                const url = `${this.geocodingUrl}/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18`;

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 10000);

                const response = await fetch(url, {
                    signal: controller.signal,
                    headers: {
                        "User-Agent": "FoodRecommendationApp/1.0",
                    },
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error("Gagal melakukan reverse geocoding");
                }

                const data = await response.json();
                return {
                    displayName: data.display_name,
                    address: data.address,
                };
            } catch (error) {
                if (error.name === "AbortError") {
                    throw new Error("Permintaan timeout, silakan coba lagi");
                }
                console.error("Error reverse geocoding:", error);
                throw error;
            }
        });
    }

    /**
     * Format durasi dari detik ke format yang dapat dibaca
     * @param {number} seconds - Durasi dalam detik
     * @returns {string} Durasi yang diformat
     */
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (hours > 0) {
            return `${hours} jam ${minutes} menit`;
        }
        return `${minutes} menit`;
    }

    /**
     * Format jarak dari meter ke format yang dapat dibaca
     * @param {number} meters - Jarak dalam meter
     * @returns {string} Jarak yang diformat
     */
    formatDistance(meters) {
        if (meters >= 1000) {
            return `${(meters / 1000).toFixed(1)} km`;
        }
        return `${Math.round(meters)} m`;
    }

    /**
     * Menghitung jarak antara dua titik (Haversine formula)
     * @param {number} lat1 - Latitude titik 1
     * @param {number} lng1 - Longitude titik 1
     * @param {number} lat2 - Latitude titik 2
     * @param {number} lng2 - Longitude titik 2
     * @returns {number} Jarak dalam meter
     */
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371000; // Radius bumi dalam meter
        const φ1 = (lat1 * Math.PI) / 180;
        const φ2 = (lat2 * Math.PI) / 180;
        const Δφ = ((lat2 - lat1) * Math.PI) / 180;
        const Δλ = ((lng2 - lng1) * Math.PI) / 180;

        const a =
            Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }
}

export default new MapService();
