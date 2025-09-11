import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import useSWR from "swr";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { MultiSelect } from "@/components/ui/multi-select";
import { toast } from "sonner";
import LocationPicker from "@/components/map/LocationPicker";
import { restaurantSchema } from "../schemas/restaurantSchema";
import apiService from "@/lib/api";

export default function AddRestaurantDialog({ open, onOpenChange, onSuccess }) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isGeocodingLoading, setIsGeocodingLoading] = useState(false);
    const [suggestedAddress, setSuggestedAddress] = useState(null);

    // Fetch categories for selection
    const { data: categoriesData } = useSWR(
        ["/categories"],
        () => apiService.categories.getAll(false),
        {
            revalidateOnFocus: false,
            onError: () => {
                toast.error("Gagal memuat kategori");
            },
        }
    );

    const categories = categoriesData?.data?.data || [];

    const form = useForm({
        resolver: zodResolver(restaurantSchema),
        defaultValues: {
            name: "",
            description: "",
            address: "",
            phone: "",
            email: "",
            latitude: 0,
            longitude: 0,
            is_active: true,
            category_ids: [],
        },
    });

    // Simple reverse geocoding function
    const reverseGeocode = async (latitude, longitude) => {
        setIsGeocodingLoading(true);
        setSuggestedAddress(null);

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
                if (data.display_name) {
                    setSuggestedAddress(data.display_name);
                }
            }
        } catch (error) {
            console.error("Reverse geocoding error:", error);
            toast.error("Gagal mendapatkan alamat dari koordinat");
        } finally {
            setIsGeocodingLoading(false);
        }
    };

    // Handle using suggested address
    const useSuggestedAddress = () => {
        if (suggestedAddress) {
            form.setValue("address", suggestedAddress);
            setSuggestedAddress(null);
            toast.success("Alamat berhasil diperbarui dari koordinat");
        }
    };

    // Handle dismissing suggested address
    const dismissSuggestion = () => {
        setSuggestedAddress(null);
    };

    // Handle location change from LocationPicker
    const handleLocationChange = (lat, lng) => {
        form.setValue("latitude", lat);
        form.setValue("longitude", lng);

        // Trigger reverse geocoding with debounce
        setTimeout(() => {
            reverseGeocode(lat, lng);
        }, 1000);
    };

    const onSubmit = async (data) => {
        setIsSubmitting(true);
        try {
            // Remove empty category_ids if no categories selected
            if (data.category_ids && data.category_ids.length === 0) {
                delete data.category_ids;
            }

            console.log("Creating restaurant with data:", data);

            await apiService.restaurants.create(data);
            toast.success("Restoran berhasil ditambahkan");
            form.reset();
            onSuccess?.();
            onOpenChange(false);
        } catch (error) {
            toast.error(
                error?.response?.data?.message || "Gagal menambahkan restoran"
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Tambah Restoran Baru</DialogTitle>
                    <DialogDescription>
                        Isi form di bawah untuk menambahkan restoran baru ke
                        dalam sistem.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-4"
                    >
                        <div className="space-y-4 border-b pb-4 max-h-96 overflow-y-auto px-4">
                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                <FormField
                                    control={form.control}
                                    name="name"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Nama Restoran</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="Masukkan nama restoran"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="email"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Email</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="email"
                                                    placeholder="restaurant@example.com"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>

                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                <FormField
                                    control={form.control}
                                    name="phone"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Nomor Telepon</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="+62274567890"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="is_active"
                                    render={({ field }) => (
                                        <FormItem className="flex flex-row items-end space-x-3 rounded-lg px-3">
                                            <FormLabel>Status Aktif</FormLabel>
                                            {/* <div className="text-sm text-muted-foreground">
                                                    Restoran dapat menerima
                                                    pesanan
                                                </div> */}
                                            <FormControl>
                                                <Switch
                                                    checked={field.value}
                                                    onCheckedChange={
                                                        field.onChange
                                                    }
                                                />
                                            </FormControl>
                                        </FormItem>
                                    )}
                                />
                            </div>
                            <FormField
                                control={form.control}
                                name="category_ids"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Kategori</FormLabel>
                                        <FormControl>
                                            <MultiSelect
                                                className={"z-[9999]"}
                                                options={categories}
                                                value={field.value}
                                                onChange={field.onChange}
                                                placeholder="Pilih kategori restoran..."
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="description"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Deskripsi</FormLabel>
                                        <FormControl>
                                            <Textarea
                                                placeholder="Deskripsi tentang restoran, spesialisasi makanan, dll."
                                                className="resize-none"
                                                rows={3}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="address"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>
                                            Alamat
                                            {isGeocodingLoading && (
                                                <span className="ml-2 text-sm text-blue-600">
                                                    (Mendapatkan alamat dari
                                                    koordinat...)
                                                </span>
                                            )}
                                        </FormLabel>
                                        <FormControl>
                                            <Textarea
                                                placeholder="Masukkan alamat lengkap restoran"
                                                className="resize-none"
                                                {...field}
                                                disabled={isGeocodingLoading}
                                            />
                                        </FormControl>

                                        {/* Address suggestion from geocoding */}
                                        {suggestedAddress && (
                                            <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <p className="text-sm font-medium text-blue-900 mb-1">
                                                            Alamat berdasarkan
                                                            koordinat:
                                                        </p>
                                                        <p className="text-sm text-blue-700">
                                                            {suggestedAddress}
                                                        </p>
                                                    </div>
                                                    <div className="flex gap-2 ml-3">
                                                        <button
                                                            type="button"
                                                            onClick={
                                                                useSuggestedAddress
                                                            }
                                                            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                                                        >
                                                            Gunakan
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={
                                                                dismissSuggestion
                                                            }
                                                            className="text-sm bg-gray-200 text-gray-700 px-3 py-1 rounded hover:bg-gray-300"
                                                        >
                                                            Tutup
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        <FormMessage />
                                        <p className="text-xs text-muted-foreground">
                                            Alamat akan disarankan otomatis saat
                                            Anda memilih lokasi di peta
                                        </p>
                                    </FormItem>
                                )}
                            />

                            {/* Location Picker Section */}
                            <div className="space-y-2">
                                <FormLabel>Lokasi Restoran</FormLabel>
                                <LocationPicker
                                    latitude={form.watch("latitude")}
                                    longitude={form.watch("longitude")}
                                    onLocationChange={handleLocationChange}
                                    height="400px"
                                />
                                <p className="text-xs text-muted-foreground">
                                    Pilih lokasi restoran dengan mengklik pada
                                    peta atau cari alamat
                                </p>
                            </div>
                        </div>

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                disabled={isSubmitting}
                            >
                                Batal
                            </Button>
                            <Button type="submit" disabled={isSubmitting}>
                                {isSubmitting
                                    ? "Menambahkan..."
                                    : "Tambah Restoran"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
