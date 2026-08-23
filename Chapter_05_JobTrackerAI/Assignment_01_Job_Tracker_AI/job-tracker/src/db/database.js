import { openDB } from 'idb'

const DB_NAME = 'job-tracker-ai'
const DB_VERSION = 1
const STORE_NAME = 'jobs'

export const dbPromise = openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    if (!db.objectStoreNames.contains(STORE_NAME)) {
      const store = db.createObjectStore(STORE_NAME, {
        keyPath: 'id',
      })

      store.createIndex('status', 'status')
      store.createIndex('dateApplied', 'dateApplied')
      store.createIndex('company', 'company')
    }
  },
})

export const getAllJobs = async () => {
  const db = await dbPromise
  return db.getAll(STORE_NAME)
}

export const getJob = async (id) => {
  const db = await dbPromise
  return db.get(STORE_NAME, id)
}

export const addJob = async (job) => {
  const db = await dbPromise
  await db.put(STORE_NAME, job)
  return job
}

export const updateJob = async (job) => {
  const db = await dbPromise
  await db.put(STORE_NAME, job)
  return job
}

export const deleteJob = async (id) => {
  const db = await dbPromise
  await db.delete(STORE_NAME, id)
}

export const clearAllJobs = async () => {
  const db = await dbPromise
  await db.clear(STORE_NAME)
}