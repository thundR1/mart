"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchForYou, fetchProducts, fetchCategories } from "@/lib/api";
import type { ProductWithReason, Product } from "@/lib/types";
import RecommendationRow from "@/components/RecommendationRow";
import ProductGrid from "@/components/ProductGrid";

export default function HomePage() {
  const [forYou, setForYou] = useState<ProductWithReason[]>([]);
  const [byCategory, setByCategory] = useState<Record<string, Product[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [recs, categories] = await Promise.all([fetchForYou(8), fetchCategories()]);
      setForYou(recs);

      const entries = await Promise.all(
        categories.slice(0, 3).map(async (category) => {
          const products = await fetchProducts(category);
          return [category, products.slice(0, 4)] as const;
        })
      );
      setByCategory(Object.fromEntries(entries));
      setLoading(false);
    }
    load();
  }, []);

  const isPersonalized = forYou.some((p) => p.reason && p.reason !== "Trending now" && p.reason !== "New arrival");

  return (
    <div>
      <section className="flex flex-col gap-4 border-b border-border pb-10 pt-4">
        <span className="text-sm uppercase tracking-widest text-muted">A demo storefront</span>
        <h1 className="max-w-2xl font-display text-4xl leading-tight text-ink sm:text-5xl">
          The more you look, the better it gets.
        </h1>
        <p className="max-w-xl text-muted">
          Every product you view, search for, or add to your cart shapes what Meridian shows you next.
          Browse a little, then come back to this page - the recommendations below are recomputed from
          your activity in real time.
        </p>
        <Link
          href="/search?q=cozy winter footwear"
          className="mt-2 w-fit rounded-sm border border-ink px-4 py-2 text-sm font-medium text-ink hover:border-primary hover:text-primary"
        >
          Try a semantic search &rarr;
        </Link>
      </section>

      {!loading && (
        <RecommendationRow
          title="Recommended for you"
          subtitle={isPersonalized ? "Based on your activity" : "Popular right now"}
          products={forYou}
        />
      )}

      {Object.entries(byCategory).map(([category, products]) => (
        <section key={category} className="border-t border-border py-8">
          <div className="mb-4 flex items-baseline justify-between">
            <h2 className="font-display text-2xl text-ink">{category}</h2>
            <Link href={`/search?category=${encodeURIComponent(category)}`} className="text-sm text-primary">
              View all
            </Link>
          </div>
          <ProductGrid products={products} />
        </section>
      ))}
    </div>
  );
}
