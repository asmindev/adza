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
import { foodUpdateSchema } from "@/dashboard/forms/foodSchema";
import apiService from "@/dashboard/services/api";
import { Upload, X, ImagePlus } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import useSWR from "swr";

export default function EditFoodDialog({
    open,
    onOpenChange,
    foodData,
    onSuccess,
}) {
    const [images, setImages] = useState([]);
    const [deletedImageIds, setDeletedImageIds] = useState([]);
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
        resolver: zodResolver(foodUpdateSchema),
        defaultValues: {
            name: "",
            description: "",
            category: "",
            price: 0,
            restaurant_id: "",
            ingredients: [],
            status: "active",
        },
    });

    // Reset form and images when food data changes
    useEffect(() => {
        if (foodData) {
            form.reset({
                name: foodData.name || "",
                description: foodData.description || "",
                category: foodData.category || "",
                price: foodData.price || 0,
                restaurant_id: foodData.restaurant_id || "",
                ingredients: foodData.ingredients || [],
                status: foodData.status || "active",
            });

            // Initialize images from food data
            if (foodData.images && foodData.images.length > 0) {
                const existingImages = foodData.images.map((img, index) => ({
                    id: img.id,
                    url: img.image_url,
                    preview: img.image_url,
                    status: "existing",
                    isMain: img.is_main,
                    existingIndex: index,
                }));

                setImages(existingImages);
            } else if (foodData.main_image) {
                // Legacy: if only main_image is available
                setImages([
                    {
                        id: foodData.main_image.id,
                        url: foodData.main_image.image_url,
                        preview: foodData.main_image.image_url,
                        status: "existing",
                        isMain: true,
                        existingIndex: 0,
                    },
                ]);
            } else {
                setImages([]);
            }

            // Reset removed image IDs
            setDeletedImageIds([]);
        }
    }, [foodData, form]);

    // Clear deletedImageIds when dialog is closed
    useEffect(() => {
        if (!open) {
            setDeletedImageIds([]);
        }
    }, [open]);

    // File dropzone setup for new images
    const onDrop = useCallback((acceptedFiles) => {
        setIsUploading(true);

        // Process each file
        const newImages = acceptedFiles.map((file) => ({
            file,
            preview: URL.createObjectURL(file),
            status: "new", // 'new' for newly uploaded files
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
            toast.error("Please enter a valid image URL");
            return;
        }

        setImages((prev) => {
            const newImage = {
                url,
                preview: url,
                status: "new_url", // 'new_url' for new URL-based images
                isMain: prev.length === 0, // Make it main if it's the first image
            };

            if (prev.length === 0) {
                newImage.isMain = true;
            }

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
        const imageToRemove = images[index];

        // If removing an existing image, add its ID to deletedImageIds
        if (imageToRemove.status === "existing" && imageToRemove.id) {
            setDeletedImageIds((prev) => [...prev, imageToRemove.id]);
        }

        setImages((prev) => {
            const filtered = prev.filter((_, i) => i !== index);

            // If we removed the main image, set a new one
            if (imageToRemove.isMain && filtered.length > 0) {
                const newMainIndex = index < filtered.length ? index : 0;
                filtered[newMainIndex].isMain = true;
            }

            return filtered;
        });

        // Revoke object URL to prevent memory leaks
        if (imageToRemove.file) {
            URL.revokeObjectURL(imageToRemove.preview);
        }
    };

    const isSubmitting = form.formState.isSubmitting;

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

            // Prepare the images data for the API
            const imagesData = {
                new_images: images
                    .filter(
                        (img) =>
                            img.status === "new" || img.status === "new_url"
                    )
                    .map((img) => ({
                        image_url: img.url || "", // URL for remote images
                        file: img.file || null, // File object for uploaded files
                        is_main: img.isMain,
                    })),
                deleted_image_ids: deletedImageIds,
            };

            // Add images to form data
            const formData = {
                ...data,
                images: imagesData,
            };

            await apiService.foods.update(foodData.id, formData);
            toast.success("Makanan berhasil diperbarui");
            // onOpenChange(false);
            if (onSuccess) onSuccess();
        } catch (error) {
            toast.error(
                error.message || "Gagal memperbarui makanan. Silakan coba lagi."
            );
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Edit Makanan</DialogTitle>
                    <DialogDescription>
                        Perbarui detail makanan dan gambar.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(onSubmit)}
                        className="space-y-4"
                    >
                        {/* Food Images Section */}
                        <div className="space-y-2">
                            <FormLabel>Food Images</FormLabel>

                            {/* Image Previews */}
                            {images.length > 0 && (
                                <ScrollArea className="h-60 w-full rounded-md border p-2 mb-2">
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
                                                    alt={`Preview ${index + 1}`}
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
                                                                Set as main
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
                                                                Remove
                                                            </span>
                                                        </Button>
                                                    </div>
                                                </div>

                                                {image.isMain && (
                                                    <div className="absolute top-0 left-0 bg-primary text-white text-xs px-1 py-0.5">
                                                        Main
                                                    </div>
                                                )}

                                                {image.status ===
                                                    "existing" && (
                                                    <div className="absolute bottom-0 right-0 bg-blue-500 text-white text-xs px-1 py-0.5">
                                                        Existing
                                                    </div>
                                                )}

                                                {image.status === "new" && (
                                                    <div className="absolute bottom-0 right-0 bg-green-500 text-white text-xs px-1 py-0.5">
                                                        New
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            )}

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
                                            Drop the images here...
                                        </p>
                                    ) : (
                                        <>
                                            <p className="text-sm text-gray-600">
                                                Add more images: drop files here
                                                or click to select
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                Supports: JPG, PNG, GIF, WEBP
                                                (max 5MB)
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
                                                    placeholder="Or enter image URL: https://example.com/image.jpg"
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
                                    Add URL
                                </Button>
                            </div>

                            {/* Loading indicator */}
                            {isUploading && (
                                <div className="flex items-center justify-center p-4">
                                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                    <span className="ml-2 text-sm text-gray-600">
                                        Uploading...
                                    </span>
                                </div>
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
                                            value={field.value}
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

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <FormField
                                control={form.control}
                                name="category"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Kategori</FormLabel>
                                        <FormControl>
                                            <Input
                                                placeholder="Kategori"
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

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
