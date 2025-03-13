"use client";

// Local imports
import { DashboardProvider } from "./DashboardProvider";
import {
  SimilaritySearchProvider,
  SimilaritySearchForm,
  SimilaritySearchResults,
  ArticleReader,
  ArticleInspector,
} from "./ui";

export default function DashboardPlaygroundPage() {
  return (
    <DashboardProvider>
      <div className="overflow-auto h-[calc(100dvh-(var(--spacing)*14.25))]">
        <div></div>
        <div className="grid grid-cols-1 2xl:grid-cols-[35rem_minmax(41rem,1fr)_35rem] gap-3">
          <div className="2xl:col-start-1">
            <div className="grid  grid-rows-[2.5rem_auto_2.5rem]">
              <div className="row-start-1"></div>
              <div className="row-start-2  max-h-[calc(100dvh-(var(--spacing)*14.25)-5rem)] overflow-auto">
                <div className="mx-auto prose prose-zinc dark:prose-invert">
                  <SimilaritySearchProvider>
                    <SimilaritySearchForm />
                    <SimilaritySearchResults />
                  </SimilaritySearchProvider>
                </div>
              </div>
              <div className="row-start-3"></div>
            </div>
          </div>
          <div className="2xl:col-start-2">
            <div className="grid grid-rows-[2.5rem_auto_2.5rem]">
              <div className="row-start-1 w-full text-center"></div>
              <div className="row-start-2 max-h-[calc(100dvh-(var(--spacing)*14.25)-5rem)] overflow-auto">
                <ArticleReader />
              </div>
              <div className="row-start-3"></div>
            </div>
          </div>
          <div className="2xl:col-start-3">
            <div className="grid grid-rows-[2.5rem_auto_2.5rem]">
              <div className="row-start-1"></div>
              <div className="row-start-2 max-h-[calc(100dvh-(var(--spacing)*14.25)-5rem)] overflow-auto">
                <div className="mx-auto prose prose-zinc dark:prose-invert">
                  <ArticleInspector />
                </div>
              </div>
              <div className="row-start-3"></div>
            </div>
          </div>
        </div>
      </div>
    </DashboardProvider>
  );
}
