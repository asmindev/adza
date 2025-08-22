import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
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
import { toast } from "sonner";
import apiService from "@/dashboard/services/api";
import LocationPicker from "@/components/map/LocationPicker";

// Validation schema for restaurant edit form
const editRestaurantSchema = z.object({
    name: z.string().min(1, "Nama restoran wajib diisi"),
    description: z.string().min(1, "Deskripsi wajib diisi"),
    address: z.string().min(1, "Alamat wajib diisi"),
    phone: z.string().min(1, "Nomor telepon wajib diisi"),
    email: z.string().email("Format email tidak valid"),
    latitude: z.number().optional(),
    longitude: z.number().optional(),
    is_active: z.boolean().default(true),
});

export default function EditRestaurantDialog({
    open,
    onOpenChange,
    restaurantData,
    onSuccess,
}) {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const form = useForm({
        resolver: zodResolver(editRestaurantSchema),
        defaultValues: {
            name: "",
            description: "",
            address: "",
            phone: "",
            email: "",
            latitude: 0,
            longitude: 0,
            is_active: true,
        },
    });

    // Handle location change from LocationPicker
    const handleLocationChange = (lat, lng) => {
        form.setValue("latitude", lat);
        form.setValue("longitude", lng);
    };

    // Reset form when restaurant data changes
    useEffect(() => {
        if (restaurantData) {
            form.reset({
                name: restaurantData.name || "",
                description: restaurantData.description || "",
                address: restaurantData.address || "",
                phone: restaurantData.phone || "",
                email: restaurantData.email || "",
                latitude: restaurantData.latitude || 0,
                longitude: restaurantData.longitude || 0,
                is_active: restaurantData.is_active ?? true,
            });
        }
    }, [restaurantData, form]);

    const onSubmit = async (data) => {
        setIsSubmitting(true);
        try {
            await apiService.restaurants.update(restaurantData.id, data);
            toast.success("Restoran berhasil diperbarui");
            onSuccess?.();
            onOpenChange(false);
        } catch (error) {
            toast.error(
                error?.response?.data?.message || "Gagal memperbarui restoran"
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCancel = () => {
        form.reset();
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Edit Restoran</DialogTitle>
                    <DialogDescription>
                        Perbarui informasi restoran di bawah ini.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-4"
                    >
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
                                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                                        <div className="space-y-0.5">
                                            <FormLabel>Status Aktif</FormLabel>
                                            <div className="text-sm text-muted-foreground">
                                                Restoran dapat menerima pesanan
                                            </div>
                                        </div>
                                        <FormControl>
                                            <Switch
                                                checked={field.value}
                                                onCheckedChange={field.onChange}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="address"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Alamat</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Masukkan alamat lengkap restoran"
                                            className="resize-none"
                                            {...field}
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
                                Pilih lokasi restoran dengan mengklik pada peta
                                atau cari alamat
                            </p>
                        </div>

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleCancel}
                                disabled={isSubmitting}
                            >
                                Batal
                            </Button>
                            <Button type="submit" disabled={isSubmitting}>
                                {isSubmitting
                                    ? "Memperbarui..."
                                    : "Perbarui Restoran"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
