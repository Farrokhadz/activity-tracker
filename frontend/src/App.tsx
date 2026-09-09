import { useState, useEffect } from 'react'

interface Entry {
  id: number
  date: string
  category: number
  duration: number
  note: string
}

function App() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/entries/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch entries')
        }
        return response.json()
      })
      .then((data: Entry[]) => {
        setEntries(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <p className="p-4">Loading...</p>
  if (error) return <p className="p-4 text-red-600">Error: {error}</p>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Activity Tracker</h1>
      <ul className="space-y-2">
        {entries.map((entry) => (
          <li key={entry.id} className="bg-white p-4 rounded shadow">
            {entry.date} — category #{entry.category} — {entry.duration} min
            {entry.note && ` — ${entry.note}`}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App
