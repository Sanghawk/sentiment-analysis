"use client";

import { Article } from "@/types";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";

export function RoutingTableRow({
  children,
  className,
  data,
}: Readonly<{
  children: React.ReactNode;
  className: string;
  data: Article;
}>) {
  const { selectedArticle, selectArticle } = useDashboardContext();
  const isSelected = selectedArticle?.id === data.id;

  return (
    <tr
      className={`${className} ${
        isSelected ? "font-bold" : "hover:font-semibold cursor-pointer"
      }`}
      onClick={() => {
        // Prevent duplicate calls if the row is already selected.
        if (!isSelected) {
          selectArticle(data);
        }
      }}
    >
      {children}
    </tr>
  );
}
