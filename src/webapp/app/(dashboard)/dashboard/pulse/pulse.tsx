"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PenIcon, Check } from "lucide-react";
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
import { Switch } from "@/components/ui/switch";
import { CarouselApi } from "@/components/ui/carousel";
import { submitDay, setAccountStatus } from "@/lib/actions";
import React from "react";


export default function PulsePage({ keywords, day, deliveryStatus, accountStatus }: 
    { keywords: string[], day: number, deliveryStatus: boolean, accountStatus: boolean }) {

    const currentKeywords: string[] = keywords;
    const currentDay: number = day;
    const { toast } = useToast();

    const [api, setApi] = React.useState<CarouselApi>();
    const [current, setCurrent] = React.useState(currentDay);

    const [isPaused, setIsPaused] = React.useState(accountStatus);

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

    const handlePauseToggle = async (checked: boolean) => {
        setIsPaused(checked);
        await setAccountStatus(checked);
        toast({
          title: checked ?  "Podcasts Resumed" : "Podcasts Paused",
          description: checked ?  "Your podcasts will resume as scheduled." : "Your podcasts have been temporarily paused.",
        });
      };

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight text-black">Pulse</h1>
            <p className="text-black">
                A personalized weekly podcast summarizing the latest updates in your
                field. All content includes citations to academic sources.
            </p>
            <Separator className="my-6" />
            <Card className="bg-black bg-opacity-10 border-none">
                <CardContent className="space-y-6">
                    <div className="space-y-4">
                        <div>
                            <p className="mb-2 text-xl font-bold text-black pt-6">Next Pulse Podcast in {days_left} {day_txt}</p>
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
                            <div className="flex flex-wrap gap-2 justify-center">
                                <Carousel
                                    className="max-w-sm"
                                    opts={{
                                        loop: true,
                                    }}
                                    setApi={setApi}
                                >
                                    <CarouselContent className="-ml-1">
                                        {days.map((day, index) => (
                                            <CarouselItem key={index} className="pl-1 basis-1/2">
                                                <div className="p-1">
                                                    <div className="bg-slate-600/30 rounded-xl backdrop-filter backdrop-blur-lg">
                                                        <div className="flex aspect-square items-center justify-center p-6">
                                                            <span className="text-2xl font-semibold text-black">
                                                                {day}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </CarouselItem>
                                        ))}
                                    </CarouselContent>
                                    <CarouselPrevious className="bg-slate-600/30 rounded-3xl backdrop-filter backdrop-blur-lg text-gray-800 border-none hover:bg-slate-600/50 transition duration-300" />
                                    <CarouselNext className="bg-slate-600/30 rounded-3xl backdrop-filter backdrop-blur-lg text-gray-800 border-none hover:bg-slate-600/50 transition duration-300" />
                                </Carousel>
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <Link href="/dashboard/edit-keywords">
                                <Button
                                    variant="outline"
                                    className="bg-slate-600/30 text-black hover:bg-gray-200"
                                >
                                    <PenIcon className="mr-2 h-4 w-4" /> Edit Interests
                                </Button>
                            </Link>
                            <Button
                                onClick={handleSaveChanges}
                                className="bg-gray-700 text-gray-100 hover:bg-gray-400"
                            >
                                <Check className="mr-2 h-4 w-4" /> Save Changes
                            </Button>
                        </div>
                        <div>
                          <h3 className="mb-2 font-medium text-black">Activity</h3>
                          <div className="flex items-center space-x-2">
                            <Switch
                              id="pause-mode"
                              checked={isPaused}
                              onCheckedChange={handlePauseToggle}
                            />
                            <label htmlFor="pause-mode" className="text-sm text-black">
                              {isPaused ? "Podcasts are active" : "Podcasts are paused"}
                            </label>
                          </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
