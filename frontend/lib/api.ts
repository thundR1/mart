import { getSessionId } from "./session";
import type {
  Product,
  ProductWithReason,
  User,
  CartItem,
  Order,
  EventType,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "mart_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Session-Id": getSessionId(),
    ...(options.headers as Record<string, string> | undefined),
  };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const registerUser = (email: string, password: string, name: string) =>
  request<{ access_token: string; user: User }>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });

export const loginUser = (email: string, password: string) =>
  request<{ access_token: string; user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const fetchMe = () => request<User>("/auth/me");

export const fetchProducts = (category?: string) =>
  request<Product[]>(
    `/products${category ? `?category=${encodeURIComponent(category)}` : ""}`,
  );

export const fetchCategories = () => request<string[]>("/products/categories");

export const fetchProduct = (id: number) => request<Product>(`/products/${id}`);

export const searchProducts = (query: string) =>
  request<ProductWithReason[]>(
    `/products/search?query=${encodeURIComponent(query)}`,
  );

export const logActivity = (
  event_type: EventType,
  product_id?: number,
  query?: string,
) =>
  request("/activity", {
    method: "POST",
    body: JSON.stringify({ event_type, product_id, query }),
  }).catch(() => {});

export const fetchForYou = (limit = 8) =>
  request<ProductWithReason[]>(`/recommendations/for-you?limit=${limit}`);

export const fetchSimilar = (productId: number, limit = 6) =>
  request<Product[]>(`/recommendations/similar/${productId}?limit=${limit}`);

export const fetchCart = () => request<CartItem[]>("/cart");

export const addToCart = (product_id: number, quantity = 1) =>
  request<CartItem>("/cart", {
    method: "POST",
    body: JSON.stringify({ product_id, quantity }),
  });

export const removeFromCart = (itemId: number) =>
  request<void>(`/cart/${itemId}`, { method: "DELETE" });

export const checkout = () =>
  request<Order>("/orders/checkout", { method: "POST" });

export const fetchOrders = () => request<Order[]>("/orders");
