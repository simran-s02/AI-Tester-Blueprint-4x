import { useCallback, useEffect, useState } from 'react'
import {
  addJob,
  deleteJob,
  getAllJobs,
  updateJob,
} from '../db/database'

export const useJobs = () => {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadJobs = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const storedJobs = await getAllJobs()

      setJobs(storedJobs || [])
    } catch (err) {
      console.error('Failed to load jobs:', err)
      setError('Unable to load your jobs.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadJobs()
  }, [loadJobs])

  const createJob = async (job) => {
    try {
      setError(null)

      const newJob = {
        ...job,
        id: job.id || crypto.randomUUID(),
        createdAt: job.createdAt || new Date().toISOString(),
      }

      await addJob(newJob)

      setJobs((currentJobs) => [
        ...currentJobs,
        newJob,
      ])

      return newJob
    } catch (err) {
      console.error('Failed to create job:', err)
      setError('Unable to create the job.')
      throw err
    }
  }

  const editJob = async (job) => {
    try {
      setError(null)

      await updateJob(job)

      setJobs((currentJobs) =>
        currentJobs.map((currentJob) =>
          currentJob.id === job.id
            ? job
            : currentJob,
        ),
      )

      return job
    } catch (err) {
      console.error('Failed to update job:', err)
      setError('Unable to update the job.')
      throw err
    }
  }

  const removeJob = async (id) => {
    try {
      setError(null)

      await deleteJob(id)

      setJobs((currentJobs) =>
        currentJobs.filter(
          (job) => job.id !== id,
        ),
      )
    } catch (err) {
      console.error('Failed to delete job:', err)
      setError('Unable to delete the job.')
      throw err
    }
  }

  return {
    jobs,
    loading,
    error,
    createJob,
    editJob,
    removeJob,
    reloadJobs: loadJobs,
  }
}