"use client";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";
import { getBorderColorFromDistance } from "@/app/dashboard/playground/utils";
import { ArticleChunkSearchResult } from "@/types";
import { useEffect, useRef } from "react";

function sortById(
  contentList: ArticleChunkSearchResult[]
): ArticleChunkSearchResult[] {
  return contentList.slice().sort((a, b) => a.chunk.id - b.chunk.id);
}

export function ArticleReader() {
  const {
    contentList,
    selectedArticle,
    highlightedChunkId,
    scrollToChunkId,
    setHighlightedChunkId,
  } = useDashboardContext();

  // Ensure refs are correctly managed
  const chunkRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});

  useEffect(() => {
    if (scrollToChunkId && chunkRefs.current[scrollToChunkId]) {
      chunkRefs.current[scrollToChunkId]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [scrollToChunkId]);

  return (
    <div className="mx-auto prose prose-zinc dark:prose-invert pb-24">
      <h1>{selectedArticle?.content_title}</h1>
      <div className="transition">
        {contentList &&
          sortById(contentList).map(({ chunk, distance }) => (
            <div
              key={`article_chunk_${chunk.id}`}
              ref={(el) => {
                if (el) chunkRefs.current[chunk.id] = el;
              }}
              className={`cursor-pointer ${getBorderColorFromDistance(
                distance
              )} ${highlightedChunkId === chunk.id ? "border-l pl-2" : ""}`}
              onMouseEnter={() => setHighlightedChunkId(chunk.id)}
              onMouseLeave={() => setHighlightedChunkId(null)}
            >
              <p>{chunk.chunk_text}</p>
            </div>
          ))}
      </div>
    </div>
  );
}
