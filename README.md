# QuXAT Store

A quality systems documentation repository platform built with Next.js, Prisma, and SQLite.

## Features

- **Admin Upload**: Upload documents with title, description, and category.
- **User Search**: Search for documents by title, description, or category.
- **Document Access**: View and download uploaded documents.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Database Setup**:
    Initialize the SQLite database:
    ```bash
    npx prisma migrate dev --name init
    ```

3.  **Run the Development Server**:
    ```bash
    npm run dev
    ```

4.  **Open the Application**:
    Visit [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

- `src/app/page.tsx`: Main user interface for searching and listing documents.
- `src/app/admin/page.tsx`: Admin interface for uploading documents.
- `src/app/actions.ts`: Server actions for handling file uploads and database queries.
- `src/lib/prisma.ts`: Prisma client instance.
- `prisma/schema.prisma`: Database schema definition.
- `public/uploads`: Directory where uploaded files are stored.

## Technologies

- Next.js 15+ (App Router)
- Prisma (ORM)
- SQLite (Database)
- Tailwind CSS (Styling)
