"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import { fetchProduct, fetchSimilar, logActivity, addToCart } from "@/lib/api";
import { productImageUrl } from "@/lib/types";
import type { Product } from "@/lib/types";
import RecommendationRow from "@/components/RecommendationRow";
import { useCart } from "@/contexts/cart-context";

export default function ProductPage() {
  const params = useParams<{ id: string }>();
  const productId = Number(params.id);

  const [product, setProduct] = useState<Product | null>(null);
  const [similar, setSimilar] = useState<Product[]>([]);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const { refresh } = useCart();

  useEffect(() => {
    if (!productId) return;
    fetchProduct(productId).then(setProduct);
    fetchSimilar(productId).then(setSimilar);
    logActivity("view", productId);
  }, [productId]);

  async function handleAddToCart() {
    setAdding(true);
    try {
      await addToCart(productId, 1);
      setAdded(true);
      await refresh();
    } finally {
      setAdding(false);
    }
  }

  if (!product) {
    return <p className="py-16 text-center text-muted">Loading...</p>;
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-10 sm:grid-cols-2">
        <div className="relative aspect-square overflow-hidden rounded-sm border border-border bg-surface">
          <Image
            src={productImageUrl(product.image_seed, 700)}
            alt={product.name}
            fill
            className="object-cover"
          />
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-sm uppercase tracking-wide text-muted">
            {product.category}
          </span>
          <h1 className="font-display text-3xl text-ink">{product.name}</h1>
          <p className="font-mono text-xl text-ink">
            ${product.price.toFixed(2)}
          </p>
          <p className="leading-relaxed text-muted">{product.description}</p>
          <button
            onClick={handleAddToCart}
            disabled={adding}
            className="mt-2 w-fit rounded-sm bg-primary px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-dark disabled:opacity-60"
          >
            {added ? "Added to cart" : adding ? "Adding..." : "Add to cart"}
          </button>
          <span className="text-xs text-muted">{product.stock} in stock</span>
        </div>
      </div>

      <RecommendationRow title="You might also like" products={similar} />
    </div>
  );
}
