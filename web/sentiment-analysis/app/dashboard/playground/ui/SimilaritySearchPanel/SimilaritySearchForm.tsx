"use client";

import { useState, FormEvent, ChangeEvent, KeyboardEvent } from "react";
import { useSimilaritySearchContext } from "./SimilaritySearchProvider";

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
  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    setQuery(event.target.value);
  }

  /**
   * Handles form submission.
   * @param event - The form submission event.
   */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await search(query);
  }

  /**
   * Handles keyboard events.
   * - Clears query on `Escape`
   * - Triggers search on `Enter`
   * @param event - The keyboard event.
   */
  async function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setQuery("");
    } else if (event.key === "Enter") {
      event.preventDefault();
      await search(query);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="search"
        value={query}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Search..."
        aria-label="Search"
      />
      <button type="submit">Search</button>
    </form>
  );
}
