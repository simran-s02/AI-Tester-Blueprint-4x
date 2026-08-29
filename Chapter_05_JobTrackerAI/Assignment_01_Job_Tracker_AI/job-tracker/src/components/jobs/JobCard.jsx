import { useEffect, useRef, useState } from 'react'
import { useDraggable } from '@dnd-kit/core'
import {
  CalendarDays,
  ExternalLink,
  FileText,
  MoreHorizontal,
  Pencil,
  Trash2,
  StickyNote,
  Eye,
  X,
} from 'lucide-react'
import { getDaysSinceApplied } from '../../utils/dateUtils'

function JobCard({ job, onEdit, onDelete, onView }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] =
    useState(false)

  const menuRef = useRef(null)

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: job.id,
  })

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setIsMenuOpen(false)
      }
    }

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsMenuOpen(false)
        setIsDeleteConfirmOpen(false)
      }
    }

    document.addEventListener(
      'mousedown',
      handleClickOutside,
    )

    document.addEventListener(
      'keydown',
      handleEscape,
    )

    return () => {
      document.removeEventListener(
        'mousedown',
        handleClickOutside,
      )

      document.removeEventListener(
        'keydown',
        handleEscape,
      )
    }
  }, [])

  const daysSinceApplied = getDaysSinceApplied(
    job.dateApplied,
  )

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined

  const handleView = (event) => {
    event.preventDefault()
    event.stopPropagation()

    setIsMenuOpen(false)

    if (typeof onView === 'function') {
      onView(job)
    }
  }

  const handleEdit = (event) => {
    event.preventDefault()
    event.stopPropagation()

    setIsMenuOpen(false)

    if (typeof onEdit === 'function') {
      onEdit(job)
    }
  }

  const handleDeleteClick = (event) => {
    event.preventDefault()
    event.stopPropagation()

    setIsMenuOpen(false)
    setIsDeleteConfirmOpen(true)
  }

  const handleConfirmDelete = (event) => {
    event.preventDefault()
    event.stopPropagation()

    setIsDeleteConfirmOpen(false)

    if (typeof onDelete === 'function') {
      onDelete(job)
    } else {
      console.error('Delete handler is not connected')
    }
  }

  const handleCancelDelete = (event) => {
    event.preventDefault()
    event.stopPropagation()

    setIsDeleteConfirmOpen(false)
  }

  return (
    <>
      <article
        ref={setNodeRef}
        style={style}
        className={`group rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-950 ${
          isDragging ? 'opacity-50' : ''
        }`}
      >
        <div className="flex items-start justify-between gap-3">
          <div
            {...listeners}
            {...attributes}
            className="min-w-0 flex-1 cursor-grab active:cursor-grabbing"
          >
            <h3 className="truncate font-semibold text-slate-900 dark:text-white">
              {job.company}
            </h3>

            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {job.title}
            </p>
          </div>

          <div
            ref={menuRef}
            className="relative shrink-0"
          >
            <button
              type="button"
              onClick={(event) => {
                event.preventDefault()
                event.stopPropagation()

                setIsMenuOpen((current) => !current)
              }}
              className="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
              aria-label="Job actions"
              aria-expanded={isMenuOpen}
              aria-haspopup="menu"
            >
              <MoreHorizontal size={18} />
            </button>

            {isMenuOpen && (
              <div
                role="menu"
                className="absolute right-0 top-9 z-20 w-40 overflow-hidden rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900"
              >
                <button
                  type="button"
                  role="menuitem"
                  onClick={handleView}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  <Eye size={14} />
                  View details
                </button>

                <button
                  type="button"
                  role="menuitem"
                  onClick={handleEdit}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  <Pencil size={14} />
                  Edit job
                </button>

                <button
                  type="button"
                  role="menuitem"
                  onClick={handleDeleteClick}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30"
                >
                  <Trash2 size={14} />
                  Delete job
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 space-y-2">
          {job.resume && (
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <FileText
                size={14}
                className="shrink-0"
              />

              <span className="truncate rounded-md bg-slate-100 px-2 py-1 font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {job.resume}
              </span>
            </div>
          )}

          {job.salary && (
            <p className="text-xs font-medium text-slate-600 dark:text-slate-300">
              💰 {job.salary}
            </p>
          )}

          {job.dateApplied && (
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <CalendarDays size={14} />

              <span>
                Applied{' '}
                {daysSinceApplied === 0
                  ? 'today'
                  : `${daysSinceApplied} ${
                      daysSinceApplied === 1
                        ? 'day'
                        : 'days'
                    } ago`}
              </span>
            </div>
          )}

          {job.notes && (
            <div className="flex items-start gap-2 rounded-lg bg-slate-50 p-2.5 dark:bg-slate-900">
              <StickyNote
                size={14}
                className="mt-0.5 shrink-0 text-slate-400"
              />

              <p className="line-clamp-2 text-xs leading-5 text-slate-600 dark:text-slate-300">
                {job.notes}
              </p>
            </div>
          )}
        </div>

        <div className="mt-4 border-t border-slate-100 pt-3 dark:border-slate-800">
          {job.linkedinUrl ? (
            <a
              href={job.linkedinUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 transition hover:text-indigo-700 dark:text-indigo-400"
            >
              LinkedIn
              <ExternalLink size={13} />
            </a>
          ) : (
            <span className="text-xs text-slate-400">
              No LinkedIn link
            </span>
          )}
        </div>
      </article>

      {isDeleteConfirmOpen && (
        <div
          className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
          onClick={handleCancelDelete}
        >
          <div
            className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-900"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-500/10 dark:text-red-400">
                  <Trash2 size={18} />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Delete job?
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
                    Are you sure you want to delete{' '}
                    <span className="font-semibold text-slate-700 dark:text-slate-200">
                      {job.company}
                    </span>
                    ? This action cannot be undone.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={handleCancelDelete}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
                aria-label="Close delete confirmation"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={handleCancelDelete}
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleConfirmDelete}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700"
              >
                Delete job
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default JobCard