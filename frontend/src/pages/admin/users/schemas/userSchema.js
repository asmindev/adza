import * as z from "zod";

// Form validation schema
export const userFormSchema = z.object({
    name: z.string().min(2, { message: "Nama harus minimal 2 karakter" }),
    email: z.string().email({ message: "Masukkan alamat email yang valid" }),
    role: z.enum(["user", "moderator", "admin"], {
        required_error: "Silakan pilih peran",
    }),
    status: z.enum(["active", "inactive", "pending"], {
        required_error: "Silakan pilih status",
    }),
    avatar: z
        .string()
        .url({ message: "Masukkan URL yang valid" })
        .optional()
        .or(z.literal("")),
    password: z
        .string()
        .min(6, { message: "Kata sandi harus minimal 6 karakter" })
        .optional()
        .or(z.literal("")),
});
