import HomePage from "./landing";
import { getTop3Articles } from "@/lib/db/queries";

export default async function Page() {

  const topArticles = await getTop3Articles();

  const formattedTopArticles = topArticles.map(article => ({
    id: String(article.id),
    title: String(article.title),
    summary: String(article.summary),
    topics: Array.isArray(article.topics) ? article.topics.map(topic => String(topic)) : []
  }));

  return (
    <div>
      <HomePage articles = {formattedTopArticles} />
    </div>
  );
}
