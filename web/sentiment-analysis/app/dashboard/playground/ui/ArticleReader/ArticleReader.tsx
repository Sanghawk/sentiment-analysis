"use client";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";
import { getBorderColorFromDistance } from "@/app/dashboard/playground/utils";
import { ArticleChunkSearchResult } from "@/types";
import { useEffect, useRef } from "react";
import Image from "next/image";
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
    loading,
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

  if (loading) return <LoadingScreen />;
  if (!selectedArticle) return <NoArticleFound />;
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

function LoadingScreen() {
  return (
    <div className="mx-auto prose prose-zinc dark:prose-invert">
      <div className="flex justify-center">
        <Image
          src="/assets/cat-typing.gif"
          alt="loading"
          width="200"
          height="200"
          unoptimized
        />
      </div>
    </div>
  );
}

function NoArticleFound() {
  return (
    <div className="mx-auto prose prose-zinc dark:prose-invert">
      <h1>Welcome to the News Reader!</h1>
      <p>Read the news based on the relevancy of your query.</p>
      <h4>Step 1. Enter a query</h4>
      <p>
        Like "What is Donald Trumps view on Bitcoin?" The search results will
        give you a list of articles sorted by relevancy.
      </p>
      <h4>Step 2. Select an article</h4>
      <p>
        Selecting an article will load the article into this view. You can hover
        over the text to get a deeper look into how related certain chunks of
        the article match your query.
      </p>
    </div>
  );
}
