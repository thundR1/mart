"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { fetchOrders } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";
import type { Order } from "@/lib/types";

function OrdersContent() {
  const params = useSearchParams();
  const justPlaced = params.get("justPlaced");
  const { user, loading: authLoading } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      setLoading(false);
      return;
    }
    fetchOrders()
      .then(setOrders)
      .catch(() => setOrders([]))
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  if (!authLoading && !user) {
    return (
      <div className="py-16 text-center">
        <p className="text-muted">Sign in to see your order history.</p>
        <Link href="/login?next=/orders" className="mt-4 inline-block text-primary">
          Sign in &rarr;
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-2 font-display text-2xl text-ink">Your orders</h1>
      {justPlaced && (
        <p className="mb-6 rounded-sm border border-primary bg-primary/5 px-4 py-3 text-sm text-primary">
          Order #{justPlaced} placed. Head back to the homepage - your recommendations have already
          started adjusting to what you just bought.
        </p>
      )}
      {loading ? (
        <p className="text-muted">Loading...</p>
      ) : orders.length === 0 ? (
        <p className="text-muted">No orders yet.</p>
      ) : (
        <div className="flex flex-col gap-6">
          {orders.map((order) => (
            <div key={order.id} className="rounded-sm border border-border bg-surface p-5">
              <div className="mb-3 flex justify-between text-sm text-muted">
                <span>Order #{order.id}</span>
                <span>{new Date(order.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex flex-col gap-2">
                {order.items.map((item, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className="text-ink">
                      {item.product.name} &times; {item.quantity}
                    </span>
                    <span className="font-mono text-ink">
                      ${(item.price_at_purchase * item.quantity).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-between border-t border-border pt-3 font-display text-ink">
                <span>Total</span>
                <span className="font-mono">${order.total.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function OrdersPage() {
  return (
    <Suspense fallback={<p className="text-muted">Loading...</p>}>
      <OrdersContent />
    </Suspense>
  );
}
