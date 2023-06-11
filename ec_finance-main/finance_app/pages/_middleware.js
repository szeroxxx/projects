import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";

export async function middleware(req, ev) {
  const session = await getToken({ req: req, secret: process.env.SECRET });

  // Allow to access post login page if session exist
 
  if (session) return NextResponse.next();
 
  // Add exception to allow request without session
  let unprotectedRoutes = ["/dt/accounts/auth_user/", "logo.png", "/favicon.ico"];
  if (unprotectedRoutes.includes(req.url)) {
    return NextResponse.next();
  }
  if (req.url.includes("/login")) {
    return NextResponse.redirect("/api/auth/signin/");
  }
  if (req.url.indexOf("/api/auth/") >= 0||req.url.indexOf("favicon.ico") >= 0   || req.url.indexOf("/account/Failure") >= 0 || req.url.indexOf("logo.png") >= 0) {
    return NextResponse.next();
  }

  // Stop redirection loop for login page
  if (!req.url.includes("/signin")) {
    return NextResponse.redirect("/api/auth/signin/");
  }
}
