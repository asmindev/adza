import { redirect } from "react-router";

async function onboardingMiddleware({ request }, next) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Skip middleware for auth pages and preferences page
    if (
        pathname === "/login" ||
        pathname === "/register" ||
        pathname === "/preferences"
    ) {
        return next();
    }

    console.log("Onboarding Middleware - Checking onboarding status");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (user) {
        const hasCompletedOnboarding = user.onboarding_completed;
        if (!hasCompletedOnboarding) {
            console.log("Onboarding Middleware - Redirecting to preferences");
            throw redirect("/preferences");
        }
    }

    return next();
}

export default onboardingMiddleware;
