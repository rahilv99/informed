"use client";

import Link from "next/link";
import { GL } from "./gl";
import { Pill } from "./pill";
import { Button } from "./ui/button";
import { useState } from "react";

export function Landing() {
  const [hovering, setHovering] = useState(false);
  return (
    <div className="flex flex-col h-svh justify-between">
      <GL hovering={hovering} />

      <div className="pb-16 mt-auto text-center relative">
        <Pill className="mb-6">BETA RELEASE</Pill>
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-sentient">
          A new level of <i className="font-light">visibility</i> <br />
          in US policy
        </h1>
        <p className="font-mono text-lg sm:text-base text-foreground/60 mt-8 max-w-[440px] mx-auto">
          Through an event-driven data layer designed for LLMs
        </p>

        <Link className="contents max-sm:hidden" href="/search">
          <Button
            className="mt-14"
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
          >
            Try Search
          </Button>
        </Link>
        <Link className="contents sm:hidden" href="/search">
          <Button
            size="sm"
            className="mt-14"
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
          >
            Try Search
          </Button>
        </Link>
      </div>
    </div>
  );
}
