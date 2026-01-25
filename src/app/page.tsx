'use client'

import { useState, useEffect } from 'react'
import { getDocuments } from './actions'

type Document = {
  id: number
  title: string
  description: string | null
  fileUrl: string
  category: string | null
  uploadedAt: Date | string
}

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    // Initial load
    fetchDocs()
  }, [])

  async function fetchDocs(query?: string) {
    const docs = await getDocuments(query)
    setDocuments(docs)
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    fetchDocs(search)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">QuXAT Store</h1>
          <a href="/admin" className="text-indigo-600 hover:text-indigo-900">Admin Upload</a>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="mb-8 flex gap-2">
                <input 
                    type="text" 
                    placeholder="Search documents..." 
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="flex-1 rounded-md border border-gray-300 p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
                <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Search</button>
            </form>

            {/* Document List */}
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                    {documents.map((doc) => (
                        <li key={doc.id}>
                            <a href={doc.fileUrl} target="_blank" rel="noopener noreferrer" className="block hover:bg-gray-50">
                                <div className="px-4 py-4 sm:px-6">
                                    <div className="flex items-center justify-between">
                                        <p className="text-sm font-medium text-indigo-600 truncate">{doc.title}</p>
                                        <div className="ml-2 flex-shrink-0 flex">
                                            <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                {doc.category || 'Uncategorized'}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="mt-2 sm:flex sm:justify-between">
                                        <div className="sm:flex">
                                            <p className="flex items-center text-sm text-gray-500">
                                                {doc.description}
                                            </p>
                                        </div>
                                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                            <p>
                                                Uploaded on <time dateTime={doc.uploadedAt.toString()}>{new Date(doc.uploadedAt).toLocaleDateString()}</time>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </a>
                        </li>
                    ))}
                    {documents.length === 0 && (
                        <li className="px-4 py-8 text-center text-gray-500">No documents found.</li>
                    )}
                </ul>
            </div>
        </div>
      </main>
    </div>
  )
}
