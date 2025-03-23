
import { redirect } from "next/navigation";
import PricingPage from "./personal";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "components/ui/tabs";

export default async function Page() {

  return (
    <div className="min-h-screen text-black flex flex-col">
      <div className="max-w-6xl w-full mx-auto px-4 py-12 flex flex-col items-center">
          <PricingPage />
      </div>
    </div>
  );
}
