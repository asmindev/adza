import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Navigation, Clock, Route } from "lucide-react";
import mapService from "@/services/mapService";
import { toast } from "sonner";

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
    const routeRef = useRef(null);

    useEffect(() => {
        if (!route || !map) return;

        // Hapus rute sebelumnya
        if (routeRef.current) {
            map.removeLayer(routeRef.current);
        }

        // Konversi koordinat OSRM (lng, lat) ke Leaflet (lat, lng)
        const coordinates = route.coordinates.map((coord) => [
            coord[1],
            coord[0],
        ]);

        // Tambahkan polyline rute
        routeRef.current = L.polyline(coordinates, {
            color: "#3b82f6",
            weight: 5,
            opacity: 0.8,
        }).addTo(map);

        // Fit map ke rute
        map.fitBounds(routeRef.current.getBounds(), { padding: [20, 20] });

        return () => {
            if (routeRef.current) {
                map.removeLayer(routeRef.current);
            }
        };
    }, [route, map]);

    return null;
};

// Komponen utama LocationMap
export default function LocationMap({
    restaurantLat,
    restaurantLng,
    restaurantName = "Restoran",
    restaurantAddress = "",
    showRouting = true,
    height = "400px",
    onLocationFound = null,
}) {
    const [userLocation, setUserLocation] = useState(null);
    const [route, setRoute] = useState(null);
    const [isLoadingLocation, setIsLoadingLocation] = useState(false);
    const [isLoadingRoute, setIsLoadingRoute] = useState(false);
    const [routeInfo, setRouteInfo] = useState(null);

    // Default center jika tidak ada koordinat restoran
    const defaultCenter = [-3.9889, 122.5103]; // Kendari
    const center =
        restaurantLat && restaurantLng
            ? [restaurantLat, restaurantLng]
            : defaultCenter;

    // Fungsi untuk mendapatkan lokasi pengguna
    const getUserLocation = async () => {
        setIsLoadingLocation(true);
        try {
            const location = await mapService.getCurrentLocation();
            setUserLocation(location);

            if (onLocationFound) {
                onLocationFound(location);
            }

            toast.success("Lokasi berhasil ditemukan");
        } catch (error) {
            console.error("Error getting user location:", error);
            toast.error(error.message);
        } finally {
            setIsLoadingLocation(false);
        }
    };

    // Fungsi untuk mendapatkan rute
    const getDirections = async () => {
        if (!userLocation || !restaurantLat || !restaurantLng) {
            toast.error("Lokasi tidak lengkap untuk mendapatkan rute");
            return;
        }

        setIsLoadingRoute(true);
        try {
            const routeData = await mapService.getRoute(
                userLocation.lat,
                userLocation.lng,
                restaurantLat,
                restaurantLng
            );

            setRoute(routeData);
            setRouteInfo({
                distance: mapService.formatDistance(routeData.distance),
                duration: mapService.formatDuration(routeData.duration),
            });

            toast.success("Rute berhasil ditemukan");
        } catch (error) {
            console.error("Error getting route:", error);
            toast.error(error.message);
        } finally {
            setIsLoadingRoute(false);
        }
    };

    // Auto-detect user location saat komponen dimount
    useEffect(() => {
        if (showRouting) {
            getUserLocation();
        }
    }, [showRouting]);

    return (
        <div className="space-y-4">
            {/* Header dengan informasi restoran */}
            <Card>
                <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-red-500" />
                        Lokasi {restaurantName}
                    </CardTitle>
                    {restaurantAddress && (
                        <p className="text-sm text-muted-foreground">
                            {restaurantAddress}
                        </p>
                    )}
                </CardHeader>

                {showRouting && (
                    <CardContent className="pt-0">
                        <div className="flex flex-wrap gap-2">
                            <Button
                                onClick={getUserLocation}
                                disabled={isLoadingLocation}
                                variant="outline"
                                size="sm"
                                className="flex items-center gap-2"
                            >
                                <Navigation className="h-4 w-4" />
                                {isLoadingLocation
                                    ? "Mencari..."
                                    : "Lokasi Saya"}
                            </Button>

                            {userLocation && restaurantLat && restaurantLng && (
                                <Button
                                    onClick={getDirections}
                                    disabled={isLoadingRoute}
                                    size="sm"
                                    className="flex items-center gap-2"
                                >
                                    <Route className="h-4 w-4" />
                                    {isLoadingRoute
                                        ? "Memuat..."
                                        : "Dapatkan Rute"}
                                </Button>
                            )}
                        </div>

                        {/* Info rute */}
                        {routeInfo && (
                            <div className="mt-4 flex gap-4">
                                <Badge
                                    variant="secondary"
                                    className="flex items-center gap-1"
                                >
                                    <Route className="h-3 w-3" />
                                    {routeInfo.distance}
                                </Badge>
                                <Badge
                                    variant="secondary"
                                    className="flex items-center gap-1"
                                >
                                    <Clock className="h-3 w-3" />
                                    {routeInfo.duration}
                                </Badge>
                            </div>
                        )}
                    </CardContent>
                )}
            </Card>

            {/* Peta */}
            <Card>
                <CardContent className="p-0">
                    <div
                        style={{ height }}
                        className="w-full rounded-lg overflow-hidden"
                    >
                        <MapContainer
                            center={center}
                            zoom={restaurantLat && restaurantLng ? 15 : 10}
                            style={{ height: "100%", width: "100%" }}
                            className="z-0"
                        >
                            <TileLayer
                                url="http://{s}.google.com/vt?lyrs=m&x={x}&y={y}&z={z}"
                                maxZoom={20}
                                subdomains={["mt0", "mt1", "mt2", "mt3"]}
                                attribution='&copy; <a href="https://maps.google.com">Google Maps</a>'
                            />

                            {/* Marker restoran */}
                            {restaurantLat && restaurantLng && (
                                <Marker
                                    position={[restaurantLat, restaurantLng]}
                                    icon={restaurantIcon}
                                >
                                    <Popup>
                                        <div className="p-2">
                                            <h3 className="font-semibold">
                                                {restaurantName}
                                            </h3>
                                            {restaurantAddress && (
                                                <p className="text-sm text-gray-600">
                                                    {restaurantAddress}
                                                </p>
                                            )}
                                            <p className="text-xs text-gray-500 mt-1">
                                                {restaurantLat.toFixed(6)},{" "}
                                                {restaurantLng.toFixed(6)}
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
                                                {userLocation.lat.toFixed(6)},{" "}
                                                {userLocation.lng.toFixed(6)}
                                            </p>
                                        </div>
                                    </Popup>
                                </Marker>
                            )}

                            {/* Layer rute */}
                            {route && <RouteLayer route={route} />}
                        </MapContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
