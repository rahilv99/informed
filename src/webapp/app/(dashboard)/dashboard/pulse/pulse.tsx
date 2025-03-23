"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PenIcon, Check } from 'lucide-react';
import Link from "next/link";
import { useToast } from "@/hooks/use-toast";
import { Separator } from "@/components/ui/separator";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { CarouselApi } from "@/components/ui/carousel";
import { submitDay } from "@/lib/actions";
import React from "react";

export default function PulsePage({ keywords, day, deliveryStatus }: {
  keywords: string[];
  day: number;
  deliveryStatus: boolean;
}) {
  const currentKeywords: string[] = keywords;
  const currentDay: number = day;
  const { toast } = useToast();

  const [api, setApi] = React.useState<CarouselApi>();
  const [current, setCurrent] = React.useState(currentDay);

  // get today's day
  const date = new Date();
  const today = date.getDay();
  let days_left = currentDay - today;
  let day_txt = "Days";

  // logic for when user will receive the next podcast
  if (days_left < 0) {
    days_left = days_left + 7;
  } else if (deliveryStatus) {
    days_left += 7;
  }
  if (days_left == 1) {
    day_txt = "Day";
  }

  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];

  React.useEffect(() => {
    if (!api) {
      return;
    }

    api.scrollTo(current);

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap());
    });
  }, [api]);

  const handleSaveChanges = async () => {
    // Mock API call
    await submitDay(current);

    toast({
      title: "Settings Saved",
      description: "Your podcast settings have been updated.",
    });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-black">Pulse</h1>
      <p className="text-black">
        A personalized weekly podcast summarizing the latest updates on topics that are important to you. All content includes citations to primary data sources.
      </p>
      <Separator className="my-6" />
      <Card className="bg-black bg-opacity-10 border-none p-2 sm:p-6">
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div>
              <p className="mb-2 text-xl font-bold text-black pt-6">
                Next Pulse Podcast in {days_left} {day_txt}
              </p>
            </div>
            <h3 className="mb-2 font-medium text-black">Podcast Settings</h3>

            <div>
              <h3 className="mb-2 font-medium text-black">Current Interests</h3>
              <div className="flex flex-wrap gap-2">
                {currentKeywords.map((interest) => (
                  <span
                    key={interest}
                    className="rounded-full bg-slate-600/30 px-2 py-1 text-sm text-black"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="mb-2 font-medium text-black">Delivery Day</h3>
              <div className="flex flex-wrap gap-2 justify-center px-8 sm:px-12">
                <Carousel
                  className="w-full max-w-[280px] sm:max-w-sm md:max-w-md"
                  opts={{
                    loop: true,
                  }}
                  setApi={setApi}
                >
                  <CarouselContent className="-ml-1">
                    {days.map((day, index) => (
                      <CarouselItem
                        key={index}
                        className="pl-1 basis-1/2"
                      >
                        <div className="p-1">
                        <div className={`rounded-3xl backdrop-filter backdrop-blur-lg transition-all duration-300 ${
                              index === current 
                                ? 'bg-black bg-opacity-30 scale-100' 
                                : 'bg-black bg-opacity-10 scale-90'
                            }`}>
                            <div className="flex aspect-square items-center justify-center p-2 sm:p-4">
                              <span className="text-base sm:text-lg md:text-2xl font-semibold text-black">
                                {day}
                              </span>
                            </div>
                          </div>
                        </div>
                      </CarouselItem>
                    ))}
                  </CarouselContent>
                  <CarouselPrevious className="hidden md:flex bg-black text-black bg-opacity-20 rounded-full backdrop-filter backdrop-blur-lg border-none hover:bg-gray-700 transition duration-300" /> 
                  <CarouselNext className="hidden md:flex bg-black text-black bg-opacity-20 rounded-full backdrop-filter backdrop-blur-lg border-none hover:bg-gray-700 transition duration-300" />
                </Carousel>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <Link href="/dashboard/edit-keywords" className="w-full sm:w-auto">
                <Button
                  variant="outline"
                  className="w-full bg-slate-600/30 text-black hover:bg-gray-200"
                >
                  <PenIcon className="mr-2 h-4 w-4" /> Edit Interests
                </Button>
              </Link>
              <Button
                onClick={handleSaveChanges}
                className="w-full sm:w-auto bg-gray-700 text-gray-100 hover:bg-gray-400"
              >
                <Check className="mr-2 h-4 w-4" /> Save Changes
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

