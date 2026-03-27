"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Chat" },
  { href: "/library", label: "My Library" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-warm-white border-r border-earth-light/40 flex flex-col p-6">
      <h1 className="font-serif text-2xl text-charcoal mb-10 tracking-tight">
        Bookshelf
      </h1>
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-colors ${
                active
                  ? "bg-sage text-white"
                  : "text-stone hover:bg-earth-light/30 hover:text-charcoal"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
