import AIPodcastWalkthrough from "../walkthrough"
import { Fingerprint, IdCard, BrainCog } from "lucide-react"

export default function Home() {
  const steps = [
    {
      icon: <Fingerprint className="w-8 h-8" />,
      title: "Interests",
      content: "Ex: Generative AI, Text-to-Speech, Transformer Models, Linguistics",
      prompt: "List some of your major interests so I can find data relevant to you.",
    },
    {
      icon: <IdCard className="w-8 h-8" />,
      title: "Role",
      content: "Ex: Researcher",
      prompt: "Please share your role to help me understand your objectives.",
    },
    {
      icon: <BrainCog className="w-6 h-6" />,
      title: "Auxiom Analysis",
      content: "Auxiom searches our database of academic articles",
      prompt: "Auxiom is finding recent advances related to you and generating insights..."
    },
  ]

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-black">
      <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Welcome to Pulse</h1>
      <p className="text-xl text-center mb-12">Stay up to date on developments you're interested in.</p>
              <AIPodcastWalkthrough steps = {steps} product = 'pulse' />
            </div>
    </main>
  )
}

