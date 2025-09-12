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
import { foodUpdateSchema } from "../schemas/foodSchema";
import { Upload, X, ImagePlus } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Combobox } from "@/components/ui/combobox";
import useSWR from "swr";
import apiService from "@/lib/api";

export default function EditFoodDialog({
    open,
    onOpenChange,
    foodData,
    onSuccess,
}) {
    const [images, setImages] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

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
        resolver: zodResolver(foodUpdateSchema),
        defaultValues: {
            name: "",
            description: "",
            price: 0,
            restaurant_id: "",
            ingredients: [],
            status: "active",
        },
    });

    // Reset form when food data changes
    useEffect(() => {
        if (foodData && open) {
            form.reset({
                name: foodData.name || "",
                description: foodData.description || "",
                price: foodData.price || 0,
                restaurant_id: foodData.restaurant_id || "",
                ingredients: foodData.ingredients || [],
                status: foodData.status || "active",
            });

            // Set existing images
            if (foodData.images && foodData.images.length > 0) {
                const existingImages = foodData.images.map((img, index) => ({
                    id: img.id,
                    url: img.image_url,
                    preview: img.image_url,
                    status: "success",
                    isMain: img.is_main || index === 0,
                    isExisting: true, // Flag to identify existing images
                }));
                setImages(existingImages);
            } else {
                setImages([]);
            }
        }
    }, [foodData, form, open]);

    // Clear images when dialog is closed
    useEffect(() => {
        if (!open) {
            // Reset all states immediately when dialog closes
            setIsUploading(false);
            setIsSubmitting(false);
            setImages([]);
            form.reset();
        }
    }, [open, form]);

    // Cleanup effect for component unmount
    useEffect(() => {
        return () => {
            // Cleanup any object URLs to prevent memory leaks
            images.forEach((image) => {
                if (image.file && image.preview) {
                    URL.revokeObjectURL(image.preview);
                }
            });
        };
    }, [images]);

    // Dropzone setup
    const onDrop = useCallback((acceptedFiles) => {
        setIsUploading(true);

        // Process each file
        const newImages = acceptedFiles.map((file) => ({
            file,
            preview: URL.createObjectURL(file),
            status: "pending",
            progress: 0,
            isMain: false,
            isExisting: false,
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
        noClick: false, // Allow click
        noKeyboard: false, // Allow keyboard
        noDrag: false, // Allow drag
        preventDropOnDocument: true, // Prevent dropping on document
    });

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

        // Revoke object URL to prevent memory leaks (only for new uploads)
        if (images[index].file) {
            URL.revokeObjectURL(images[index].preview);
        }
    };

    async function onSubmit(data) {
        // Validasi terlebih dahulu
        if (images.length === 0) {
            toast.warning("Silakan tambahkan minimal satu gambar");
            return;
        }

        if (!data.restaurant_id) {
            toast.warning("Silakan pilih restoran");
            return;
        }

        // Set loading state
        setIsSubmitting(true);

        try {
            // Separate new images from existing images
            const newImages = images.filter(
                (img) => !img.isExisting && img.file
            );
            const existingImages = images.filter((img) => img.isExisting);

            // Find deleted images (compare with original foodData.images)
            const deletedImageIds = [];
            if (foodData.images) {
                foodData.images.forEach((originalImg) => {
                    const stillExists = existingImages.find(
                        (img) => img.id === originalImg.id
                    );
                    if (!stillExists) {
                        deletedImageIds.push(originalImg.id);
                    }
                });
            }

            // Prepare images data in the format expected by API service
            const formData = { ...data };

            // Only add images data if there are changes
            if (newImages.length > 0 || deletedImageIds.length > 0) {
                formData.images = {
                    new_images: newImages,
                    deleted_image_ids: deletedImageIds,
                };
            }

            console.log("Sending form data:", formData); // Debug log
            console.log("New images:", newImages.length); // Debug log
            console.log("Deleted image IDs:", deletedImageIds); // Debug log

            // Submit data
            await apiService.foods.update(foodData.id, formData);
            toast.success("Makanan berhasil diperbarui");

            // Important: Call success first to update data
            if (onSuccess) {
                onSuccess();
            }

            // Reset form (do this before closing dialog)
            form.reset();
            setImages([]);

            // Close dialog (after reset)
            onOpenChange(false);
        } catch (error) {
            toast.error(
                error.message || "Gagal memperbarui makanan. Silakan coba lagi."
            );
        } finally {
            // Always reset loading state
            setIsSubmitting(false);
        }
    }

    const handleCancel = () => {
        // Reset state before closing
        setIsSubmitting(false);
        setIsUploading(false);
        form.reset();

        // Clean up images
        images.forEach((image) => {
            if (image.file && image.preview) {
                URL.revokeObjectURL(image.preview);
            }
        });
        setImages([]);

        // Then close dialog
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto z-50">
                <DialogHeader>
                    <DialogTitle>Edit Makanan</DialogTitle>
                    <DialogDescription>
                        Perbarui informasi makanan di bawah ini.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-4"
                    >
                        <div className="space-y-4 pb-4 border-b max-h-96 overflow-y-auto px-2">
                            {/* Food Images Section */}
                            <div className="space-y-2">
                                <FormLabel>Gambar Makanan</FormLabel>

                                <div className="border-2 border-dashed rounded-2xl p-3 space-y-3">
                                    {/* Dropzone */}
                                    <div
                                        {...getRootProps()}
                                        className={`rounded-lg p-4 text-center cursor-pointer transition-colors ${
                                            isDragActive
                                                ? "border-primary bg-primary/5 border-2 border-dashed"
                                                : "bg-gray-50 hover:bg-gray-100 border border-gray-200"
                                        }`}
                                    >
                                        <input {...getInputProps()} />
                                        <Upload className="mx-auto h-6 w-6 text-gray-400" />
                                        <p className="text-sm text-gray-600 mt-1">
                                            {isDragActive
                                                ? "Letakkan gambar di sini..."
                                                : "Klik atau drag gambar"}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            JPG, PNG, GIF, WEBP (maks 5MB)
                                        </p>
                                    </div>

                                    {/* Loading */}
                                    {isUploading && (
                                        <div className="flex items-center justify-center p-2 gap-2">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
                                            <span className="text-sm text-gray-600">
                                                Mengunggah...
                                            </span>
                                        </div>
                                    )}

                                    {/* Image Previews */}
                                    {images.length > 0 && (
                                        <div className="space-y-2">
                                            <div className="text-sm font-medium text-gray-700">
                                                Preview ({images.length} gambar)
                                            </div>
                                            <div className="flex flex-wrap gap-2">
                                                {images.map((img, i) => (
                                                    <div
                                                        key={img.id || i}
                                                        className={`group relative rounded-md overflow-hidden border ${
                                                            img.isMain
                                                                ? "ring-2 ring-primary"
                                                                : ""
                                                        }`}
                                                    >
                                                        <img
                                                            src={img.preview}
                                                            alt={`Pratinjau ${
                                                                i + 1
                                                            }`}
                                                            className="size-12 object-cover"
                                                            onError={(e) =>
                                                                (e.target.src =
                                                                    "https://via.placeholder.com/150?text=Error")
                                                            }
                                                        />
                                                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                                                            <Button
                                                                type="button"
                                                                variant="secondary"
                                                                size="sm"
                                                                disabled={
                                                                    img.isMain
                                                                }
                                                                onClick={() =>
                                                                    handleSetMainImage(
                                                                        i
                                                                    )
                                                                }
                                                                className="h-5 w-5 p-0"
                                                            >
                                                                <ImagePlus className="h-3 w-3" />
                                                            </Button>
                                                            <Button
                                                                type="button"
                                                                variant="destructive"
                                                                size="sm"
                                                                onClick={() =>
                                                                    handleRemoveImage(
                                                                        i
                                                                    )
                                                                }
                                                                className="h-5 w-5 p-0"
                                                            >
                                                                <X className="h-3 w-3" />
                                                            </Button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
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
                                            <FormControl>
                                                <Combobox
                                                    className="truncate"
                                                    items={restaurants.map(
                                                        (restaurant) => ({
                                                            value: restaurant.id,
                                                            label: restaurant.name,
                                                        })
                                                    )}
                                                    value={field.value}
                                                    onValueChange={
                                                        field.onChange
                                                    }
                                                    placeholder="Pilih restoran..."
                                                    searchPlaceholder="Cari restoran..."
                                                    emptyText="Restoran tidak ditemukan."
                                                />
                                            </FormControl>
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
                                            value={field.value}
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
                        </div>

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleCancel}
                                disabled={isSubmitting || isUploading}
                            >
                                Batal
                            </Button>
                            <Button
                                type="submit"
                                disabled={isSubmitting || isUploading}
                            >
                                {isSubmitting
                                    ? "Memperbarui..."
                                    : "Perbarui Makanan"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
