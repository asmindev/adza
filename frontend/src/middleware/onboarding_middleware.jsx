import { redirect } from "react-router";

async function onboardingMiddleware({ request }, next) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    console.log("Onboarding Middleware - Current Path:", pathname);

    // Allow preferences page to load
    if (pathname === "/preferences") {
        console.log("Onboarding Middleware - On Preferences Page");
        return await next();
    }

    console.log("Onboarding Middleware - Checking onboarding status");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (user) {
        const hasCompletedOnboarding = user.onboarding_completed;
        console.log(
            "Onboarding Middleware - User onboarding status:",
            hasCompletedOnboarding
        );

        if (!hasCompletedOnboarding) {
            console.log(
                "Onboarding Middleware - Redirecting to preferences (onboarding not completed)"
            );
            window.location.href = "/preferences";
        }
    }

    // If onboarding is completed or no user, continue to next middleware/route
    return await next();
}

export default onboardingMiddleware;
