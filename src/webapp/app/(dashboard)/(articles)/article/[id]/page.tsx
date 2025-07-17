import { getArticleById } from "@/lib/actions";
import { getSimilarArticles } from "@/lib/db/queries";
import ArticlePage from "./article";

export default async function Page({ params }: { params: { id: string } }) {

  const { id } = params;
  const ID = parseInt(id, 10)
  const article = await getArticleById(ID);

  let formattedArticle;
  let relatedArticles;

  if (!article) {
    // Mock article data - in real app, this would come from your CMS/database
    formattedArticle = {
        id: 1,
        title: "The Future of Sustainable Technology in Urban Development",
        summary:
          "Exploring how green technology is reshaping our cities and creating more sustainable living environments for future generations.",
        content: `
          <p>Cities around the world are embracing sustainable technology at an unprecedented pace, fundamentally transforming how we think about urban living. From smart energy grids to vertical farming systems, these innovations are not just reducing environmental impact—they're creating more livable, efficient communities.</p>

          <p>The integration of renewable energy sources has become a cornerstone of modern urban planning. Solar panels now adorn rooftops across major metropolitan areas, while wind turbines are being seamlessly incorporated into building designs. Copenhagen leads by example, with plans to become carbon neutral by 2025 through comprehensive green infrastructure.</p>

          <p>Smart building technologies are revolutionizing energy consumption patterns. Advanced sensors monitor everything from lighting to HVAC systems, automatically adjusting to optimize efficiency. These systems can reduce energy consumption by up to 30% while improving occupant comfort and productivity.</p>

          <p>Transportation infrastructure is undergoing a similar transformation. Electric vehicle charging stations are becoming as common as traditional gas stations, while cities like Amsterdam and Copenhagen have created extensive cycling networks that prioritize sustainable mobility.</p>

          <p>The challenge now lies in scaling these solutions globally while ensuring equitable access to green technology benefits across all socioeconomic levels.</p>
        `,
        people: ["Sarah Chen", "Dr. Michael Green", "Lisa Wang", "Prof. Jennifer Martinez"],
        topics: ["Sustainable Technology", "Urban Development", "Green Infrastructure", "Smart Cities"],
        date: "2024-01-15T10:00:00Z",
        duration: 5,
        tags: ["Sustainability", "Urban Planning", "Green Tech", "Smart Cities"],
        featured: true,
        sources: [
            {
              type: "primary",
              title: "Copenhagen Carbon Neutral Plan 2025",
              url: "https://example.com/copenhagen-plan",
              source: "City of Copenhagen",
            },
            {
              type: "primary",
              title: "Smart Building Energy Efficiency Study",
              url: "https://example.com/smart-buildings",
              source: "International Energy Agency",
            },
            {
              type: "news",
              title: "Urban Sustainability Trends Report",
              url: "https://example.com/sustainability-trends",
              source: "World Economic Forum",
            },
            {
              type: "news",
              title: "Green Infrastructure Investment Analysis",
              url: "https://example.com/green-investment",
              source: "McKinsey & Company",
            },
        ]
    } 
    // Mock related articles
    relatedArticles = [
      {
        id: 2,
        title: "Climate Change Adaptation Strategies for Coastal Cities",
        summary: "How coastal communities are implementing innovative solutions to combat rising sea levels.",
        topics: ["Environment"],
        duration: 6
      },
      {
        id: 3,
        title: "Smart Grid Technology: Powering Tomorrow's Cities",
        summary: "The infrastructure revolution that's making renewable energy more reliable and efficient.",
        topics: ["Technology"],
        duration: 4
      },
    ]
  } else {
    formattedArticle = {
      id: article.id,
      title: article.title || "Untitled",
      summary: article.summary,
      content: article.content,
      people: Array.isArray(article.people) ? article.people : [],
      topics: Array.isArray(article.topics) ? article.topics : [],
      tags: Array.isArray(article.tags) ? article.tags : [],
      date: article.date.toISOString(),
      duration: article.duration,
      featured: article.featured,
      sources: Array.isArray(article.sources) ? article.sources.map((source: any) => ({
        type: source.type || "unknown",
        title: source.title || "Untitled",
        url: source.url || "#",
        source: source.source || "Unknown",
      })) : [],
    };

    const rawRelated = await getSimilarArticles(article.embedding);
    relatedArticles = Array.isArray(rawRelated)
      ? rawRelated.map((item: any) => ({
          id: item.id,
          title: item.title,
          summary: item.summary,
          topics: Array.isArray(item.topics) ? item.topics : [],
          duration: item.duration,
        }))
      : [];
  }

  return (
    <div>
      <ArticlePage article = {formattedArticle} related = {relatedArticles} />
    </div>
  );
}
