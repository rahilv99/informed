"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Bookmark, Clock, Calendar, ExternalLink, Twitter, Facebook, LinkIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { toast } from "@/hooks/use-toast"

export default function ArticlePage({article, related}: {
    article: {
    id: number
    title: string
    summary: string
    content: string
    people: string[]
    topics: string[]
    tags: string[]
    date: string
    duration: number
    featured: boolean
    sources: { type: string; title: string; url: string; source: string }[]
  },
  related: Array<{
    id: number
    title: string
    summary: string
    topics: string[]
    duration: number
  }>
}) {

  const router = useRouter()
  const [readingProgress, setReadingProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = (window.scrollY / totalHeight) * 100
      setReadingProgress(Math.min(progress, 100))
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  if (!article) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Article Not Found</h1>
          <Button onClick={() => router.push("/articles")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Articles
          </Button>
        </div>
      </div>
    )
  }

  const handleShare = (platform: string) => {
    const url = window.location.href
    const title = article.title

    let shareUrl = ""
    switch (platform) {
      case "twitter":
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`
        break
      case "facebook":
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`
        break
      case "email":
        shareUrl = `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${title}\n${url}`)}`
        break
      case "copy":
        navigator.clipboard.writeText(url)
        toast({ title: "Link copied to clipboard!" })
        return
    }

    if (shareUrl) {
      window.open(shareUrl, "_blank")
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    })
  }

  return (
    <div className="min-h-screen">
      {/* Reading Progress Bar */}
      <div
        className="fixed top-0 left-0 h-1 bg-primary z-50 transition-all duration-150"
        style={{ width: `${readingProgress}%` }}
      />

      {/* Navigation */}
      <nav className="sticky top-0 backdrop-blur border-b z-40">
        <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={() => router.push("/feed")} className="flex items-center">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Articles
            </Button>

            <div className="flex items-center space-x-2">

              <div className="flex items-center space-x-1">
              <Button variant="ghost" size="sm" onClick={() => handleShare("twitter")}>
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => handleShare("facebook")}>
                <Facebook className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => handleShare("email")}>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <path d="M3 7l9 6 9-6" />
                </svg>
              </Button>
              <Button variant="ghost" size="sm" onClick={() => handleShare("copy")}>
                <LinkIcon className="h-4 w-4" />
              </Button>
              </div>
            </div>
            </div>
        </div>
      </nav>

      {/* Article Content */}
      <article className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Article Header */}
        <header className="mb-8">
          <div className="flex items-center space-x-2 mb-4">
            {article.featured && <Badge className="bg-primary text-primary-foreground">Featured</Badge>}
          </div>

          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">{article.title}</h1>

          <p className="text-xl text-muted-foreground leading-relaxed mb-6">{article.summary}</p>

          {/* Topics */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Topics covered:</h3>
            <div className="flex flex-wrap gap-2">
              {article.topics.map((topic, topicIndex) => (
                <Badge key={topicIndex} variant="outline" className="text-sm bg-primary/10 text-primary border-primary/20 px-3 py-1">
                  {topic}
                </Badge>
              ))}
            </div>
          </div>

          {/* Article Meta */}
          <div className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground mb-8">

            <div className="flex items-center space-x-1">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(article.date)}</span>
            </div>

            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>{article.duration} mins read</span>
            </div>

            <div className="flex items-center space-x-3 ml-auto">
              <div className="flex -space-x-2">
                {article.people.slice(0, 3).map((person, personIndex) => (
                  <Avatar key={personIndex} className="h-10 w-10 border-2 border-background">
                    <AvatarImage alt={person} />
                    <AvatarFallback>
                      {person
                        .split(" ")
                        .map((n: string) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                ))}
                {article.people.length > 3 && (
                  <div className="h-10 w-10 rounded-full bg-muted border-2 border-background flex items-center justify-center text-sm font-medium">
                    +{article.people.length - 3}
                  </div>
                )}
              </div>
              <div className="text-sm">
                <p className="font-medium">
                  {article.people.join(", ")}
                </p>
                {article.people.length > 0 && (
                  <p className="text-xs text-muted-foreground">People mentioned in this article</p>
                )}
              </div>
            </div>
          </div>

        </header>

        {/* Article Body */}
        <div className="prose prose-lg max-w-none mb-12">
          <div
            dangerouslySetInnerHTML={{ __html: article.content }}
            className="leading-relaxed text-foreground [&>p]:mb-6 [&>p]:text-base [&>p]:leading-7 [&>ul]:list-disc [&>ul]:pl-6 [&>ul]:mb-6 [&>ul>li]:mb-2 [&>ol]:list-decimal [&>ol]:pl-6 [&>ol]:mb-6 [&>ol>li]:mb-2"
          />
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-8">
          {article.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        <Separator className="my-8" />

        {/* Sources Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Sources</h2>

          {/* Primary Sources */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <div className="w-2 h-2 bg-muted-foreground rounded-full mr-2" />
              Primary Sources
            </h3>
            <div className="space-y-3">
              {article.sources.filter(source => source.type === "primary").map((source, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-400 bg-opacity-10 rounded-lg">
                  <ExternalLink className="h-4 w-4 mt-1 text-muted-foreground flex-shrink-0" />
                  <div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-primary hover:underline"
                    >
                      {source.title}
                    </a>
                    <p className="text-sm text-muted-foreground">{source.source}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Secondary Sources */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <div className="w-2 h-2 bg-muted-foreground rounded-full mr-2" />
              Secondary Sources
            </h3>
            <div className="space-y-3">
              {article.sources.filter(source => source.type === "news").map((source, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-400 bg-opacity-10 rounded-lg">
                  <ExternalLink className="h-4 w-4 mt-1 text-muted-foreground flex-shrink-0" />
                  <div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-foreground hover:text-primary hover:underline"
                    >
                      {source.title}
                    </a>
                    <p className="text-sm text-muted-foreground">{source.source}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <Separator className="my-8" />

        {/* Related Articles */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Related Articles</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {related.map((relatedArticle) => (
              <Card 
              onClick={() => {
                // Navigate to article detail page (replace with actual navigation logic)
                router.push(`/article/${relatedArticle.id}`)
                console.log(`Navigating to article ${relatedArticle.id}`)
              }}
              key={relatedArticle.id} 
              className="group hover:shadow-lg transition-shadow cursor-pointer bg-black bg-opacity-20">
                <CardContent className="p-0">
                  <div className="p-4">
                    {relatedArticle.topics.map((topic, topicIndex) => (
                      <Badge key={topicIndex} variant="secondary" className="mb-2 text-xs mr-2">
                        {topic}
                      </Badge>
                    ))}
                    <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
                      {relatedArticle.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{relatedArticle.summary}</p>
                    <div className="flex items-center text-xs text-muted-foreground">
                      <Clock className="h-3 w-3 mr-1" />
                      {relatedArticle.duration} mins read
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </article>
    </div>
  )
}
