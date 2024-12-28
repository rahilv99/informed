import AIPodcastWalkthrough from "../walkthrough";
import { Fingerprint, IdCard, BrainCog } from "lucide-react";

export default function Home() {
  const steps = [
    {
      icon: <Fingerprint className="w-8 h-8" />,
      title: "Interests",
      content:
        "Ex: Generative AI, Text-to-Speech, Transformer Models, Linguistics",
      prompt:
        "List some of your major interests so I can find data relevant to you.",
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
      prompt:
        "Auxiom is finding recent advances related to you and generating insights...",
    },
  ];

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-4 sm:p-8 md:p-24 text-black">
      <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
        <h1 className="text-2xl sm:text-4xl font-bold text-center mb-4 sm:mb-8">
          Welcome to Insight
        </h1>
        <p className="text-base sm:text-xl text-center mb-6 sm:mb-12">
          Get expert analyses of your content.
        </p>
        <AIPodcastWalkthrough steps={steps} product="pulse" />
      </div>
    </main>
  );
}
