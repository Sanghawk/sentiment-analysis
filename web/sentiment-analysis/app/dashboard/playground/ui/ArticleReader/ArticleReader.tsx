"use client";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";
import { ArticleChunkSearchResult } from "@/types";
function sortById(
  contentList: ArticleChunkSearchResult[]
): ArticleChunkSearchResult[] {
  return contentList.slice().sort((a, b) => a.chunk.id - b.chunk.id);
}
export function ArticleReader() {
  const { contentList, selectedArticle } = useDashboardContext();

  return (
    <div className="mx-auto prose prose-zinc dark:prose-invert pb-24">
      <h1>{selectedArticle?.content_title}</h1>
      {contentList &&
        sortById(contentList).map(({ chunk, distance }) => {
          return (
            <span key={`article_chunk_${chunk.id}`}>{chunk.chunk_text}</span>
          );
        })}
    </div>
  );
}
