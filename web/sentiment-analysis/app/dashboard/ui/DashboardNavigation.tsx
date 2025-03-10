export default function DashboardNavigation() {
  return (
    <div className="fixed inset-x-0 top-0 border-b border-base-950/5 dark:border-base-200/10">
      <div className="bg-base-200 dark:bg-base-950">
        <div className="flex h-14 items-center justify-between gap-8 px-4 sm:px-6">
          {/* left */}
          <div className="flex items-center gap-4">
            <div className="shrink-0">
              <div className="h-5 font-extrabold text-base-950 dark:text-base-200">
                Canary
              </div>
            </div>
          </div>
          {/* right */}
          <div className="flex items-center gap-6">
            <div className="text-sm/6 text-base-950 dark:text-base-200">
              ???
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
