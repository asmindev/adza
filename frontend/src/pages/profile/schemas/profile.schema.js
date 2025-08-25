import { z } from "zod";

// Profile schema untuk validasi
export const profileSchema = z.object({
    name: z
        .string()
        .min(2, "Nama minimal 2 karakter")
        .max(50, "Nama maksimal 50 karakter"),
    email: z.string().email("Format email tidak valid"),
    bio: z.string().max(200, "Bio maksimal 200 karakter").optional(),
    avatar: z
        .string()
        .url("URL avatar tidak valid")
        .optional()
        .or(z.literal("")),
});

// Schema untuk update password
export const passwordSchema = z
    .object({
        currentPassword: z.string().min(1, "Password saat ini wajib diisi"),
        newPassword: z.string().min(6, "Password baru minimal 6 karakter"),
        confirmPassword: z.string(),
    })
    .refine((data) => data.newPassword === data.confirmPassword, {
        message: "Password tidak cocok",
        path: ["confirmPassword"],
    });

// Default values
export const defaultProfileValues = {
    name: "",
    email: "",
    bio: "",
    avatar: "",
};

export const defaultPasswordValues = {
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
};
