"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useCart } from "@/contexts/cart-context";
import { useAuth } from "@/contexts/auth-context";
import { checkout } from "@/lib/api";
import { productImageUrl } from "@/lib/types";

export default function CartPage() {
  const { items, loading, removeItem, refresh } = useCart();
  const { user } = useAuth();
  const router = useRouter();
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState("");

  const total = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);

  async function handleCheckout() {
    if (!user) {
      router.push("/login?next=/cart");
      return;
    }
    setPlacing(true);
    setError("");
    try {
      const order = await checkout();
      await refresh();
      router.push(`/orders?justPlaced=${order.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Checkout failed");
    } finally {
      setPlacing(false);
    }
  }

  if (loading) return <p className="text-muted">Loading cart...</p>;

  if (items.length === 0) {
    return (
      <div className="py-16 text-center">
        <p className="text-muted">Your cart is empty.</p>
        <Link href="/" className="mt-4 inline-block text-primary">
          Continue shopping &rarr;
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
      <div className="flex flex-col gap-4 lg:col-span-2">
        {items.map((item) => (
          <div key={item.id} className="flex items-center gap-4 border-b border-border pb-4">
            <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-sm border border-border">
              <Image src={productImageUrl(item.product.image_seed, 200)} alt={item.product.name} fill className="object-cover" />
            </div>
            <div className="flex-1">
              <p className="font-display text-lg text-ink">{item.product.name}</p>
              <p className="text-sm text-muted">Qty {item.quantity}</p>
            </div>
            <p className="font-mono text-ink">${(item.product.price * item.quantity).toFixed(2)}</p>
            <button onClick={() => removeItem(item.id)} className="text-sm text-muted hover:text-primary">
              Remove
            </button>
          </div>
        ))}
      </div>
      <div className="h-fit rounded-sm border border-border bg-surface p-5">
        <div className="flex justify-between pb-2 text-sm text-muted">
          <span>Subtotal</span>
          <span className="font-mono">${total.toFixed(2)}</span>
        </div>
        <div className="flex justify-between border-t border-border py-3 font-display text-lg text-ink">
          <span>Total</span>
          <span className="font-mono">${total.toFixed(2)}</span>
        </div>
        {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
        <button
          onClick={handleCheckout}
          disabled={placing}
          className="w-full rounded-sm bg-primary py-3 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
        >
          {placing ? "Placing order..." : "Checkout"}
        </button>
        {!user && <p className="mt-2 text-xs text-muted">You'll be asked to sign in first.</p>}
      </div>
    </div>
  );
}
