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
  return (
    <tr className={className} onClick={() => selectArticle(data)}>
      {children}
    </tr>
  );
}
