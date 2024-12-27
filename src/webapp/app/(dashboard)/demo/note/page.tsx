import NotesDemo from './notes-demo'

export default function Home() {
  return (
    <main className="min-h-screen text-black">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">Welcome to Auxiom Notes</h1>
        <p className="text-xl text-center mb-12">Get the answers you've been looking for.</p>
        <NotesDemo />
      </div>
    </main>
  )
}

