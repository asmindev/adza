import React, { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useDropzone } from "react-dropzone";
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { foodCreateSchema } from "../schemas/foodSchema";
import { Upload, X, ImagePlus } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import useSWR from "swr";
import apiService from "@/lib/api";

export default function AddFoodDialog({ open, onOpenChange, onSuccess }) {
    const [images, setImages] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    // Fetch restaurants for selection
    const { data: restaurantsData } = useSWR(
        ["/restaurants/list"],
        () => apiService.restaurants.getAll(1, 100, ""),
        {
            revalidateOnFocus: false,
            onError: () => {
                toast.error("Gagal memuat daftar restoran");
            },
        }
    );

    const restaurants = restaurantsData?.data?.data?.restaurants || [];

    const form = useForm({
        resolver: zodResolver(foodCreateSchema),
        defaultValues: {
            name: "",
            description: "",
            price: 0,
            restaurant_id: "",
            ingredients: [],
            status: "active",
        },
    });

    const isSubmitting = form.formState.isSubmitting;

    // Clear images when dialog is closed
    useEffect(() => {
        if (!open) {
            setImages([]);
        }
    }, [open, form]);

    // Dropzone setup
    const onDrop = useCallback((acceptedFiles) => {
        setIsUploading(true);

        // Process each file
        const newImages = acceptedFiles.map((file) => ({
            file,
            preview: URL.createObjectURL(file),
            status: "pending", // 'pending', 'uploading', 'success', 'error'
            progress: 0,
            isMain: false,
        }));

        // Simulate upload process
        setTimeout(() => {
            setImages((prev) => {
                const updated = [...prev, ...newImages];
                // Make first image the main image if none exists
                if (prev.length === 0 && newImages.length > 0) {
                    updated[0].isMain = true;
                }
                return updated;
            });
            setIsUploading(false);
        }, 1000);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "image/*": [".jpeg", ".jpg", ".png", ".gif", ".webp"],
        },
        maxSize: 5 * 1024 * 1024, // 5MB
    });

    // Handle URL addition
    const handleAddUrl = (url) => {
        if (
            !url ||
            !url.match(/^https?:\/\/.+\.(jpeg|jpg|png|gif|webp)(\?.*)?$/i)
        ) {
            toast.error("Mohon masukkan URL gambar yang valid");
            return;
        }

        setImages((prev) => {
            const newImage = {
                url,
                preview: url,
                status: "success",
                isMain: prev.length === 0, // Make it main if it's the first image
            };
            return [...prev, newImage];
        });

        // Clear the URL input
        form.setValue("imageUrl", "");
    };

    // Set main image
    const handleSetMainImage = (index) => {
        setImages((prev) =>
            prev.map((img, i) => ({
                ...img,
                isMain: i === index,
            }))
        );
    };

    // Remove image
    const handleRemoveImage = (index) => {
        setImages((prev) => {
            const filtered = prev.filter((_, i) => i !== index);

            // If we removed the main image, set a new one
            if (prev[index].isMain && filtered.length > 0) {
                const newMainIndex = index < filtered.length ? index : 0;
                filtered[newMainIndex].isMain = true;
            }

            return filtered;
        });

        // Revoke object URL to prevent memory leaks
        if (images[index].file) {
            URL.revokeObjectURL(images[index].preview);
        }
    };

    async function onSubmit(data) {
        try {
            if (images.length === 0) {
                toast.warning("Silakan tambahkan minimal satu gambar");
                return;
            }

            if (!data.restaurant_id) {
                toast.warning("Silakan pilih restoran");
                return;
            }

            // Prepare the images data
            const imagesData = images.map((img) => ({
                image_url: img.url || "", // URL for remote images
                file: img.file || null, // File object for uploaded files
                is_main: img.isMain,
            }));

            // Add images to form data
            const formData = {
                ...data,
                images: imagesData,
            };

            await apiService.foods.create(formData);
            toast.success("Makanan berhasil ditambahkan");
            form.reset();
            onOpenChange(false);
            if (onSuccess) onSuccess();
        } catch (error) {
            toast.error(
                error.message || "Gagal menambahkan makanan. Silakan coba lagi."
            );
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Tambah Makanan Baru</DialogTitle>
                    <DialogDescription>
                        Isi detail untuk menambahkan makanan baru ke koleksi
                        Anda.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-4"
                    >
                        {/* Food Images Section */}
                        <div className="space-y-2">
                            <FormLabel>Gambar Makanan</FormLabel>

                            {/* Dropzone */}
                            <div
                                {...getRootProps()}
                                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                                    isDragActive
                                        ? "border-primary bg-primary/5"
                                        : "border-gray-300 hover:border-primary/50"
                                }`}
                            >
                                <input {...getInputProps()} />
                                <div className="flex flex-col items-center justify-center space-y-2">
                                    <Upload className="h-8 w-8 text-gray-400" />
                                    {isDragActive ? (
                                        <p className="text-sm text-gray-600">
                                            Letakkan gambar di sini...
                                        </p>
                                    ) : (
                                        <>
                                            <p className="text-sm text-gray-600">
                                                Tarik & letakkan gambar di sini,
                                                atau klik untuk memilih
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                Mendukung: JPG, PNG, GIF, WEBP
                                                (maks 5MB)
                                            </p>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* URL Input */}
                            <div className="flex items-center space-x-2 mt-2">
                                <FormField
                                    control={form.control}
                                    name="imageUrl"
                                    render={({ field }) => (
                                        <FormItem className="flex-1">
                                            <FormControl>
                                                <Input
                                                    placeholder="Atau masukkan URL gambar: https://example.com/image.jpg"
                                                    {...field}
                                                />
                                            </FormControl>
                                        </FormItem>
                                    )}
                                />
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() =>
                                        handleAddUrl(form.getValues("imageUrl"))
                                    }
                                >
                                    Tambah URL
                                </Button>
                            </div>

                            {/* Loading indicator */}
                            {isUploading && (
                                <div className="flex items-center justify-center p-4">
                                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                    <span className="ml-2 text-sm text-gray-600">
                                        Mengunggah...
                                    </span>
                                </div>
                            )}

                            {/* Image Previews */}
                            {images.length > 0 && (
                                <ScrollArea className="h-60 w-full rounded-md border p-2">
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                        {images.map((image, index) => (
                                            <div
                                                key={index}
                                                className={`group relative rounded-md overflow-hidden border ${
                                                    image.isMain
                                                        ? "ring-2 ring-primary"
                                                        : ""
                                                }`}
                                            >
                                                <img
                                                    src={image.preview}
                                                    alt={`Pratinjau ${
                                                        index + 1
                                                    }`}
                                                    className="h-32 w-full object-cover"
                                                    onError={(e) => {
                                                        e.target.onerror = null;
                                                        e.target.src =
                                                            "https://via.placeholder.com/150?text=Error";
                                                    }}
                                                />

                                                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                    <div className="flex space-x-1">
                                                        <Button
                                                            type="button"
                                                            variant="secondary"
                                                            size="sm"
                                                            disabled={
                                                                image.isMain
                                                            }
                                                            onClick={() =>
                                                                handleSetMainImage(
                                                                    index
                                                                )
                                                            }
                                                            className="h-8 w-8 p-0"
                                                        >
                                                            <ImagePlus className="h-4 w-4" />
                                                            <span className="sr-only">
                                                                Jadikan utama
                                                            </span>
                                                        </Button>
                                                        <Button
                                                            type="button"
                                                            variant="destructive"
                                                            size="sm"
                                                            onClick={() =>
                                                                handleRemoveImage(
                                                                    index
                                                                )
                                                            }
                                                            className="h-8 w-8 p-0"
                                                        >
                                                            <X className="h-4 w-4" />
                                                            <span className="sr-only">
                                                                Hapus
                                                            </span>
                                                        </Button>
                                                    </div>
                                                </div>

                                                {image.isMain && (
                                                    <div className="absolute top-0 left-0 bg-primary text-white text-xs px-1 py-0.5">
                                                        Utama
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            )}
                        </div>

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <FormField
                                control={form.control}
                                name="name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Nama</FormLabel>
                                        <FormControl>
                                            <Input
                                                placeholder="Nama makanan"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="restaurant_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Restoran</FormLabel>
                                        <Select
                                            onValueChange={field.onChange}
                                            defaultValue={field.value}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Pilih restoran" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {restaurants.map(
                                                    (restaurant) => (
                                                        <SelectItem
                                                            key={restaurant.id}
                                                            value={
                                                                restaurant.id
                                                            }
                                                        >
                                                            {restaurant.name}
                                                        </SelectItem>
                                                    )
                                                )}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-1">
                            <FormField
                                control={form.control}
                                name="price"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Harga</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="number"
                                                step="0.01"
                                                placeholder="0.00"
                                                {...field}
                                                onChange={(e) =>
                                                    field.onChange(
                                                        parseFloat(
                                                            e.target.value
                                                        )
                                                    )
                                                }
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Deskripsi</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Deskripsikan makanan..."
                                            className="resize-none h-20"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="status"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Status</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Pilih status" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="active">
                                                Aktif
                                            </SelectItem>
                                            <SelectItem value="inactive">
                                                Tidak Aktif
                                            </SelectItem>
                                            <SelectItem value="pending">
                                                Tertunda
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                disabled={isSubmitting || isUploading}
                            >
                                Batal
                            </Button>
                            <Button
                                type="submit"
                                disabled={isSubmitting || isUploading}
                            >
                                {isSubmitting
                                    ? "Menambahkan..."
                                    : "Tambah Makanan"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
