import React, { useState, useCallback } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, RotateCcw, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
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

// Komponen untuk menangani klik pada peta
function LocationClickHandler({ onLocationSelect }) {
    useMapEvents({
        click(e) {
            const { lat, lng } = e.latlng;
            onLocationSelect(lat, lng);
        },
    });
    return null;
}

export default function LocationPicker({
    latitude = 0,
    longitude = 0,
    onLocationChange,
    height = "300px",
}) {
    const [selectedLocation, setSelectedLocation] = useState(
        latitude && longitude ? { lat: latitude, lng: longitude } : null
    );
    const [searchAddress, setSearchAddress] = useState("");
    const [isSearching, setIsSearching] = useState(false);

    // Default center (Indonesia)
    const defaultCenter = [-2.5489, 118.0149];
    const center = selectedLocation
        ? [selectedLocation.lat, selectedLocation.lng]
        : latitude && longitude
        ? [latitude, longitude]
        : defaultCenter;

    // Handle location selection from map click
    const handleLocationSelect = useCallback(
        (lat, lng) => {
            const newLocation = { lat, lng };
            setSelectedLocation(newLocation);
            onLocationChange?.(lat, lng);
            toast.success(
                `Lokasi dipilih: ${lat.toFixed(6)}, ${lng.toFixed(6)}`
            );
        },
        [onLocationChange]
    );

    // Handle address search
    const handleAddressSearch = async () => {
        if (!searchAddress.trim()) {
            toast.error("Masukkan alamat untuk dicari");
            return;
        }

        setIsSearching(true);
        try {
            const results = await mapService.geocodeAddress(searchAddress);
            if (results && results.length > 0) {
                const result = results[0];
                handleLocationSelect(result.lat, result.lng);
                setSearchAddress(result.displayName);
                toast.success("Alamat ditemukan!");
            } else {
                toast.error("Alamat tidak ditemukan");
            }
        } catch (error) {
            console.error("Error searching address:", error);
            toast.error("Gagal mencari alamat");
        } finally {
            setIsSearching(false);
        }
    };

    // Reset location
    const handleReset = () => {
        setSelectedLocation(null);
        setSearchAddress("");
        onLocationChange?.(0, 0);
        toast.info("Lokasi direset");
    };

    // Get current location
    const handleGetCurrentLocation = async () => {
        try {
            const location = await mapService.getCurrentLocation();
            handleLocationSelect(location.lat, location.lng);

            // Try to get address for display
            try {
                const addressData = await mapService.reverseGeocode(
                    location.lat,
                    location.lng
                );
                setSearchAddress(addressData.displayName);
            } catch (addressError) {
                console.warn("Could not get address for current location");
            }
        } catch (error) {
            console.error("Error getting current location:", error);
            toast.error(error.message);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-blue-500" />
                    Pilih Lokasi Restoran
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                    Klik pada peta untuk memilih lokasi atau cari alamat
                </p>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Search and Controls */}
                <div className="space-y-3">
                    <div className="flex gap-2">
                        <Input
                            placeholder="Cari alamat..."
                            value={searchAddress}
                            onChange={(e) => setSearchAddress(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === "Enter") {
                                    handleAddressSearch();
                                }
                            }}
                        />
                        <Button
                            type="button"
                            onClick={handleAddressSearch}
                            disabled={isSearching}
                            variant="outline"
                            size="icon"
                        >
                            <Search className="h-4 w-4" />
                        </Button>
                    </div>

                    <div className="flex gap-2">
                        <Button
                            type="button"
                            onClick={handleGetCurrentLocation}
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                        >
                            <MapPin className="h-4 w-4" />
                            Lokasi Saya
                        </Button>
                        <Button
                            type="button"
                            onClick={handleReset}
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                        >
                            <RotateCcw className="h-4 w-4" />
                            Reset
                        </Button>
                    </div>
                </div>

                {/* Selected Location Info */}
                {selectedLocation && (
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-sm font-medium text-blue-900">
                            Lokasi Terpilih:
                        </p>
                        <p className="text-sm text-blue-700">
                            Latitude: {selectedLocation.lat.toFixed(6)}
                        </p>
                        <p className="text-sm text-blue-700">
                            Longitude: {selectedLocation.lng.toFixed(6)}
                        </p>
                    </div>
                )}

                {/* Map */}
                <div
                    style={{ height }}
                    className="w-full rounded-lg overflow-hidden border"
                >
                    <MapContainer
                        center={center}
                        zoom={selectedLocation ? 15 : 5}
                        style={{ height: "100%", width: "100%" }}
                        className="cursor-crosshair"
                    >
                        <TileLayer
                            url="http://{s}.google.com/vt?lyrs=m&x={x}&y={y}&z={z}"
                            maxZoom={20}
                            subdomains={["mt0", "mt1", "mt2", "mt3"]}
                            attribution='&copy; <a href="https://maps.google.com">Google Maps</a>'
                        />

                        <LocationClickHandler
                            onLocationSelect={handleLocationSelect}
                        />

                        {selectedLocation && (
                            <Marker
                                position={[
                                    selectedLocation.lat,
                                    selectedLocation.lng,
                                ]}
                            />
                        )}
                    </MapContainer>
                </div>

                <p className="text-xs text-muted-foreground text-center">
                    💡 Tip: Klik pada peta untuk memilih lokasi restoran
                </p>
            </CardContent>
        </Card>
    );
}
