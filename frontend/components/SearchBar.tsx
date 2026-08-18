"use client";

import { useRouter } from "next/navigation";
import { useState, FormEvent } from "react";

export default function SearchBar({ initialQuery = "" }: { initialQuery?: string }) {
  const [value, setValue] = useState(initialQuery);
  const router = useRouter();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    router.push(`/search?q=${encodeURIComponent(value.trim())}`);
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-md items-center gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search by meaning, not just keywords..."
        className="w-full rounded-sm border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-primary"
      />
      <button
        type="submit"
        className="rounded-sm bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-dark"
      >
        Search
      </button>
    </form>
  );
}
