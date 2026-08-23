import {
  DndContext,
  closestCenter,
} from '@dnd-kit/core'
import {
  BriefcaseBusiness,
  Search,
} from 'lucide-react'

import { JOB_STATUSES } from '../data/statuses'
import KanbanColumn from './KanbanColumn'

function KanbanBoard({
  jobs,
  onEditJob,
  onDeleteJob,
  onViewJob,
  onMoveJob,
  hasFilters,
  onClearFilters,
  onAddJob,
}) {
  const handleDragEnd = (event) => {
    const { active, over } = event

    if (!over) {
      return
    }

    const jobId = active.id
    const newStatus = over.id

    const job = jobs.find(
      (currentJob) => currentJob.id === jobId,
    )

    if (!job) {
      return
    }

    if (job.status === newStatus) {
      return
    }

    onMoveJob({
      ...job,
      status: newStatus,
    })
  }

  if (jobs.length === 0) {
    return (
      <div className="flex min-h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 text-center dark:border-slate-700 dark:bg-slate-900/50">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400 dark:bg-slate-800">
          {hasFilters ? (
            <Search size={22} />
          ) : (
            <BriefcaseBusiness size={22} />
          )}
        </div>

        <h2 className="mt-4 text-base font-semibold text-slate-900 dark:text-white">
          {hasFilters
            ? 'No jobs match your filters'
            : 'No jobs yet'}
        </h2>

        <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
          {hasFilters
            ? 'Try changing your search or filters to find matching jobs.'
            : 'Start building your job tracker by adding your first job.'}
        </p>

        {hasFilters ? (
          <button
            type="button"
            onClick={onClearFilters}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            Clear filters
          </button>
        ) : (
          <button
            type="button"
            onClick={onAddJob}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            Add your first job
          </button>
        )}
      </div>
    )
  }

  return (
    <DndContext
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {JOB_STATUSES.map((status) => {
          const statusJobs = jobs.filter(
            (job) => job.status === status.id,
          )

          return (
            <KanbanColumn
              key={status.id}
              status={status}
              jobs={statusJobs}
              onEditJob={onEditJob}
              onDeleteJob={onDeleteJob}
              onViewJob={onViewJob}
            />
          )
        })}
      </div>
    </DndContext>
  )
}

export default KanbanBoard