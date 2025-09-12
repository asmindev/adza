import { redirect } from "react-router";

async function onboardingMiddleware({ request }, next) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    console.log("Onboarding Middleware - Current Path:", pathname);

    if (pathname === "/login" || pathname === "/register") {
        console.log("Onboarding Middleware - Already Authenticated");
        await next();
    }

    if (pathname === "/preferences") {
        console.log("Onboarding Middleware - On Preferences Page");
        await next();
    }

    console.log("Onboarding Middleware - Checking onboarding status");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (user) {
        const hasCompletedOnboarding = user.onboarding_completed;
        if (!hasCompletedOnboarding) {
            console.log("Onboarding Middleware - Redirecting to preferences");
            window.location.href = "/preferences";
        }
    }
}

export default onboardingMiddleware;
