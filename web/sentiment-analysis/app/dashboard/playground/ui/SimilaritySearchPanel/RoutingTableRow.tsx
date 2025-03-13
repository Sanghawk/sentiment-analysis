"use client";

import { Article } from "@/types";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";
import { useSimilaritySearchContext } from "./SimilaritySearchProvider";

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
  const { currentQuery } = useSimilaritySearchContext();
  const isSelected = selectedArticle?.id === data.id;

  return (
    <tr
      className={`${className} ${
        isSelected ? "font-bold" : "hover:font-semibold cursor-pointer"
      }`}
      onClick={() => {
        // Prevent duplicate calls if the row is already selected.
        if (!isSelected) {
          selectArticle(data, currentQuery);
        }
      }}
    >
      {children}
    </tr>
  );
}
