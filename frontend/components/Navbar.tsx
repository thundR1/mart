"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";
import { useCart } from "@/contexts/cart-context";
import SearchBar from "./SearchBar";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();

  return (
    <header className="border-b border-border bg-surface">
      <div className="container-page flex flex-wrap items-center gap-4 py-4">
        <Link href="/" className="font-display text-2xl tracking-tight text-ink">
          Meridian
        </Link>
        <div className="order-3 w-full sm:order-none sm:w-auto sm:flex-1">
          <SearchBar />
        </div>
        <nav className="ml-auto flex items-center gap-5 text-sm">
          <Link href="/cart" className="text-ink hover:text-primary">
            Cart{count > 0 ? ` (${count})` : ""}
          </Link>
          {user ? (
            <>
              <Link href="/orders" className="text-ink hover:text-primary">
                Orders
              </Link>
              <button onClick={logout} className="text-muted hover:text-primary">
                Sign out ({user.name})
              </button>
            </>
          ) : (
            <Link href="/login" className="text-ink hover:text-primary">
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
