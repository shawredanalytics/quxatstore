'use client'

import { useState } from 'react'
import { uploadDocument } from '../actions'

export default function AdminPage() {
  const [status, setStatus] = useState<string>('')

  async function handleSubmit(formData: FormData) {
    setStatus('Uploading...')
    try {
      await uploadDocument(formData)
      setStatus('Upload successful!')
      const form = document.querySelector('form') as HTMLFormElement
      form.reset()
    } catch (error) {
      console.error(error)
      setStatus('Upload failed.')
    }
  }

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-6">Admin Upload</h1>
        <form action={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Title</label>
            <input name="title" required className="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea name="description" className="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Category</label>
            <select name="category" className="mt-1 block w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                <option value="Manual">Manual</option>
                <option value="Procedure">Procedure</option>
                <option value="Form">Form</option>
                <option value="Record">Record</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">File</label>
            <input type="file" name="file" required className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
          </div>
          <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Upload Document
          </button>
        </form>
        {status && <p className="mt-4 text-center text-sm font-medium text-indigo-600">{status}</p>}
      </div>
    </div>
  )
}
