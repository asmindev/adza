import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    ArrowLeft,
    MapPin,
    Navigation,
    Clock,
    Route,
    Loader2,
} from "lucide-react";
import mapService from "@/services/mapService";
import { toast } from "sonner";
import useSWR from "swr";
import RouteNavigationSkeleton from "@/components/navigation/RouteNavigationSkeleton";

// Fix untuk ikon default Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
    iconUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Ikon kustom untuk lokasi pengguna
const userLocationIcon = new L.Icon({
    iconUrl:
        "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

// Ikon kustom untuk restoran
const restaurantIcon = new L.Icon({
    iconUrl:
        "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

// Komponen untuk menampilkan rute pada peta
const RouteLayer = ({ route }) => {
    const map = useMap();

    useEffect(() => {
        if (!route || !map) return;

        // Konversi koordinat OSRM (lng, lat) ke Leaflet (lat, lng)
        const coordinates = route.coordinates.map((coord) => [
            coord[1],
            coord[0],
        ]);

        // Tambahkan polyline rute
        const routeLine = L.polyline(coordinates, {
            color: "#3b82f6",
            weight: 5,
            opacity: 0.8,
        }).addTo(map);

        // Fit map ke rute
        map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });

        return () => {
            map.removeLayer(routeLine);
        };
    }, [route, map]);

    return null;
};

export default function RouteNavigationPage() {
    const { restaurantId, foodId } = useParams();
    const navigate = useNavigate();

    const [userLocation, setUserLocation] = useState(null);
    const [route, setRoute] = useState(null);
    const [isLoadingLocation, setIsLoadingLocation] = useState(false);
    const [isLoadingRoute, setIsLoadingRoute] = useState(false);
    const [routeInfo, setRouteInfo] = useState(null);
    const [routeSteps, setRouteSteps] = useState([]);
    const [hasAutoDetected, setHasAutoDetected] = useState(false); // Flag untuk mencegah auto-detect berulang

    // Offline detection
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    // Fetch data based on type
    const endpoint = restaurantId
        ? `/api/v1/restaurants/${restaurantId}`
        : `/api/v1/foods/${foodId}`;

    const { data, error, isLoading } = useSWR(endpoint, {
        revalidateOnFocus: false,
    });

    // Extract location data
    const locationData = React.useMemo(() => {
        if (!data?.data) return null;

        if (restaurantId) {
            // Restaurant data
            return {
                name: data.data.name,
                address: data.data.address,
                latitude: data.data.latitude,
                longitude: data.data.longitude,
                type: "restaurant",
            };
        } else {
            // Food data
            return {
                name: data.data.restaurant?.name || "Restoran",
                address: data.data.restaurant?.address,
                latitude: data.data.restaurant?.latitude,
                longitude: data.data.restaurant?.longitude,
                foodName: data.data.name,
                type: "food",
            };
        }
    }, [data, restaurantId]);

    // Default center jika tidak ada koordinat
    const defaultCenter = [-3.9889, 122.5103]; // Kendari
    const center =
        locationData?.latitude && locationData?.longitude
            ? [locationData.latitude, locationData.longitude]
            : defaultCenter;

    // Fungsi untuk mendapatkan rute - menggunakan parameter langsung
    const getDirections = useCallback(
        async (userLoc) => {
            // Gunakan parameter atau state userLocation
            const locationToUse = userLoc || userLocation;

            if (
                !locationToUse ||
                !locationData?.latitude ||
                !locationData?.longitude
            ) {
                toast.error("Lokasi tidak lengkap untuk mendapatkan rute");
                return;
            }

            setIsLoadingRoute(true);
            try {
                const routeData = await mapService.getRoute(
                    locationToUse.lat,
                    locationToUse.lng,
                    locationData.latitude,
                    locationData.longitude
                );

                setRoute(routeData);
                setRouteInfo({
                    distance: mapService.formatDistance(routeData.distance),
                    duration: mapService.formatDuration(routeData.duration),
                });
                setRouteSteps(routeData.steps || []);

                toast.success("Rute berhasil ditemukan");
            } catch (error) {
                console.error("Error getting route:", error);
                toast.error(error.message);
            } finally {
                setIsLoadingRoute(false);
            }
        },
        [userLocation, locationData] // Include userLocation dependency
    );

    // Fungsi untuk mendapatkan lokasi pengguna - tanpa auto get route
    const getUserLocation = useCallback(async () => {
        setIsLoadingLocation(true);
        try {
            const location = await mapService.getCurrentLocation();
            setUserLocation(location);
            toast.success("Lokasi berhasil ditemukan");
        } catch (error) {
            console.error("Error getting user location:", error);
            toast.error(error.message);
        } finally {
            setIsLoadingLocation(false);
        }
    }, []); // Tidak ada dependency

    // Auto-detect user location saat komponen dimount - hanya sekali
    useEffect(() => {
        if (locationData && !hasAutoDetected) {
            setHasAutoDetected(true);
            getUserLocation();
        }
    }, [locationData, hasAutoDetected, getUserLocation]);

    // Auto get route setelah user location ditemukan - hanya sekali
    useEffect(() => {
        if (userLocation && locationData && hasAutoDetected && !route) {
            getDirections(userLocation);
        }
    }, [userLocation, locationData, hasAutoDetected, route, getDirections]);

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);

        return () => {
            window.removeEventListener("online", handleOnline);
            window.removeEventListener("offline", handleOffline);
        };
    }, []);

    if (isLoading) {
        return <RouteNavigationSkeleton />;
    }

    if (error || !locationData) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        Data tidak ditemukan
                    </h2>
                    <Button onClick={() => navigate(-1)}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Kembali
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Offline indicator */}
            {!isOnline && (
                <div className="bg-red-500 text-white text-center py-2 text-sm">
                    Anda sedang offline. Beberapa fitur mungkin tidak tersedia.
                </div>
            )}

            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => navigate(-1)}
                                className="flex items-center gap-2"
                            >
                                <ArrowLeft className="h-4 w-4" />
                                Kembali
                            </Button>
                            <div>
                                <h1 className="text-xl font-bold">
                                    Navigasi & Rute
                                </h1>
                                <p className="text-sm text-muted-foreground">
                                    {locationData?.type === "food"
                                        ? `${locationData.foodName} - ${locationData.name}`
                                        : locationData?.name}
                                </p>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        {/* <div className="flex items-center gap-2">
                            {locationData?.address && (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                        const address = encodeURIComponent(
                                            locationData.address
                                        );
                                        window.open(
                                            `https://www.google.com/maps/search/${address}`,
                                            "_blank"
                                        );
                                    }}
                                    className="hidden sm:flex items-center gap-2"
                                >
                                    <MapPin className="h-4 w-4" />
                                    Buka di Google Maps
                                </Button>
                            )}
                        </div> */}
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Peta - Kolom kiri/atas */}
                <div className="lg:col-span-2 order-2 lg:order-1">
                    <div className="h-[400px] lg:h-[500px]">
                        <div className="p-0 h-full">
                            {!isOnline ? (
                                <div className="h-full flex items-center justify-center bg-gray-100 rounded-lg">
                                    <div className="text-center">
                                        <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                            Peta Tidak Tersedia
                                        </h3>
                                        <p className="text-gray-600">
                                            Koneksi internet diperlukan untuk
                                            menampilkan peta
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <MapContainer
                                    center={center}
                                    zoom={
                                        locationData?.latitude &&
                                        locationData?.longitude
                                            ? 15
                                            : 10
                                    }
                                    style={{ height: "100%", width: "100%" }}
                                    className="rounded-lg bg-accent"
                                >
                                    <TileLayer
                                        url="http://{s}.google.com/vt?lyrs=m&x={x}&y={y}&z={z}"
                                        maxZoom={20}
                                        subdomains={[
                                            "mt0",
                                            "mt1",
                                            "mt2",
                                            "mt3",
                                        ]}
                                        attribution='&copy; <a href="https://maps.google.com">Google Maps</a>'
                                    />

                                    {/* Marker restoran */}
                                    {locationData?.latitude &&
                                        locationData?.longitude && (
                                            <Marker
                                                position={[
                                                    locationData.latitude,
                                                    locationData.longitude,
                                                ]}
                                                icon={restaurantIcon}
                                            >
                                                <Popup>
                                                    <div className="p-2">
                                                        <h3 className="font-semibold">
                                                            {locationData.name}
                                                        </h3>
                                                        {locationData.address && (
                                                            <p className="text-sm text-gray-600">
                                                                {
                                                                    locationData.address
                                                                }
                                                            </p>
                                                        )}
                                                        <p className="text-xs text-gray-500 mt-1">
                                                            {locationData.latitude.toFixed(
                                                                6
                                                            )}
                                                            ,{" "}
                                                            {locationData.longitude.toFixed(
                                                                6
                                                            )}
                                                        </p>
                                                    </div>
                                                </Popup>
                                            </Marker>
                                        )}

                                    {/* Marker lokasi pengguna */}
                                    {userLocation && (
                                        <Marker
                                            position={[
                                                userLocation.lat,
                                                userLocation.lng,
                                            ]}
                                            icon={userLocationIcon}
                                        >
                                            <Popup>
                                                <div className="p-2">
                                                    <h3 className="font-semibold">
                                                        Lokasi Anda
                                                    </h3>
                                                    <p className="text-xs text-gray-500">
                                                        {userLocation.lat.toFixed(
                                                            6
                                                        )}
                                                        ,{" "}
                                                        {userLocation.lng.toFixed(
                                                            6
                                                        )}
                                                    </p>
                                                </div>
                                            </Popup>
                                        </Marker>
                                    )}

                                    {/* Layer rute */}
                                    {route && <RouteLayer route={route} />}
                                </MapContainer>
                            )}
                        </div>
                    </div>
                </div>

                {/* Panel informasi - Kolom kanan/bawah */}
                <div className="order-1 lg:order-2 space-y-6">
                    {/* Informasi Lokasi */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <MapPin className="h-5 w-5 text-red-500" />
                                Tujuan
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div>
                                <h3 className="font-semibold">
                                    {locationData?.name}
                                </h3>
                                {locationData?.type === "food" && (
                                    <p className="text-sm text-blue-600">
                                        {locationData.foodName}
                                    </p>
                                )}
                                {locationData?.address && (
                                    <p className="text-sm text-muted-foreground">
                                        {locationData.address}
                                    </p>
                                )}
                            </div>

                            {/* Koordinat info */}
                            {locationData?.latitude &&
                                locationData?.longitude && (
                                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                                        Koordinat:{" "}
                                        {locationData.latitude.toFixed(6)},{" "}
                                        {locationData.longitude.toFixed(6)}
                                    </div>
                                )}
                        </CardContent>
                    </Card>

                    {/* Kontrol Lokasi */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Navigasi</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <Button
                                onClick={() => getUserLocation(false)} // Tidak auto get route
                                disabled={isLoadingLocation || !isOnline}
                                variant="outline"
                                className="w-full flex items-center gap-2"
                            >
                                <Navigation className="h-4 w-4" />
                                {isLoadingLocation
                                    ? "Mencari..."
                                    : "Deteksi Lokasi Saya"}
                            </Button>

                            {userLocation &&
                                locationData?.latitude &&
                                locationData?.longitude && (
                                    <Button
                                        onClick={() => getDirections()}
                                        disabled={isLoadingRoute || !isOnline}
                                        className="w-full flex items-center gap-2"
                                    >
                                        <Route className="h-4 w-4" />
                                        {isLoadingRoute
                                            ? "Memuat..."
                                            : "Tampilkan Rute"}
                                    </Button>
                                )}

                            {!isOnline && (
                                <p className="text-xs text-gray-500 text-center">
                                    Koneksi internet diperlukan untuk navigasi
                                </p>
                            )}
                        </CardContent>
                    </Card>

                    {/* Info Rute */}
                    {routeInfo && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Informasi Rute</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="flex items-center gap-2">
                                        <Route className="h-4 w-4" />
                                        Jarak
                                    </span>
                                    <Badge variant="secondary">
                                        {routeInfo.distance}
                                    </Badge>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="flex items-center gap-2">
                                        <Clock className="h-4 w-4" />
                                        Estimasi Waktu
                                    </span>
                                    <Badge variant="secondary">
                                        {routeInfo.duration}
                                    </Badge>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Direct Distance (jika tidak ada rute) */}
                    {userLocation &&
                        locationData?.latitude &&
                        locationData?.longitude &&
                        !route && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Jarak Langsung</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">
                                            Jarak garis lurus
                                        </span>
                                        <Badge variant="outline">
                                            {mapService.formatDistance(
                                                mapService.calculateDistance(
                                                    userLocation.lat,
                                                    userLocation.lng,
                                                    locationData.latitude,
                                                    locationData.longitude
                                                )
                                            )}
                                        </Badge>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                    {/* Panduan Arah */}
                    {/* {routeSteps.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Panduan Arah</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-2 max-h-60 overflow-y-auto">
                                    {routeSteps
                                        .slice(0, 10)
                                        .map((step, index) => (
                                            <div
                                                key={index}
                                                className="flex gap-3 p-2 bg-gray-50 rounded"
                                            >
                                                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0">
                                                    {index + 1}
                                                </div>
                                                <div className="flex-1 text-sm">
                                                    {step.maneuver
                                                        ?.instruction ||
                                                        "Lanjutkan perjalanan"}
                                                    {step.distance && (
                                                        <span className="text-muted-foreground ml-2">
                                                            (
                                                            {mapService.formatDistance(
                                                                step.distance
                                                            )}
                                                            )
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>
                    )} */}
                </div>
            </div>
        </div>
    );
}
