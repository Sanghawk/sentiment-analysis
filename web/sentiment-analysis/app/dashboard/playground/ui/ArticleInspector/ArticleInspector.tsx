// ArticleInspector.tsx
"use client";
import { useDashboardContext } from "@/app/dashboard/playground/DashboardProvider";
import { getUnderlineColorFromDistance } from "@/app/dashboard/playground/utils";
import Image from "next/image";
export function ArticleInspector() {
  const {
    loading,
    error,
    contentList,
    highlightedChunkId,
    setHighlightedChunkId,
    setScrollToChunkId,
  } = useDashboardContext();

  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="">
      <div className="border border-white/10">
        <div className="w-full overflow-x-auto whitespace-nowrap">
          <table className="grid grid-cols-[auto_auto] w-full">
            <thead className="col-span-2 grid grid-cols-subgrid">
              <tr className="col-span-2 grid grid-cols-subgrid">
                <th className="px-2 text-left text-sm/7 font-semibold text-base-950 dark:text-base-200">
                  Cosine
                </th>
                <th className="px-2  text-left text-sm/7 font-semibold text-base-950 dark:text-base-200">
                  Chunk
                </th>
              </tr>
            </thead>
            <tbody className="col-span-2 grid grid-cols-subgrid border-base-900/10 dark:border-base-200/10">
              {loading ? (
                <tr className="col-span-3">
                  <td className="flex justify-center">
                    <Image
                      src="/assets/cat-typing.gif"
                      alt="loading"
                      width="200"
                      height="200"
                      unoptimized
                    />
                  </td>
                </tr>
              ) : contentList ? (
                contentList.map(({ chunk, distance }) => (
                  <tr
                    key={`article_result_${chunk.id}`}
                    className={`col-span-2 grid grid-cols-subgrid not-last:border-b not-last:border-gray-950/5 dark:not-last:border-white/5 cursor-pointer ${getUnderlineColorFromDistance(
                      distance
                    )} ${highlightedChunkId === chunk.id ? "underline" : ""}`}
                    onMouseEnter={() => {
                      setHighlightedChunkId(chunk.id);
                    }}
                    onMouseLeave={() => setHighlightedChunkId(null)}
                    onClick={() => {
                      setScrollToChunkId(chunk.id);
                    }}
                  >
                    <td className="px-2 py-2 align-top font-mono text-xs/6">
                      {Math.round(distance * 1000) / 1000}
                    </td>
                    <td className="truncate max-w-xs px-2 py-2 align-top font-mono text-xs/6">
                      {chunk.chunk_text}
                    </td>
                  </tr>
                ))
              ) : (
                <tr className="col-span-3">
                  <td className="col-span-3 px-2 py-2 align-top font-mono text-xs/6 font-medium text-center w-full">
                    n/a
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
