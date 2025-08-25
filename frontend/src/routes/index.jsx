import ADMIN_ROUTES from "./admin";
import REGULAR_ROUTES from "./reguler";
import {
    createBrowserRouter,
    unstable_RouterContextProvider,
} from "react-router";
import { userContext } from "@/contexts/context";

const ROUTES = [...ADMIN_ROUTES, ...REGULAR_ROUTES];

const router = createBrowserRouter([...ROUTES], {
    unstable_getContext() {
        const user = {
            id: 1,
            name: "John Doe",
            email: "john.doe@example.com",
        };
        let context = new unstable_RouterContextProvider();
        context.set(userContext, user);
        return context;
    },
});

export default router;
