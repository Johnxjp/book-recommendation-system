"use client";

import type { Shelf } from "@/lib/types";

const tabs: { label: string; value: Shelf | null }[] = [
  { label: "All", value: null },
  { label: "Read", value: "read" },
  { label: "To Read", value: "to-read" },
  { label: "Reading", value: "is-reading" },
  { label: "Did Not Finish", value: "did-not-finish" },
];

interface ShelfTabsProps {
  active: Shelf | null;
  onSelect: (shelf: Shelf | null) => void;
}

export function ShelfTabs({ active, onSelect }: ShelfTabsProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      {tabs.map((tab) => (
        <button
          key={tab.label}
          onClick={() => onSelect(tab.value)}
          className={`px-4 py-1.5 rounded-full text-sm transition-colors ${
            active === tab.value
              ? "bg-sage text-white"
              : "bg-earth-light/20 text-stone hover:bg-earth-light/40 hover:text-charcoal"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
