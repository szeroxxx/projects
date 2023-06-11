// import { appRoutes } from "../constants";
import { useSession } from "next-auth/react";

//check if you are on the client (browser) or server
const isBrowser = () => typeof window !== "undefined";

const ProtectedRoute = ({ router, children }) => {
  //Identify authenticated user
  const { data: session, status } = useSession();
  const loading = status === "loading";

  //   let unprotectedRoutes = [
  //     appRoutes.LOGIN_PAGE,
  //   ];
  let unprotectedRoutes = ["/login"];

  /**
   * @var pathIsProtected Checks if path exists in the unprotectedRoutes routes array
   */

  let pathIsProtected = unprotectedRoutes.indexOf(router.pathname) === -1;

  if (isBrowser() && !loading && !session && pathIsProtected) {
    router.push("login");
  }

  return children;
};

export default ProtectedRoute;
