import { getAllArticles } from "@/lib/actions";
import { getUser } from "@/lib/db/queries";
import ArticlesPage from "./content";


export default async function Page() {

  const articles = await getAllArticles();
  
  const formattedArticles = articles.map((article) => ({
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
    topics: Array.isArray(article.topics) ? article.topics
    .map((name: string) =>
        name
        .toLowerCase()
        .replace(/(^\w{1})|(\s+\w{1})/g, (letter) => letter.toUpperCase())
      ) : [],
    tags: Array.isArray(article.tags) ? article.tags
    .map((name: string) =>
        name
        .toLowerCase()
        .replace(/(^\w{1})|(\s+\w{1})/g, (letter) => letter.toUpperCase())
      ) : [],
    date: article.date.toISOString(),
    duration: article.duration,
    featured: article.featured
  }));

  return (
    <div>
      <ArticlesPage articles = {formattedArticles} />
    </div>
  );
}
