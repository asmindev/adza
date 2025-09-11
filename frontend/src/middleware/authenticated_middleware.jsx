import { userContext } from "@/contexts/context";
import { redirect } from "react-router";

export default async function auth({ request, context }) {
    const user = JSON.parse(localStorage.getItem("user") || "null");
    const url = new URL(request.url);

    // Jika sudah login & mau ke login/register, arahkan ke dashboard
    if (user && (url.pathname === "/login" || url.pathname === "/register")) {
        console.log(
            "Authenticated Middleware - Already Authenticated, redirecting"
        );
        throw redirect("/dashboard");
    }

    // Jika belum login & mau ke route yang butuh login → arahkan ke /login
    if (!user && url.pathname !== "/login" && url.pathname !== "/register") {
        console.log("Authenticated Middleware - Not Authenticated");
        throw redirect("/login");
    }

    // kalau lolos, lanjut ke halaman tujuan
    return null;
}

export const profileLoader = async ({ context }) => {
    const user = context.get(userContext);
    return user;
};
