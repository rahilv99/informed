import JournalClubPodcastWalkthrough from "./journal-club"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center text-white">Journal Club Demo</h1>
        <JournalClubPodcastWalkthrough />
      </div>
    </main>
  )
}

