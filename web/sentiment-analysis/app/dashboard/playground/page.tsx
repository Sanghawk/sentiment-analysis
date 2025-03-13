"use client";

// import { ArrowRightStartOnRectangleIcon } from "@heroicons/react/24/outline";
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
      <div>
        <div></div>
        <div className="grid grid-cols-[35rem_minmax(0,1fr)_35rem] ">
          <div className="col-start-1">
            <div className=" grid grid-cols-1 grid-rows-[2.5rem_auto] gap-3">
              <div className="row-start-1">{/* <ToggleButton /> */}</div>

              <div className="row-start-2">
                <SimilaritySearchProvider>
                  <SimilaritySearchForm />
                  <SimilaritySearchResults />
                </SimilaritySearchProvider>
              </div>
            </div>
          </div>
          <div className="col-start-2 ">
            <div className="grid grid-rows-[2.5rem_auto_2.5rem]">
              <div className="row-start-1 w-full text-center"></div>
              <div className="row-start-2 max-h-[calc(100dvh-(var(--spacing)*14.25)-5rem)] overflow-auto">
                <ArticleReader />
              </div>
              <div className="row-start-3"></div>
            </div>
          </div>
          <div className="col-start-3">
            <div className="grid grid-rows-[2.5rem_auto]">
              <div className="row-start-1"></div>
              <div className="row-start-2 max-h-[calc(100dvh-(var(--spacing)*14.25)-5rem)] overflow-auto">
                <ArticleInspector />
              </div>
              <div className="row-start-3"></div>
            </div>
          </div>
        </div>
      </div>
    </DashboardProvider>
  );
}

// function ToggleButton() {
//   return (
//     <button className="rounded-md bg-rose-500/50 px-4 py-2 text-sm">
//       <ArrowRightStartOnRectangleIcon className="size-4" />
//     </button>
//   );
// }
