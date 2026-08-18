"use client";

import Image from "next/image";
import Link from "next/link";
import { productImageUrl } from "@/lib/types";
import type { ProductWithReason } from "@/lib/types";

export default function ProductCard({ product }: { product: ProductWithReason }) {
  return (
    <Link
      href={`/products/${product.id}`}
      className="group flex w-full flex-col overflow-hidden rounded-sm border border-border bg-surface transition-colors hover:border-primary"
    >
      <div className="relative aspect-square w-full overflow-hidden bg-bg">
        <Image
          src={productImageUrl(product.image_seed)}
          alt={product.name}
          fill
          sizes="(max-width: 768px) 50vw, 25vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {product.reason && (
          <span className="absolute left-2 top-2 rounded-sm bg-accent px-2 py-1 text-[11px] font-medium leading-none text-ink shadow-sm">
            {product.reason}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-1 p-3">
        <span className="text-[11px] uppercase tracking-wide text-muted">{product.category}</span>
        <h3 className="font-display text-base leading-snug text-ink">{product.name}</h3>
        <span className="mt-auto pt-1 font-mono text-sm text-ink">${product.price.toFixed(2)}</span>
      </div>
    </Link>
  );
}
