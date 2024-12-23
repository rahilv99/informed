import AIPodcastWalkthrough from "./updates"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="container mx-auto px-4 py-8">
              <h1 className="text-4xl font-bold mb-8 text-center text-white">Updates Podcast Demo</h1>
              <AIPodcastWalkthrough />
            </div>
    </main>
  )
}

