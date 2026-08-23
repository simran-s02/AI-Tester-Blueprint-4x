import { useDroppable } from '@dnd-kit/core'
import JobCard from './JobCard'

function KanbanColumn({
  status,
  jobs = [],
  onEditJob,
  onDeleteJob,
  onViewJob,
}) {
  const { setNodeRef, isOver } = useDroppable({
    id: status.id,
  })

  return (
    <section
      ref={setNodeRef}
      className={`flex min-h-[500px] min-w-[280px] flex-1 flex-col rounded-2xl border transition ${
        isOver
          ? 'border-indigo-400 bg-indigo-50/70 dark:border-indigo-500 dark:bg-indigo-950/30'
          : 'border-slate-200 bg-slate-50/80 dark:border-slate-800 dark:bg-slate-900/50'
      }`}
    >
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
            {status.label}
          </h2>

          <p className="mt-0.5 text-xs text-slate-500">
            {status.description}
          </p>
        </div>

        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
          {jobs.length}
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-3">
        {jobs.length === 0 ? (
          <div className="flex min-h-32 items-center justify-center rounded-xl border border-dashed border-slate-300 text-xs text-slate-400 dark:border-slate-700">
            No jobs here yet
          </div>
        ) : (
          jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onEdit={onEditJob}
              onDelete={onDeleteJob}
              onView={onViewJob}
            />
          ))
        )}
      </div>
    </section>
  )
}

export default KanbanColumn