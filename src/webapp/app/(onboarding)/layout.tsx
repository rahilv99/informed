"use client";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { CircleIcon } from "lucide-react";
import { redirect } from "next/navigation";
import React, { useState } from "react";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [currentPage, setCurrentPage] = useState(1);

  const handlePageChange = (page: React.SetStateAction<number>) => {
    setCurrentPage(page);
    if (page ===1) {
      redirect("/identity");
    } else if (page === 2) {
      redirect("/keywords");
    } else if (page === 3) {
      redirect("/day");
    }
  };

  const handlePreviousPage = () => {
    if (currentPage === 2) {
      handlePageChange(1);
    } else if (currentPage === 3) {
      handlePageChange(2);
    }
  };

  const handleNextPage = () => {
    if (currentPage === 1) {
      handlePageChange(2);
    } else if (currentPage === 2) {
      handlePageChange(3);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-cyan-900">
    <div className="flex h-screen flex-col md:flex-col md:overflow-hidden">
      <header>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center">
          <CircleIcon className="h-8 w-8 text-cyan-300" />
          <span className="ml-2 text-3xl text-white">Onboarding</span>
        </div>
      </header>
      <div className="flex-grow p-6 overflow-y-auto md:p-12">{children}</div>
      <section className="p-4 md:p-10 flex-shrink-0">
        <div className="flex justify-center items-center h-full text-white">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
          <PaginationPrevious className="text-xl font-bold" href="#" onClick={handlePreviousPage} />
              </PaginationItem>
              <PaginationItem>
          <PaginationLink className="text-xl font-bold" href="/identity" onClick={() => setCurrentPage(1)}>1</PaginationLink>
              </PaginationItem>
              <PaginationItem>
          <PaginationLink className="text-xl font-bold" href="/keywords" onClick={() => setCurrentPage(2)}>2</PaginationLink>
              </PaginationItem>
              <PaginationItem>
          <PaginationLink className="text-xl font-bold" href="/day" onClick={() => setCurrentPage(3)}>3</PaginationLink>
              </PaginationItem>
              <PaginationItem>
          <PaginationNext className="text-xl font-bold" href="#" onClick={handleNextPage}/>
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      </section>
    </div>
    </div>
  );
}
