import { useState } from 'react'
import Header from './components/Header'
import DashboardStats from './components/DashboardStats'
import SearchBar from './components/SearchBar'
import KanbanBoard from './components/KanbanBoard'
import { useJobs } from './hooks/useJobs'
import JobModal from './components/JobModal'
import { ExternalLink, X } from 'lucide-react'

function App() {
  const [isJobModalOpen, setIsJobModalOpen] = useState(false)
  const [editingJob, setEditingJob] = useState(null)
  const [jobToDelete, setJobToDelete] = useState(null)
  const [selectedJob, setSelectedJob] = useState(null)

  const {
    jobs,
    createJob,
    editJob,
    removeJob,
  } = useJobs()

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [dateFilter, setDateFilter] = useState('all')
  const [darkMode, setDarkMode] = useState(false)

  const filteredJobs = jobs.filter((job) => {
    const query = search.toLowerCase().trim()

    const matchesSearch =
      !query ||
      job.company.toLowerCase().includes(query) ||
      job.title.toLowerCase().includes(query)

    const matchesStatus =
      statusFilter === 'all' ||
      job.status === statusFilter

    let matchesDate = true

    if (dateFilter !== 'all' && job.dateApplied) {
      const appliedDate = new Date(job.dateApplied)
      const today = new Date()

      appliedDate.setHours(0, 0, 0, 0)
      today.setHours(0, 0, 0, 0)

      const difference =
        today.getTime() - appliedDate.getTime()

      const daysAgo = Math.floor(
        difference / (1000 * 60 * 60 * 24),
      )

      if (dateFilter === 'today') {
        matchesDate = daysAgo === 0
      }

      if (dateFilter === '7days') {
        matchesDate = daysAgo >= 0 && daysAgo <= 7
      }

      if (dateFilter === '30days') {
        matchesDate = daysAgo >= 0 && daysAgo <= 30
      }
    }

    return (
      matchesSearch &&
      matchesStatus &&
      matchesDate
    )
  })

  const handleAddJob = () => {
    setEditingJob(null)
    setIsJobModalOpen(true)
  }

  const handleEditJob = (job) => {
    setEditingJob(job)
    setIsJobModalOpen(true)
  }

  const handleViewJob = (job) => {
    setSelectedJob(job)
  }

  const handleSaveJob = async (job) => {
    if (editingJob) {
      await editJob(job)
    } else {
      await createJob(job)
    }

    setIsJobModalOpen(false)
    setEditingJob(null)
  }

  const handleMoveJob = async (job) => {
    await editJob(job)
  }

  const handleDeleteJob = (job) => {
    setJobToDelete(job)
  }

  const handleConfirmDelete = async () => {
    if (!jobToDelete) {
      return
    }

    try {
      await removeJob(jobToDelete.id)
      setJobToDelete(null)

      if (selectedJob?.id === jobToDelete.id) {
        setSelectedJob(null)
      }
    } catch (error) {
      console.error(
        'Failed to delete job:',
        error,
      )
    }
  }

  const handleCancelDelete = () => {
    setJobToDelete(null)
  }

  const handleClearFilters = () => {
    setSearch('')
    setStatusFilter('all')
    setDateFilter('all')
  }

  const toggleDarkMode = () => {
    setDarkMode((current) => !current)
  }

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-100 text-slate-900 transition-colors dark:bg-slate-950 dark:text-white">
        <Header
          darkMode={darkMode}
          onToggleDarkMode={toggleDarkMode}
          onAddJob={handleAddJob}
        />

        <main className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6">
          <div className="space-y-6">
            <section>
              <div>
                <p className="text-sm font-medium text-indigo-600">
                  Career Command Center
                </p>

                <h2 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">
                  Your job search, organized.
                </h2>

                <p className="mt-2 max-w-2xl text-sm text-slate-500 dark:text-slate-400">
                  Track applications, manage interviews,
                  and make smarter career decisions from
                  one place.
                </p>
              </div>
            </section>

            <DashboardStats jobs={jobs} />

            <SearchBar
              search={search}
              onSearch={setSearch}
              statusFilter={statusFilter}
              onStatusFilter={setStatusFilter}
              dateFilter={dateFilter}
              onDateFilter={setDateFilter}
              onClearFilters={handleClearFilters}
              resultCount={filteredJobs.length}
            />

            <KanbanBoard
              jobs={filteredJobs}
              onEditJob={handleEditJob}
              onDeleteJob={handleDeleteJob}
              onViewJob={handleViewJob}
              onMoveJob={handleMoveJob}
            />
          </div>
        </main>

        <JobModal
          isOpen={isJobModalOpen}
          onClose={() => {
            setIsJobModalOpen(false)
            setEditingJob(null)
          }}
          onSave={handleSaveJob}
          job={editingJob}
        />

        {selectedJob && (
          <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
            onClick={() => setSelectedJob(null)}
          >
            <div
              className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-900"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-indigo-600">
                    Job Details
                  </p>

                  <h2 className="mt-1 text-xl font-bold text-slate-900 dark:text-white">
                    {selectedJob.company}
                  </h2>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {selectedJob.title}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setSelectedJob(null)}
                  className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
                  aria-label="Close details"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="mt-6 space-y-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Status
                  </p>

                  <p className="mt-1 text-sm font-medium text-slate-700 dark:text-slate-200">
                    {selectedJob.status || 'Not specified'}
                  </p>
                </div>

                {selectedJob.salary && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Salary
                    </p>

                    <p className="mt-1 text-sm text-slate-700 dark:text-slate-200">
                      {selectedJob.salary}
                    </p>
                  </div>
                )}

                {selectedJob.dateApplied && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Date Applied
                    </p>

                    <p className="mt-1 text-sm text-slate-700 dark:text-slate-200">
                      {selectedJob.dateApplied}
                    </p>
                  </div>
                )}

                {selectedJob.resume && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Resume
                    </p>

                    <p className="mt-1 text-sm text-slate-700 dark:text-slate-200">
                      {selectedJob.resume}
                    </p>
                  </div>
                )}

                {selectedJob.notes && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Notes
                    </p>

                    <p className="mt-1 rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                      {selectedJob.notes}
                    </p>
                  </div>
                )}

                {selectedJob.linkedinUrl && (
                  <div className="border-t border-slate-100 pt-4 dark:border-slate-800">
                    <a
                      href={selectedJob.linkedinUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                    >
                      Open LinkedIn
                      <ExternalLink size={15} />
                    </a>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  type="button"
                  onClick={() => setSelectedJob(null)}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {jobToDelete && (
          <div className="fixed inset-0 z-[110] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-500/10 dark:text-red-400">
                  ⚠️
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Delete job?
                  </h2>

                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    Are you sure you want to delete{' '}
                    <span className="font-semibold text-slate-700 dark:text-slate-200">
                      {jobToDelete.company}
                    </span>
                    ? This action cannot be undone.
                  </p>
                </div>
              </div>

              <div className="mt-5 flex justify-end gap-3">
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
      </div>
    </div>
  )
}

export default App