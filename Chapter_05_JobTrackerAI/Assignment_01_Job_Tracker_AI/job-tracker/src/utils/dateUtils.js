export function getDaysSinceApplied(dateApplied) {
  if (!dateApplied) {
    return 0
  }

  const appliedDate = new Date(dateApplied)
  const today = new Date()

  appliedDate.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)

  const difference =
    today.getTime() - appliedDate.getTime()

  return Math.floor(
    difference / (1000 * 60 * 60 * 24),
  )
}