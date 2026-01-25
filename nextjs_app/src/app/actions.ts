'use server'

import { writeFile } from 'fs/promises'
import { join } from 'path'
import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function uploadDocument(formData: FormData) {
  const file = formData.get('file') as File
  const title = formData.get('title') as string
  const description = formData.get('description') as string
  const category = formData.get('category') as string

  if (!file) {
    throw new Error('No file uploaded')
  }

  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)

  // Create unique filename
  const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
  const filename = file.name.replace(/[^a-zA-Z0-9.-]/g, '_') // Sanitize filename
  const savedFilename = `${uniqueSuffix}-${filename}`
  
  const uploadDir = join(process.cwd(), 'public', 'uploads')
  const path = join(uploadDir, savedFilename)
  
  await writeFile(path, buffer)
  
  const fileUrl = `/uploads/${savedFilename}`

  await prisma.document.create({
    data: {
      title,
      description,
      fileUrl,
      fileName: file.name,
      fileType: file.type,
      category
    }
  })

  revalidatePath('/')
  return { success: true }
}

export async function getDocuments(query?: string) {
  const documents = await prisma.document.findMany({
    where: query ? {
      OR: [
        { title: { contains: query } },
        { description: { contains: query } },
        { category: { contains: query } }
      ]
    } : {},
    orderBy: { uploadedAt: 'desc' }
  })
  return documents
}
