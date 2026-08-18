import ProductCard from "./ProductCard";
import type { ProductWithReason } from "@/lib/types";

export default function ProductGrid({ products }: { products: ProductWithReason[] }) {
  if (products.length === 0) {
    return <p className="py-12 text-center text-muted">Nothing here yet.</p>;
  }
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
