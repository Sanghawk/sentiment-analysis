"use client";

import { createContext, useContext, useReducer, ReactNode } from "react";
import { ArticleSimilaritySearchResult } from "@/types";

// Extend the state to store the current query as well as search results.
interface SimilaritySearchState {
  data: ArticleSimilaritySearchResult | null;
  loading: boolean;
  error: Error | null;
  currentQuery: string;
}

// Define actions for starting a search, handling success, errors, or resetting.
type SimilaritySearchAction =
  | { type: "SEARCH_START" }
  | {
      type: "SEARCH_SUCCESS";
      payload: { result: ArticleSimilaritySearchResult; query: string };
    }
  | { type: "SEARCH_ERROR"; payload: Error }
  | { type: "RESET" };

// Extend the context type to include pagination functions and computed values.
interface SimilaritySearchContextType extends SimilaritySearchState {
  search: (query: string, page?: number, pageSize?: number) => Promise<void>;
  nextPage: () => Promise<void>;
  prevPage: () => Promise<void>;
  currentPage: number;
  pageSize: number;
  totalResults: number;
  currentRange: { start: number; end: number };
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

// Create the context.
const SimilaritySearchContext = createContext<
  SimilaritySearchContextType | undefined
>(undefined);

// Initial state includes no data and an empty query.
const initialState: SimilaritySearchState = {
  data: null,
  loading: false,
  error: null,
  currentQuery: "",
};

/**
 * Reducer function to update the state based on action types.
 * SEARCH_SUCCESS now also updates the current query.
 */
function similaritySearchReducer(
  state: SimilaritySearchState,
  action: SimilaritySearchAction
): SimilaritySearchState {
  switch (action.type) {
    case "SEARCH_START":
      return { ...state, loading: true, error: null };
    case "SEARCH_SUCCESS":
      return {
        ...state,
        loading: false,
        data: action.payload.result,
        currentQuery: action.payload.query,
      };
    case "SEARCH_ERROR":
      return { ...state, loading: false, error: action.payload, data: null };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

/**
 * Provides similarity search context with pagination functionality to child components.
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
      dispatch({ type: "SEARCH_SUCCESS", payload: { result, query } });
    } catch (error) {
      dispatch({ type: "SEARCH_ERROR", payload: error as Error });
    }
  }

  /**
   * Moves to the next page if one exists.
   */
  async function nextPage() {
    if (
      state.data &&
      state.data.page * state.data.page_size < state.data.total
    ) {
      const next = state.data.page + 1;
      await search(state.currentQuery, next, state.data.page_size);
    }
  }

  /**
   * Moves to the previous page if one exists.
   */
  async function prevPage() {
    if (state.data && state.data.page > 1) {
      const prev = state.data.page - 1;
      await search(state.currentQuery, prev, state.data.page_size);
    }
  }

  // Compute pagination values based on the current data.
  const currentPage = state.data ? state.data.page : 0;
  const pageSize = state.data ? state.data.page_size : 10;
  const totalResults = state.data ? state.data.total : 0;
  const currentRange = state.data
    ? {
        start: (state.data.page - 1) * state.data.page_size + 1,
        end: Math.min(state.data.page * state.data.page_size, state.data.total),
      }
    : { start: 0, end: 0 };
  const hasNextPage = state.data
    ? state.data.page * state.data.page_size < state.data.total
    : false;
  const hasPreviousPage = state.data ? state.data.page > 1 : false;

  return (
    <SimilaritySearchContext.Provider
      value={{
        ...state,
        search,
        nextPage,
        prevPage,
        currentPage,
        pageSize,
        totalResults,
        currentRange,
        hasNextPage,
        hasPreviousPage,
      }}
    >
      {children}
    </SimilaritySearchContext.Provider>
  );
}

/**
 * Custom hook to access the similarity search context with pagination.
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
