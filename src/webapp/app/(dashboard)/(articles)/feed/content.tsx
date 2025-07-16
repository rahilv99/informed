"use client"

import { useState } from "react"
import { Search, Calendar, Clock, Filter } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { useRouter } from "next/navigation"


export default function ArticlesPage({articles}: {
  articles: Array<{
    id: number
    title: string
    summary: string
    people: string[]
    topics: string[]
    tags: string[]
    date: string
    duration: number
    featured: boolean
  }>
}) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTopic, setSelectedTopic] = useState("All")
  const [filteredArticles, setFilteredArticles] = useState(articles)
  const [currentPage, setCurrentPage] = useState(1)

  const router = useRouter()
  
  const ITEMS_PER_PAGE = 10

  // Get all unique topics from articles for filtering
  const getAllTopics = (articles: any[]) => {
    const allTopics = articles.flatMap(article => article.topics)
    return ["All", ...Array.from(new Set(allTopics)).sort()]
  }

  const topics = getAllTopics(articles)

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    filterArticles(query, selectedTopic)
  }

  const handleTopicFilter = (topic: string) => {
    setSelectedTopic(topic)
    filterArticles(searchQuery, topic)
  }

  const filterArticles = (query: string, topic: string) => {
    let filtered = articles

    if (topic !== "All") {
      filtered = filtered.filter((article) => article.topics.includes(topic))
    }

    if (query) {
      filtered = filtered.filter(
        (article) =>
          article.title.toLowerCase().includes(query.toLowerCase()) ||
          article.summary.toLowerCase().includes(query.toLowerCase()) ||
          article.people.some(person => person.toLowerCase().includes(query.toLowerCase())) ||
          article.topics.some(topic => topic.toLowerCase().includes(query.toLowerCase())) ||
          article.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())),
      )
    }

    setFilteredArticles(filtered)
    setCurrentPage(1) // Reset to first page when filtering
  }

  // Calculate pagination
  const totalPages = Math.ceil(filteredArticles.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const paginatedArticles = filteredArticles.slice(startIndex, endIndex)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-2xl mx-auto space-y-4">
            {/* Search Bar */}
            <div className="relative bg-opacity-10 bg-black">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="Search articles, authors, or topics..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 h-12 text-base border-0 bg-muted/50 ring-1"
              />
            </div>

            {/* Filter Topics */}
            <div className="overflow-x-auto whitespace-nowrap py-1 px-0">
              <div className="inline-flex gap-2">
              {topics.map((topic) => (
                <Button
                key={topic}
                variant={selectedTopic === topic ? "default" : "outline"}
                size="sm"
                onClick={() => handleTopicFilter(topic)}
                className="rounded-full text-xs font-medium bg-primary text-primary-foreground"
                >
                {topic}
                </Button>
              ))}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Results Info */}
          <div className="flex items-center justify-between mb-8">
            <div className="text-sm text-muted-foreground">
              {filteredArticles.length > 0 && (
                <>
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredArticles.length)} of {filteredArticles.length} {filteredArticles.length === 1 ? "article" : "articles"}
                  {selectedTopic !== "All" && ` in ${selectedTopic}`}
                  {searchQuery && ` matching "${searchQuery}"`}
                </>
              )}
              {filteredArticles.length === 0 && (
                <>
                  0 articles
                  {selectedTopic !== "All" && ` in ${selectedTopic}`}
                  {searchQuery && ` matching "${searchQuery}"`}
                </>
              )}
            </div>
          </div>

          {/* Articles Feed */}
          <div className="space-y-8">
            {paginatedArticles.map((article, index) => (
              <Card
                onClick={() => {
                  // Navigate to article detail page (replace with actual navigation logic)
                  router.push(`/article/${article.id}`)
                  console.log(`Navigating to article ${article.id}`)
                }}
                key={article.id}
                className={`group hover:shadow-lg transition-all duration-300 border-0 shadow-sm bg-black bg-opacity-20 cursor-pointer ${
                  article.featured ? "ring-1 ring-primary/20" : ""
                }`}
              >
                <CardContent className="p-6">
                  {/* Featured Badge */}
                  {article.featured && (
                    <Badge className="w-fit mb-3 bg-primary text-primary-foreground">Featured</Badge>
                  )}
                  
                  <div className="space-y-3">

                    {/* Title */}
                    <h2 className="font-bold leading-tight group-hover:text-primary transition-colors text-lg md:text-xl">
                      {article.title}
                    </h2>

                    {/* summary */}
                    <p
                      className={`text-muted-foreground leading-relaxed ${
                        index === 0 || article.featured ? "text-base" : "text-sm"
                      }`}
                    >
                      {article.summary}
                    </p>

                    {/* Topics */}
                    <div className="flex flex-wrap gap-2">
                      {article.topics.slice(0, 3).map((topic, topicIndex) => (
                        <Badge key={topicIndex} variant="outline" className="text-xs bg-primary/10 text-primary border-primary/20">
                          {topic}
                        </Badge>
                      ))}
                      {article.topics.length > 3 && (
                        <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/20">
                          +{article.topics.length - 3} more
                        </Badge>
                      )}
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      {article.tags.slice(0, 4).map((tag, tagIndex) => (
                        <Badge key={tagIndex} variant="secondary" className="text-xs bg-muted/50">
                          {tag}
                        </Badge>
                      ))}
                      {article.tags.length > 4 && (
                        <Badge variant="secondary" className="text-xs bg-muted/50">
                          +{article.tags.length - 4}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Article Meta */}
                  <div className="flex items-center justify-between pt-4 mt-4 border-t border-border/50">
                    <div className="flex items-center space-x-3">
                      <div className="flex -space-x-1">
                        {article.people.map((person, personIndex) => (
                          <Avatar key={personIndex} className="h-8 w-8 border-2 border-background">
                            <AvatarImage alt={person} />
                            <AvatarFallback>
                              {person
                                .split(" ")
                                .map((n: string) => n[0])
                                .join("")}
                            </AvatarFallback>
                          </Avatar>
                        ))}
                      </div>
                      <div className="text-sm">
                        <p className="font-medium">
                          {article.people.join(", ")}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3" />
                        <span>{formatDate(article.date)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{article.duration} minute read</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {filteredArticles.length > 0 && totalPages > 1 && (
            <div className="mt-12 flex justify-center">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious 
                      href="#"
                      onClick={(e) => {
                        e.preventDefault()
                        if (currentPage > 1) {
                          handlePageChange(currentPage - 1)
                        }
                      }}
                      className={currentPage === 1 ? "pointer-events-none opacity-50" : ""}
                    />
                  </PaginationItem>
                  
                  {/* Generate page numbers */}
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    // Show first page, last page, current page, and pages around current page
                    const showPage = 
                      page === 1 || 
                      page === totalPages || 
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    
                    if (!showPage) {
                      // Show ellipsis for gaps
                      if (page === currentPage - 2 || page === currentPage + 2) {
                        return (
                          <PaginationItem key={page}>
                            <PaginationEllipsis />
                          </PaginationItem>
                        )
                      }
                      return null
                    }
                    
                    return (
                      <PaginationItem key={page}>
                        <PaginationLink
                          href="#"
                          onClick={(e) => {
                            e.preventDefault()
                            handlePageChange(page)
                          }}
                          isActive={currentPage === page}
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    )
                  })}
                  
                  <PaginationItem>
                    <PaginationNext 
                      href="#"
                      onClick={(e) => {
                        e.preventDefault()
                        if (currentPage < totalPages) {
                          handlePageChange(currentPage + 1)
                        }
                      }}
                      className={currentPage === totalPages ? "pointer-events-none opacity-50" : ""}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}

          {/* No Results */}
          {filteredArticles.length === 0 && (
            <div className="text-center py-12">
              <div className="text-muted-foreground mb-4">
                <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">No articles found</h3>
                <p>Try adjusting your search terms or filters</p>
              </div>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("")
                  setSelectedTopic("All")
                  setFilteredArticles(articles)
                }}
              >
                Clear Filters
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
