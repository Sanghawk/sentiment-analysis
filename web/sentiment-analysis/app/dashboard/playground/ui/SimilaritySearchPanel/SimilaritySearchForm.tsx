"use client";

import { useState, FormEvent, ChangeEvent, KeyboardEvent } from "react";
import { useSimilaritySearchContext } from "./SimilaritySearchProvider";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
/**
 * Form component for performing similarity search queries.
 */
export function SimilaritySearchForm() {
  const [query, setQuery] = useState("");
  const { search } = useSimilaritySearchContext();

  /**
   * Handles input value changes.
   * @param event - The input change event.
   */
  function handleInputChange(event: ChangeEvent<HTMLTextAreaElement>) {
    setQuery(event.target.value);
  }

  /**
   * Handles form submission.
   * @param event - The form submission event.
   */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (query.trim()) {
      await search(query);
    }
  }

  /**
   * Handles keyboard events.
   * - Clears query on `Escape`
   * - Triggers search on `Enter`
   * @param event - The keyboard event.
   */
  async function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Escape") {
      setQuery("");
    } else if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (query.trim()) {
        await search(query);
      }
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="relative flex flex-col w-full max-w-2xl mx-auto p-4 border border-white/10 rounded">
        <div className="max-h-32 overflow-y-auto">
          <textarea
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything"
            aria-label="Search"
            className="w-full resize-none border-none focus:outline-none"
            rows={3}
          />
        </div>

        <div className="flex justify-end">
          {/* Submit button pinned at the bottom-left */}
          <button
            type="submit"
            className="cursor-pointer bg-indigo-600 text-white px-6 py-1.5 rounded-full hover:bg-indigo-600/70 transition duration-150 font-semibold"
          >
            {/* <MagnifyingGlassIcon className="size-4" /> */}
            Search
          </button>
        </div>
      </div>
    </form>
  );
}
