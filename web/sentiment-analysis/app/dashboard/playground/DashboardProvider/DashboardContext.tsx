"use client";

import { createContext, useContext, useReducer, ReactNode } from "react";
import {
  Article,
  ArticleChunkSearchResult,
  ArticleContentResponse,
  PaginatedArticleChunkSearchResults,
} from "@/types";

// Define the structure of the dashboard state
interface DashboardState {
  contentList: ArticleChunkSearchResult[]; // Holds the article content
  loading: boolean; // Tracks whether content is being loaded
  error: Error | null; // Stores any error encountered during fetching
  selectedArticle: Article | null; // Stores the currently selected article
  highlightedChunkId: number | null;
  scrollToChunkId: number | null;
}

// Extend the state interface to include actions
interface DashboardContextType extends DashboardState {
  selectArticle: (article: Article, query: string) => Promise<void>; // Function to select and load an article
  setHighlightedChunkId: (chunkId: number | null) => void;
  setScrollToChunkId: (chunkId: number | null) => void;
}

// Create a context with an undefined default value
const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined
);

// Define the initial state of the dashboard
const initialState: DashboardState = {
  contentList: [],
  loading: false,
  error: null,
  selectedArticle: null,
  highlightedChunkId: null,
  scrollToChunkId: null,
};

/**
 * Reducer function for managing state updates.
 * It merges the current state with new partial updates.
 */
function dashboardReducer(
  state: DashboardState,
  action: Partial<DashboardState>
) {
  return { ...state, ...action };
}

/**
 * Provides the dashboard context to child components.
 */
export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  /**
   * Fetches the article content from an API endpoint.
   * @param articleId - The ID of the article to fetch.
   * @returns The article content as a string.
   * @throws Error if the request fails.
   */

  async function DEPRECATED__fetchArticleContent(
    articleId: number
  ): Promise<string> {
    const response = await fetch(
      `http://localhost:8000/articles/${articleId}/s3`
    );
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    const result: ArticleContentResponse = await response.json();
    return result.text;
  }

  async function fetchArticleChunks(
    query: string,
    articleId: number,
    page: number = 1,
    pageSize = 100
  ): Promise<PaginatedArticleChunkSearchResults> {
    const response = await fetch(
      `http://localhost:8000/article_chunks/search_by_similarity?page=${page}&page_size=${pageSize}&q=${encodeURIComponent(
        query
      )}&article_id=${articleId}`
    );
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    const result: PaginatedArticleChunkSearchResults = await response.json();
    return result;
  }

  async function selectArticle(article: Article, query: string) {
    dispatch({ loading: true, error: null });
    try {
      const result = await fetchArticleChunks(query, article.id);

      dispatch({ contentList: result.items, selectedArticle: article });
    } catch (error) {
      dispatch({ error: error as Error, contentList: [] });
    } finally {
      dispatch({ loading: false });
    }
  }

  function setHighlightedChunkId(chunkId: number | null) {
    dispatch({ highlightedChunkId: chunkId });
  }

  function setScrollToChunkId(chunkId: number | null) {
    dispatch({ scrollToChunkId: chunkId });
  }

  return (
    <DashboardContext.Provider
      value={{
        ...state,
        selectArticle,
        setHighlightedChunkId,
        setScrollToChunkId,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

/**
 * Custom hook to access the dashboard context.
 * @returns The dashboard context.
 * @throws Error if used outside of a `DashboardProvider`.
 */
export function useDashboardContext(): DashboardContextType {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error(
      "useDashboardContext must be used within a DashboardProvider"
    );
  }
  return context;
}
