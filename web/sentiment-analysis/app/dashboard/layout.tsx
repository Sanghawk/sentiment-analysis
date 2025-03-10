import type { Metadata } from "next";

// Local UI components
import DashboardNavigation from "./ui/DashboardNavigation";
import DashboardSidebarNavigation from "./ui/DashboardSidebarNavigation";

export const metadata: Metadata = {
  title: "JAT - Dashboard",
  description: "Just Another Tool",
};

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="isolate">
      <DashboardNavigation />
      <div className="grid grid-cols-[var(--container-2xs)_2.5rem_minmax(0,1fr)_2.5rem] min-h-dvh pt-14.25 ">
        <div className="col-start-1 row-span-full row-start-1 relative ">
          <div className="absolute inset-0">
            <div className="sticky top-14.25 bottom-0 left-0 h-full max-h-[calc(100dvh-(var(--spacing)*14.25))] w-2xs overflow-y-auto p-6">
              <div>
                <DashboardSidebarNavigation />
              </div>
            </div>
          </div>
        </div>
        <div className="col-start-2 row-span-full row-start-1"></div>
        <div className="col-start-3 row-span-full row-start-1 relative">
          {children}
        </div>
        <div className="col-start-4 row-span-full row-start-1"></div>
      </div>
    </div>
  );
}
