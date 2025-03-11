"use client";

import { createContext, useContext, useReducer, ReactNode } from "react";
import { Article, ArticleContentResponse } from "@/types";

// Define the structure of the dashboard state
interface DashboardState {
  content: string; // Holds the article content
  loading: boolean; // Tracks whether content is being loaded
  error: Error | null; // Stores any error encountered during fetching
  selectedArticle: Article | null; // Stores the currently selected article
}

// Extend the state interface to include actions
interface DashboardContextType extends DashboardState {
  selectArticle: (article: Article) => Promise<void>; // Function to select and load an article
}

// Create a context with an undefined default value
const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined
);

// Define the initial state of the dashboard
const initialState: DashboardState = {
  content: "",
  loading: false,
  error: null,
  selectedArticle: null,
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
  async function fetchArticleContent(articleId: number): Promise<string> {
    const response = await fetch(
      `http://localhost:8000/articles/${articleId}/s3`
    );
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    const result: ArticleContentResponse = await response.json();
    return result.text;
  }

  /**
   * Selects an article, fetches its content, and updates the state.
   * @param article - The article to select.
   */
  async function selectArticle(article: Article) {
    dispatch({ loading: true, error: null });
    try {
      const content = await fetchArticleContent(article.id);
      dispatch({ content, selectedArticle: article });
    } catch (error) {
      dispatch({ error: error as Error, content: "" });
    } finally {
      dispatch({ loading: false });
    }
  }

  return (
    <DashboardContext.Provider value={{ ...state, selectArticle }}>
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
