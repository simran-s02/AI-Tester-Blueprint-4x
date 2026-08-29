import { CalendarClock, ArrowRight } from 'lucide-react'
import { getDaysSinceApplied } from '../../utils/dateUtils'

function FollowUpAlerts({ jobs = [], onFollowUp }) {
  const followUpJobs = jobs.filter((job) => {
    if (job.status !== 'applied' || !job.dateApplied) {
      return false
    }

    return getDaysSinceApplied(job.dateApplied) >= 7
  })

  if (followUpJobs.length === 0) {
    return null
  }

  return (
    <section className="rounded-2xl border border-amber-200 bg-amber-50/70 p-4 dark:border-amber-900/50 dark:bg-amber-950/20">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-400">
          <CalendarClock size={18} />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-amber-900 dark:text-amber-300">
            Follow-up recommended
          </h3>

          <p className="mt-1 text-xs text-amber-700 dark:text-amber-400">
            These applications have been waiting for 7 or more
            days.
          </p>

          <div className="mt-3 space-y-2">
            {followUpJobs.map((job) => {
              const days = getDaysSinceApplied(
                job.dateApplied,
              )

              return (
                <div
                  key={job.id}
                  className="flex flex-col gap-3 rounded-xl border border-amber-200 bg-white p-3 sm:flex-row sm:items-center sm:justify-between dark:border-amber-900/50 dark:bg-slate-900"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">
                      {job.company}
                    </p>

                    <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                      {job.title}
                    </p>

                    <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                      Applied {days} days ago
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => onFollowUp?.(job)}
                    className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-lg bg-amber-500 px-3 py-2 text-xs font-semibold text-white transition hover:bg-amber-600"
                  >
                    Follow up
                    <ArrowRight size={14} />
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

export default FollowUpAlerts