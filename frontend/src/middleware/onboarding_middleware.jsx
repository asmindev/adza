import { userContext } from "@/contexts/context";

async function onboardingMiddleware({ context }, next) {
    console.log("Onboarding Middleware - Checking onboarding status");
    const user = JSON.parse(localStorage.getItem("user"));
    console.log({ user });
    if (user) {
        const hasCompletedOnboarding = user.onboarding_completed;
        console.log({ hasCompletedOnboarding });
        if (!hasCompletedOnboarding) {
            console.log("Onboarding Middleware - Redirecting to preferences");
            window.location.href = "/preferences";
            return;
        }
        context.set(userContext, user);
    }
    await next();
}

export default onboardingMiddleware;
