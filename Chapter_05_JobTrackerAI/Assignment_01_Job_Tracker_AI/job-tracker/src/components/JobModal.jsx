import { useEffect, useState } from 'react'
import { X, BriefcaseBusiness } from 'lucide-react'
import { JOB_STATUSES } from '../data/statuses'

const initialForm = {
  company: '',
  title: '',
  linkedinUrl: '',
  resume: '',
  dateApplied: new Date().toISOString().split('T')[0],
  salary: '',
  notes: '',
  status: 'wishlist',
}

function JobModal({ isOpen, onClose, onSave, job }) {
  const [form, setForm] = useState(initialForm)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (!isOpen) {
      return
    }

    if (job) {
      setForm({
        company: job.company || '',
        title: job.title || '',
        linkedinUrl: job.linkedinUrl || '',
        resume: job.resume || '',
        dateApplied: job.dateApplied
          ? new Date(job.dateApplied).toISOString().split('T')[0]
          : new Date().toISOString().split('T')[0],
        salary: job.salary || '',
        notes: job.notes || '',
        status: job.status || 'wishlist',
      })
    } else {
      setForm(initialForm)
    }

    setErrors({})
  }, [isOpen, job])

  if (!isOpen) {
    return null
  }

  const handleChange = (event) => {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))

    setErrors((current) => ({
      ...current,
      [name]: '',
    }))
  }

  const validate = () => {
    const newErrors = {}

    if (!form.company.trim()) {
      newErrors.company = 'Company name is required.'
    }

    if (!form.title.trim()) {
      newErrors.title = 'Job title is required.'
    }

    if (
      form.linkedinUrl &&
      !/^https?:\/\/.+/i.test(form.linkedinUrl)
    ) {
      newErrors.linkedinUrl = 'Enter a valid URL.'
    }

    return newErrors
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    const validationErrors = validate()

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    const savedJob = {
      ...form,
      ...(job ? { id: job.id } : {}),
      dateApplied: new Date(
        `${form.dateApplied}T00:00:00`,
      ).toISOString(),
    }

    await onSave(savedJob)

    setForm(initialForm)
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-100 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
              <BriefcaseBusiness size={19} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900 dark:text-white">
                {job ? 'Edit job' : 'Add new job'}
              </h2>

              <p className="text-xs text-slate-500 dark:text-slate-400">
                {job
                  ? 'Update your job opportunity'
                  : 'Track a new opportunity'}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
            aria-label="Close modal"
          >
            <X size={19} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="max-h-[70vh] space-y-5 overflow-y-auto p-5">
            <div className="grid gap-5 sm:grid-cols-2">
              <FormField
                label="Company name"
                name="company"
                value={form.company}
                onChange={handleChange}
                error={errors.company}
                placeholder="e.g. Microsoft"
                required
              />

              <FormField
                label="Job title / role"
                name="title"
                value={form.title}
                onChange={handleChange}
                error={errors.title}
                placeholder="e.g. QA Automation Engineer"
                required
              />

              <FormField
                label="LinkedIn job URL"
                name="linkedinUrl"
                value={form.linkedinUrl}
                onChange={handleChange}
                error={errors.linkedinUrl}
                placeholder="https://linkedin.com/jobs/..."
              />

              <FormField
                label="Resume used"
                name="resume"
                value={form.resume}
                onChange={handleChange}
                placeholder="e.g. QA_Lead_Resume"
              />

              <FormField
                label="Date applied"
                name="dateApplied"
                type="date"
                value={form.dateApplied}
                onChange={handleChange}
              />

              <FormField
                label="Salary range"
                name="salary"
                value={form.salary}
                onChange={handleChange}
                placeholder="e.g. ₹25-30 LPA"
              />

              <div className="sm:col-span-2">
                <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                  Status
                </label>

                <select
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
                >
                  {JOB_STATUSES.map((status) => (
                    <option key={status.id} value={status.id}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                  Notes
                </label>

                <textarea
                  name="notes"
                  value={form.notes}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Recruiter name, referral information, interview notes..."
                  className="w-full resize-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-200 px-5 py-4 dark:border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Cancel
            </button>

            <button
              type="submit"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700"
            >
              {job ? 'Update job' : 'Save job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function FormField({
  label,
  name,
  value,
  onChange,
  error,
  placeholder,
  type = 'text',
  required = false,
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
        {label}

        {required && (
          <span className="ml-1 text-red-500">*</span>
        )}
      </label>

      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        onClick={(event) => {
          if (type === 'date') {
            event.currentTarget.showPicker?.()
          }
        }}
        placeholder={placeholder}
        className={`h-10 w-full rounded-lg border bg-white px-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:ring-2 focus:ring-indigo-500/20 dark:bg-slate-950 dark:text-white ${
          error
            ? 'border-red-400 focus:border-red-500'
            : 'border-slate-200 focus:border-indigo-500 dark:border-slate-700'
        }`}
      />

      {error && (
        <p className="mt-1 text-xs text-red-500">
          {error}
        </p>
      )}
    </div>
  )
}

export default JobModal