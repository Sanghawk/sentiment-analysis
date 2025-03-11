"use client";
import { usePathname } from "next/navigation";
import { BeakerIcon, HomeIcon } from "@heroicons/react/24/outline";

import Link from "next/link";

export function DashboardSidebarNavigation() {
  const pathname = usePathname(); // Get current route

  return (
    <nav className="flex flex-col gap-8">
      <ul className="flex flex-col gap-2">
        <li>
          <Link
            href="/dashboard"
            className={`group inline-flex items-center gap-3 text-sm/6 
              ${
                pathname === "/dashboard"
                  ? "font-semibold text-base-950 dark:text-base-200"
                  : "text-base-600 dark:text-base-300 hover:text-base-950 dark:hover:text-base-200"
              }
            `}
            aria-current={pathname === "/dashboard" ? "page" : undefined}
          >
            <HomeIcon className="size-4" />
            Default
          </Link>
        </li>
        <li>
          <Link
            href="/dashboard/playground"
            className={`group inline-flex items-center gap-3 text-sm/6 
              ${
                pathname === "/dashboard/playground"
                  ? "font-semibold text-base-950 dark:text-base-200"
                  : "text-base-600 dark:text-base-300 hover:text-base-950 dark:hover:text-base-200"
              }
            `}
            aria-current={
              pathname === "/dashboard/playground" ? "page" : undefined
            }
          >
            <BeakerIcon className="size-4" />
            Playground
          </Link>
        </li>
      </ul>
    </nav>
  );
}
