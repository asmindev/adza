import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import LocationMap from "@/components/map/LocationMap";

export default function LocationDialog({
    open,
    onOpenChange,
    restaurantLat,
    restaurantLng,
    restaurantName,
    restaurantAddress,
}) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
                <DialogHeader>
                    <DialogTitle>Lokasi & Navigasi</DialogTitle>
                    <DialogDescription>
                        Lihat lokasi Rumah Makan dan dapatkan rute untuk menuju
                        ke sana.
                    </DialogDescription>
                </DialogHeader>

                <div className="mt-4">
                    <LocationMap
                        restaurantLat={restaurantLat}
                        restaurantLng={restaurantLng}
                        restaurantName={restaurantName}
                        restaurantAddress={restaurantAddress}
                        showRouting={true}
                        height="500px"
                    />
                </div>
            </DialogContent>
        </Dialog>
    );
}
