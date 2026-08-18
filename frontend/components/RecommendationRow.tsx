import ProductCard from "./ProductCard";
import type { ProductWithReason } from "@/lib/types";

export default function RecommendationRow({
  title,
  subtitle,
  products,
}: {
  title: string;
  subtitle?: string;
  products: ProductWithReason[];
}) {
  if (products.length === 0) return null;
  return (
    <section className="py-8">
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="font-display text-2xl text-ink">{title}</h2>
        {subtitle && <span className="text-sm text-muted">{subtitle}</span>}
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
