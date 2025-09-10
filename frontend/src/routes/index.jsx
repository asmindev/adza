import ADMIN_ROUTES from "./admin";
import REGULAR_ROUTES from "./reguler";
import {
    createBrowserRouter,
    unstable_RouterContextProvider,
} from "react-router";
import { userContext } from "@/contexts/context";

const ROUTES = [...ADMIN_ROUTES, ...REGULAR_ROUTES];

const router = createBrowserRouter([...ROUTES], {});

export default router;
