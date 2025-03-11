"use client";

import { useSimilaritySearchContext } from "./SimilaritySearchProvider/SimilaritySearchContext";
import { RoutingTableRow } from "./RoutingTableRow";
import { DateTimeConverter } from "@/ui/DateTimeConverter";
export function SimilaritySearchResults() {
  const { data, loading, error } = useSimilaritySearchContext();

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  if (!data) return <p>No results yet.</p>;

  return (
    <div className="">
      <div className="">
        <div></div>
        <div className="w-full overflow-x-auto whitespace-nowrap font-mono">
          <table className="grid grid-cols-[auto_auto_auto] w-full">
            <thead className="col-span-3 grid grid-cols-subgrid">
              <tr className="col-span-3 grid grid-cols-subgrid">
                <th className="px-2 py-2.5 text-left text-sm/7 font-semibold text-base-950 dark:text-base-200">
                  {" "}
                  Cosine
                </th>
                <th className="px-2 py-2.5 text-left text-sm/7 font-semibold text-base-950 dark:text-base-200">
                  {" "}
                  Title
                </th>

                <th className="px-2 py-2.5 text-left text-sm/7 font-semibold text-base-950 dark:text-base-200">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="col-span-3 grid grid-cols-subgrid border-t border-base-900/10 dark:border-base-200/10">
              {data.items.map(({ article, distance }) => {
                return (
                  <RoutingTableRow
                    key={`article_result_${article.id}`}
                    className="col-span-3 grid grid-cols-subgrid not-last:border-b not-last:border-gray-950/5 dark:not-last:border-white/5"
                    data={article}
                  >
                    <td className="px-2 py-2 align-top font-mono text-xs/6 font-medium">
                      {Math.round(distance * 1000) / 1000}
                    </td>

                    <td className="truncate max-w-xs px-2 py-2 align-top font-mono text-xs/6 font-medium">
                      {article.content_title}
                    </td>
                    <td className="px-2 py-2 align-top font-mono text-xs/6 font-medium">
                      <DateTimeConverter
                        dateTime={article.publish_datetime}
                        formatStr="MMM d, yyyy"
                      />
                    </td>
                  </RoutingTableRow>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
