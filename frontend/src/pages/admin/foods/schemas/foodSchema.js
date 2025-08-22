import { z } from "zod";

export const foodSchema = z.object({
    name: z
        .string()
        .min(3, { message: "Nama makanan harus minimal 3 karakter" })
        .max(100, {
            message: "Nama makanan tidak boleh lebih dari 100 karakter",
        }),
    description: z
        .string()
        .min(10, { message: "Deskripsi harus minimal 10 karakter" })
        .max(500, { message: "Deskripsi tidak boleh lebih dari 500 karakter" }),
    category: z
        .string()
        .min(2, { message: "Kategori harus minimal 2 karakter" })
        .max(50, { message: "Kategori tidak boleh lebih dari 50 karakter" }),
    price: z
        .number({
            required_error: "Harga diperlukan",
            invalid_type_error: "Harga harus berupa angka",
        })
        .min(0, { message: "Harga tidak boleh negatif" })
        .or(
            z
                .string()
                .regex(/^\d+(\.\d{1,2})?$/)
                .transform((val) => parseFloat(val))
        ),
    restaurant_id: z.string().min(1, { message: "Restoran harus dipilih" }),
    ingredients: z.array(z.string()).optional().default([]),
    image: z
        .string()
        .url({ message: "Mohon masukkan URL gambar yang valid" })
        .optional()
        .or(z.literal("")),
    status: z.enum(["active", "inactive", "pending"], {
        required_error: "Status diperlukan",
    }),
});

export const foodCreateSchema = foodSchema;

export const foodUpdateSchema = foodSchema.partial();
