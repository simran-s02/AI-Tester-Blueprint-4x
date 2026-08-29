import { BriefcaseBusiness, Moon, Plus, Sun } from 'lucide-react'

function Header({ darkMode, onToggleDarkMode, onAddJob }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
            <BriefcaseBusiness size={20} />
          </div>

          <div>
            <h1 className="text-base font-bold tracking-tight text-slate-900 dark:text-white">
              JobTracker
              <span className="text-indigo-600"> AI</span>
            </h1>

            <p className="hidden text-xs text-slate-500 sm:block">
              Your intelligent career command center
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onToggleDarkMode}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <button
            type="button"
            onClick={onAddJob}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
          >
            <Plus size={17} />
            <span className="hidden sm:inline">Add Job</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header