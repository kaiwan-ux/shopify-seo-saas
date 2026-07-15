import { NextRequest, NextResponse } from "next/server";

const publicRoutes = ["/", "/login", "/register", "/forgot-password"];

export function middleware(request: NextRequest) {
  // Temporarily allow all routes for initial deployment
  // TODO: Re-enable auth check after testing
  return NextResponse.next();
  
  // const isPublic = publicRoutes.includes(request.nextUrl.pathname);
  // const hasSession = request.cookies.has("seo_session");
  // if (!isPublic && !hasSession && process.env.NODE_ENV === "production") {
  //   return NextResponse.redirect(new URL("/login", request.url));
  // }
  // return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
