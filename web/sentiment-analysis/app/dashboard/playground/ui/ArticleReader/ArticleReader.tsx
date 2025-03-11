"use client";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";

export function ArticleReader() {
  const { content, selectedArticle } = useDashboardContext();
  return (
    <div className="mx-auto prose prose-zinc dark:prose-invert pb-24">
      <h1>{selectedArticle?.content_title}</h1>
      {content}
    </div>
  );
}
