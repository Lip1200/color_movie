import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl;
    const token = req.cookies.get('token');

    console.log('Pathname:', pathname);
    console.log('Token:', token);

    // Redirect to login if not authenticated and trying to access protected pages
    if (!token && pathname !== '/login') {
        console.log('Redirecting to login because no token is found');
        return NextResponse.redirect(new URL('/login', req.url));
    }

    // Redirect to Dashboard if authenticated and trying to access login page
    if (token && pathname === '/login') {
        console.log('Redirecting to Dashboard because token is found');
        return NextResponse.redirect(new URL('/dashboard', req.url));
    }

    return NextResponse.next();
}
