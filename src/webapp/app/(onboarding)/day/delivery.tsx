"use client";
import { Button } from "@/components/ui/button";
import { redirect } from "next/navigation";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { type CarouselApi } from "@/components/ui/carousel";
import React from "react";

export function Delivery() {
  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  const [api, setApi] = React.useState<CarouselApi>();
  const [current, setCurrent] = React.useState(0);

  React.useEffect(() => {
    if (!api) {
      return;
    }

    setCurrent(api.selectedScrollSnap());

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap());
      const ret = api.selectedScrollSnap();
      console.log("Current day:", days[ret]);
    });
  }, [api]);

  const handleSubmit = () => {
    // BACKEND - replace with sending to database
    console.log("Selected day:", days[current]);
    redirect("/pricing");
  };

  return (
        <main>
          <section className="py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
                <div>
                  <h1 className="text-3xl font-bold text-white mb-6 sm:text-4xl">
                    What day would you like your weekly podcast delivered?
                  </h1>
                  <p className="mt-4 text-base text-gray-200">
                    Our paid plans offer longer and more frequent podcasts in
                    addition to an array of great features. Change your plan
                    anytime.
                  </p>
                </div>
              </div>
            </div>
          </section>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-wrap gap-2"></div>
          </div>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
                        <div className = 'bg-white bg-opacity-10 rounded-xl backdrop-filter backdrop-blur-lg'>
                          <div className="flex aspect-square items-center justify-center p-6 ">
                            <span className="text-2xl font-semibold text-white">
                              {day}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="bg-white bg-opacity-10 rounded-3xl backdrop-filter backdrop-blur-lg text-white border-none hover:bg-cyan-100 transition duration-300"/>
                <CarouselNext className="bg-white bg-opacity-10 rounded-3xl backdrop-filter backdrop-blur-lg text-white border-none hover:bg-cyan-100 transition duration-300"/>
              </Carousel>
            </div>
            <div className="flex justify-end py-5">
              <Button onClick={handleSubmit} className="mt-4 bg-white text-black px-4 py-2 rounded-full font-semibold hover:bg-cyan-100 transition duration-300">
                Submit
              </Button>
            </div>
          </div>
        </main>
  );
}
