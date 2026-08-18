"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { searchProducts, fetchProducts, logActivity } from "@/lib/api";
import type { ProductWithReason } from "@/lib/types";
import ProductGrid from "@/components/ProductGrid";

function SearchContent() {
  const params = useSearchParams();
  const q = params.get("q");
  const category = params.get("category");

  const [results, setResults] = useState<ProductWithReason[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    if (q) {
      searchProducts(q).then((data) => {
        setResults(data);
        setLoading(false);
      });
      logActivity("search", undefined, q);
    } else if (category) {
      fetchProducts(category).then((data) => {
        setResults(data);
        setLoading(false);
      });
    } else {
      fetchProducts().then((data) => {
        setResults(data);
        setLoading(false);
      });
    }
  }, [q, category]);

  return (
    <div>
      <div className="mb-6 border-b border-border pb-4">
        <h1 className="font-display text-2xl text-ink">
          {q ? `Results for "${q}"` : category ? category : "All products"}
        </h1>
        {q && <p className="mt-1 text-sm text-muted">Matched by meaning using product embeddings, not just keywords.</p>}
      </div>
      {loading ? <p className="text-muted">Searching...</p> : <ProductGrid products={results} />}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<p className="text-muted">Loading...</p>}>
      <SearchContent />
    </Suspense>
  );
}
