import {
  BriefcaseBusiness,
  CalendarClock,
  MessageSquareText,
  Trophy,
} from 'lucide-react'

function DashboardStats({ jobs = [] }) {
  const totalApplications = jobs.filter(
    (job) => job.status !== 'wishlist',
  ).length

  const interviews = jobs.filter(
    (job) => job.status === 'interview',
  ).length

  const followUps = jobs.filter(
    (job) => job.status === 'follow-up',
  ).length

  const offers = jobs.filter(
    (job) => job.status === 'offer',
  ).length

  const stats = [
    {
      label: 'Total Applications',
      value: totalApplications,
      icon: BriefcaseBusiness,
    },
    {
      label: 'Interviews',
      value: interviews,
      icon: MessageSquareText,
    },
    {
      label: 'Follow-ups',
      value: followUps,
      icon: CalendarClock,
    },
    {
      label: 'Offers',
      value: offers,
      icon: Trophy,
    },
  ]

  return (
    <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {stats.map(({ label, value, icon: Icon }) => (
        <div
          key={label}
          className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {label}
            </p>

            <Icon
              size={18}
              className="text-slate-400"
            />
          </div>

          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            {value}
          </p>
        </div>
      ))}
    </section>
  )
}

export default DashboardStats