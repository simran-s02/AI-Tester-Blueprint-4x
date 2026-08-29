import { Search, SlidersHorizontal, X } from 'lucide-react'
import { JOB_STATUSES } from '../../data/statuses'

function SearchBar({
  search,
  onSearch,
  statusFilter,
  onStatusFilter,
  dateFilter,
  onDateFilter,
  sortBy,
  onSortBy,
  onClearFilters,
  resultCount,
}) {
  const hasFilters =
    search ||
    statusFilter !== 'all' ||
    dateFilter !== 'all' ||
    sortBy !== 'newest'

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            type="search"
            value={search}
            onChange={(event) =>
              onSearch(event.target.value)
            }
            placeholder="Search by company or role..."
            className="h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-800 dark:bg-slate-900 dark:text-white"
          />
        </div>

        <div className="relative">
          <SlidersHorizontal
            size={17}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <select
            value={statusFilter}
            onChange={(event) =>
              onStatusFilter(event.target.value)
            }
            className="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-white pl-10 pr-9 text-sm font-medium text-slate-700 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 lg:w-48 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="all">
              All statuses
            </option>

            {JOB_STATUSES.map((status) => (
              <option
                key={status.id}
                value={status.id}
              >
                {status.label}
              </option>
            ))}
          </select>
        </div>

        <div className="relative">
          <select
            value={dateFilter}
            onChange={(event) =>
              onDateFilter(event.target.value)
            }
            className="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-white px-4 pr-9 text-sm font-medium text-slate-700 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 lg:w-44 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="all">
              All time
            </option>

            <option value="today">
              Today
            </option>

            <option value="7days">
              Last 7 days
            </option>

            <option value="30days">
              Last 30 days
            </option>
          </select>
        </div>

        <div className="relative">
          <select
            value={sortBy}
            onChange={(event) =>
              onSortBy(event.target.value)
            }
            className="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-white px-4 pr-9 text-sm font-medium text-slate-700 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 lg:w-48 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="newest">
              Newest first
            </option>

            <option value="oldest">
              Oldest first
            </option>

            <option value="companyAsc">
              Company A–Z
            </option>

            <option value="companyDesc">
              Company Z–A
            </option>
          </select>
        </div>

        {hasFilters && (
          <button
            type="button"
            onClick={onClearFilters}
            className="flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <X size={16} />
            Clear
          </button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <span>
          <span className="font-semibold text-slate-700 dark:text-slate-200">
            {resultCount}
          </span>{' '}
          {resultCount === 1 ? 'job' : 'jobs'} found
        </span>

        {(statusFilter !== 'all' ||
          dateFilter !== 'all') && (
          <>
            <span>·</span>

            <span>
              Filters:{' '}

              {statusFilter !== 'all' && (
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {
                    JOB_STATUSES.find(
                      (status) =>
                        status.id === statusFilter,
                    )?.label
                  }
                </span>
              )}

              {statusFilter !== 'all' &&
                dateFilter !== 'all' && (
                  <span> · </span>
                )}

              {dateFilter !== 'all' && (
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {dateFilter === 'today'
                    ? 'Today'
                    : dateFilter === '7days'
                      ? 'Last 7 days'
                      : 'Last 30 days'}
                </span>
              )}
            </span>
          </>
        )}
      </div>
    </div>
  )
}

export default SearchBar