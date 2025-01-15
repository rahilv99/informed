
import { redirect } from "next/navigation";
import PricingPage from "./personal";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "components/ui/tabs";
import EnterprisePricingPage from "./enterprise";

export default async function Page() {

  return (
    <div className="min-h-screen text-black flex flex-col">
      <div className="max-w-6xl w-full mx-auto px-4 py-12 flex flex-col items-center">
      <Tabs defaultValue="personal" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mx-auto h-auto rounded-lg bg-black bg-opacity-10 p-1 text-gray-800">
          <TabsTrigger
            value="personal"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-2 text-xs sm:px-4 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Personal
          </TabsTrigger>
          <TabsTrigger
            value="enterprise"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-2 text-xs sm:px-4 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Enterprise
          </TabsTrigger>
        </TabsList>

        <TabsContent value="personal">
          <PricingPage />
        </TabsContent>

        <TabsContent value="enterprise">
          <EnterprisePricingPage />
        </TabsContent>
      </Tabs>
      </div>
    </div>
  );
}
