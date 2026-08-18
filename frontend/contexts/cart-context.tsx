"use client";

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { fetchCart, addToCart as apiAddToCart, removeFromCart as apiRemoveFromCart, logActivity } from "@/lib/api";
import type { CartItem } from "@/lib/types";
import { useAuth } from "./auth-context";

interface CartContextValue {
  items: CartItem[];
  count: number;
  loading: boolean;
  addItem: (productId: number, quantity?: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  refresh: () => Promise<void>;
}

const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const refresh = useCallback(async () => {
    try {
      const data = await fetchCart();
      setItems(data);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh, user]);

  async function addItem(productId: number, quantity = 1) {
    await apiAddToCart(productId, quantity);
    await refresh();
  }

  async function removeItem(itemId: number) {
    await apiRemoveFromCart(itemId);
    await refresh();
  }

  const count = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <CartContext.Provider value={{ items, count, loading, addItem, removeItem, refresh }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
