export interface Product {
  id: number;
  name: string;
  description: string;
  category: string;
  price: number;
  image_seed: string;
  stock: number;
}

export interface ProductWithReason extends Product {
  reason?: string | null;
  score?: number | null;
}

export interface User {
  id: number;
  email: string;
  name: string;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
}

export interface OrderItem {
  product: Product;
  quantity: number;
  price_at_purchase: number;
}

export interface Order {
  id: number;
  total: number;
  created_at: string;
  items: OrderItem[];
}

export type EventType = "view" | "search" | "add_to_cart" | "purchase";

export function productImageUrl(seed: string, size = 500): string {
  return `https://picsum.photos/seed/${encodeURIComponent(seed)}/${size}/${size}`;
}
