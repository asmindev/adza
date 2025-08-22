import * as z from "zod";

// Validation schema for restaurant form
export const restaurantSchema = z.object({
    name: z.string().min(1, "Nama restoran wajib diisi"),
    description: z.string().min(1, "Deskripsi wajib diisi"),
    address: z.string().min(1, "Alamat wajib diisi"),
    phone: z.string().min(1, "Nomor telepon wajib diisi"),
    email: z.string().email("Format email tidak valid"),
    latitude: z.number().optional(),
    longitude: z.number().optional(),
    is_active: z.boolean().default(true),
});

// For future additions or validations specific to restaurant edit form
export const editRestaurantSchema = restaurantSchema;
