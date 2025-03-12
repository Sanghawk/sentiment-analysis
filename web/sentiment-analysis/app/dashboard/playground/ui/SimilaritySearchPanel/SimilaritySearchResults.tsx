"use client";

import { useSimilaritySearchContext } from "./SimilaritySearchProvider";
import { RoutingTableRow } from "./RoutingTableRow";
import { DateTimeConverter } from "@/ui/DateTimeConverter";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
export function SimilaritySearchResults() {
  const {
    data,
    loading,
    error,
    hasNextPage,
    nextPage,
    hasPreviousPage,
    prevPage,
    currentRange,
    totalResults,
  } = useSimilaritySearchContext();

  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="mt-3">
      <div className="border border-white/10">
        <div className="flex justify-end gap-x-3 p-3">
          {!data ? (
            <div />
          ) : (
            <>
              <div className="text-sm">
                {`${currentRange.start} - ${currentRange.end} of ${totalResults}`}
              </div>
              <div className="flex gap-x-3">
                <PrevPageButton
                  onClick={prevPage}
                  hasPreviousPage={hasPreviousPage}
                />
                <NextPageButton onClick={nextPage} hasNextPage={hasNextPage} />
              </div>
            </>
          )}
        </div>
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
              {loading ? (
                <tr className="col-span-3">
                  <td className="px-2 py-2 align-top font-mono text-xs/6 font-medium">
                    TODO: make this into skeleton - fetching results
                  </td>
                </tr>
              ) : data ? (
                data.items.map(({ article, distance }) => {
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
                })
              ) : (
                <tr className="col-span-3">
                  <td className="px-2 py-2 align-top font-mono text-xs/6 font-medium">
                    No results
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
/**
 * PrevPageButton disables the button if there is no previous page.
 */
function PrevPageButton({
  onClick,
  hasPreviousPage,
}: {
  onClick: () => void;
  hasPreviousPage: boolean;
}) {
  return (
    <ButtonComponent onClick={onClick} disabled={!hasPreviousPage}>
      <ChevronLeftIcon className="w-4 h-4 group-hover:text-base-300" />
    </ButtonComponent>
  );
}

/**
 * NextPageButton disables the button if there is no next page.
 */
function NextPageButton({
  onClick,
  hasNextPage,
}: {
  onClick: () => void;
  hasNextPage: boolean;
}) {
  return (
    <ButtonComponent onClick={onClick} disabled={!hasNextPage}>
      <ChevronRightIcon className="w-4 h-4 group-hover:text-base-300" />
    </ButtonComponent>
  );
}

/**
 * ButtonComponent applies styling based on whether the button is disabled.
 * - Uses `cursor-pointer` when enabled.
 * - On hover, the icon's color changes (via `group-hover:text-blue-500` on the icon).
 */
interface ButtonComponentProps {
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}

function ButtonComponent({
  onClick,
  disabled,
  children,
}: ButtonComponentProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded ${disabled ? "opacity-50" : "cursor-pointer group"}`}
    >
      {children}
    </button>
  );
}
