import { User, FileUp, BrainCog } from 'lucide-react'
import AIPodcastWalkthrough from "@/app/(dashboard)/demo/walkthrough"


export default function Home() {
  const steps = [
    {
      icon: <User className="w-6 h-6" />,
      title: "Create User Profile",
      content: "Ex:  Generative AI, Text-to-Speech, Transformer Models, Linguistics",
      prompt:  "Enter keywords related to your research interests."
    },
    {
      icon: <FileUp className="w-6 h-6" />,
      title: "Upload Articles",
      prompt:  "Upload PDFs of scientific articles to your queue.",
      content: "Ex: Attention is All You Need"
    },
    {
      icon: <BrainCog className="w-6 h-6" />,
      title: "Auxiom Analysis",
      content: "Auxiom selects an article and generates an expert analysis.",
      prompt: "Auxiom is analyzing the uploaded articles and generating insights..."
    },
  ]

  
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-black">
      <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Welcome to Insight</h1>
      <p className="text-xl text-center mb-12">Get expert analyses of your content.</p>
        <AIPodcastWalkthrough steps = {steps} product = 'insight'/>
      </div>
    </main>
  )
}

