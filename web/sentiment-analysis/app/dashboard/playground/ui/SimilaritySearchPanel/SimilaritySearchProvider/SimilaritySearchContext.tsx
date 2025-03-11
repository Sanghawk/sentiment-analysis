"use client";

import { createContext, useContext, useReducer, ReactNode } from "react";
import { ArticleSimilaritySearchResult } from "@/types";

// Define the state structure
interface SimilaritySearchState {
  data: ArticleSimilaritySearchResult | null;
  loading: boolean;
  error: Error | null;
}

// Define action types
type SimilaritySearchAction =
  | { type: "SEARCH_START" }
  | { type: "SEARCH_SUCCESS"; payload: ArticleSimilaritySearchResult }
  | { type: "SEARCH_ERROR"; payload: Error }
  | { type: "RESET" };

// Define the context type
interface SimilaritySearchContextType extends SimilaritySearchState {
  search: (query: string, page?: number, pageSize?: number) => Promise<void>;
}

// Create context
const SimilaritySearchContext = createContext<
  SimilaritySearchContextType | undefined
>(undefined);

// Define initial state
const initialState: SimilaritySearchState = {
  data: null,
  loading: false,
  error: null,
};

// Reducer function to handle state updates
function similaritySearchReducer(
  state: SimilaritySearchState,
  action: SimilaritySearchAction
): SimilaritySearchState {
  switch (action.type) {
    case "SEARCH_START":
      return { ...state, loading: true, error: null };
    case "SEARCH_SUCCESS":
      return { ...state, loading: false, data: action.payload };
    case "SEARCH_ERROR":
      return { ...state, loading: false, error: action.payload, data: null };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

/**
 * Provides similarity search context to child components.
 */
export function SimilaritySearchProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [state, dispatch] = useReducer(similaritySearchReducer, initialState);

  /**
   * Performs a similarity search query.
   * @param query - The search query string.
   * @param page - The page number (default: 1).
   * @param pageSize - The number of results per page (default: 10).
   */
  async function search(
    query: string,
    page: number = 1,
    pageSize: number = 10
  ) {
    dispatch({ type: "SEARCH_START" });

    try {
      const url = `http://localhost:8000/articles/search_by_similarity?page=${page}&page_size=${pageSize}&q=${encodeURIComponent(
        query
      )}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const result: ArticleSimilaritySearchResult = await response.json();
      dispatch({ type: "SEARCH_SUCCESS", payload: result });
    } catch (error) {
      dispatch({ type: "SEARCH_ERROR", payload: error as Error });
    }
  }

  return (
    <SimilaritySearchContext.Provider value={{ ...state, search }}>
      {children}
    </SimilaritySearchContext.Provider>
  );
}

/**
 * Custom hook to access the similarity search context.
 * @returns The similarity search context.
 * @throws Error if used outside of a `SimilaritySearchProvider`.
 */
export function useSimilaritySearchContext(): SimilaritySearchContextType {
  const context = useContext(SimilaritySearchContext);
  if (!context) {
    throw new Error(
      "useSimilaritySearchContext must be used within a SimilaritySearchProvider"
    );
  }
  return context;
}
