import { userContext } from "@/contexts/context";
import { redirect } from "react-router";

async function adminMiddleware({ context }) {
    try {
        const user = JSON.parse(localStorage.getItem("user"));
        const is_admin = user && user.role === "admin";
        console.log({ is_admin });
        if (!user) {
            throw redirect("/login");
        }

        if (!is_admin) {
            console.log("Admin Middleware - Not Authorized");
            throw redirect("/");
        }
        context.set(userContext, user);
    } catch (error) {
        console.error("Admin Middleware Error:", error);
        throw redirect("/login");
    }
}

export default adminMiddleware;
