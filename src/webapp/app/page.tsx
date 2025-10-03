'use client'

import { Landing } from "@/components/landing";
import { Leva } from "leva";

export default function Home() {
  return (
    <>
      <Landing />
      <Leva hidden />
    </>
  );
}
