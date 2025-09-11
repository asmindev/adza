import { userContext } from "@/contexts/context";
import { redirect } from "react-router";

async function adminMiddleware({ context }, next) {
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (!user) {
        throw redirect("/login");
    }

    const is_admin = user && user.role === "admin";
    if (!is_admin) {
        console.log("Admin Middleware - Not Authorized");
        throw redirect("/");
    }

    context.set(userContext, user);
    return next();
}

export default adminMiddleware;
