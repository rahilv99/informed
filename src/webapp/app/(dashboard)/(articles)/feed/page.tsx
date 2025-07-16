import { getAllArticles } from "@/lib/actions";
import { getUser } from "@/lib/db/queries";
import ArticlesPage from "./content";


export default async function Page() {

  const user = await getUser();
  let feedIndex;

  if (!user) {
    feedIndex = null;
  } else {
    feedIndex = user.feedIndex;
  }

  const articles = await getAllArticles();

  let formattedArticles;

  if (!articles || articles.length === 0) {
     formattedArticles = [
      {
        id: 1,
        title: "The Future of Sustainable Technology in Urban Development",
        summary:
          "Exploring how green technology is reshaping our cities and creating more sustainable living environments for future generations.",
        people: ["Sarah Chen", "Dr. Michael Green", "Lisa Wang"],
        topics: ["Sustainable Technology", "Urban Development", "Green Infrastructure"],
        tags: ["Sustainability", "Urban Planning", "Green Tech", "Smart Cities"],
        date: "2024-01-15",
        duration: 5,
        featured: true,
      },
      {
        id: 2,
        title: "Global Economic Trends: What to Expect in 2024",
        summary:
          "An in-depth analysis of emerging economic patterns and their potential impact on global markets and consumer behavior.",
        people: ["Michael Rodriguez", "Janet Yellen", "Christine Lagarde"],
        topics: ["Economic Trends", "Global Markets", "Consumer Behavior"],
        tags: ["Economics", "Markets", "Finance", "Global Trade"],
        date: "2024-01-14",
        duration: 8,
        featured: false,
      },
      {
        id: 3,
        title: "Climate Change Adaptation Strategies for Coastal Cities",
        summary:
          "How coastal communities are implementing innovative solutions to combat rising sea levels and extreme weather events.",
        people: ["Dr. Emma Thompson", "Mayor Sarah Jones", "Prof. David Kim"],
        topics: ["Climate Change", "Coastal Cities", "Adaptation Strategies"],
        tags: ["Climate", "Environment", "Coastal Management", "Resilience"],
        date: "2024-01-13",
        duration: 6,
        featured: false,
      },
      {
        id: 4,
        title: "The Rise of Remote Work: Reshaping Corporate Culture",
        summary:
          "Examining how distributed teams are changing traditional workplace dynamics and creating new opportunities for collaboration.",
        people: ["James Park", "Susan Martinez", "CEO Robert White"],
        topics: ["Remote Work", "Corporate Culture", "Team Collaboration"],
        tags: ["Remote Work", "Corporate", "Collaboration", "Digital Transformation"],
        date: "2024-01-12",
        duration: 4,
        featured: false,
      },
      {
        id: 5,
        title: "Breakthrough in Renewable Energy Storage Solutions",
        summary:
          "Scientists develop new battery technology that could revolutionize how we store and distribute clean energy at scale.",
        people: ["Dr. Lisa Wang", "Prof. John Smith", "Dr. Maria Gonzalez"],
        topics: ["Renewable Energy", "Energy Storage", "Battery Technology"],
        tags: ["Renewable Energy", "Batteries", "Innovation", "Clean Energy"],
        date: "2024-01-11",
        duration: 7,
        featured: true,
      }
    ]
  } else {
    formattedArticles = articles.map((article) => ({
      id: article.id,
      title: article.title,
      summary: article.summary,
      people: Array.isArray(article.people)
      ? article.people
        .filter((name: string) => name && name.toLowerCase() !== "none")
        .map((name: string) =>
          name
          .toLowerCase()
          .replace(/(^\w{1})|(\s+\w{1})/g, (letter) => letter.toUpperCase())
        )
      : [],
      topics: Array.isArray(article.topics) ? article.topics : [],
      tags: Array.isArray(article.tags) ? article.tags : [],
      date: article.date.toISOString(),
      duration: article.duration,
      featured: article.featured
    }));
  }
  return (
    <div>
      <ArticlesPage articles = {formattedArticles} />
    </div>
  );
}
