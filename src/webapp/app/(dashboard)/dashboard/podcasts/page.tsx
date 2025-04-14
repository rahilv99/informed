import { getKeywords, getAccountStatus } from "@/lib/actions";
import { getUser, fetchUserPodcasts } from "@/lib/db/queries";
import { redirect } from "next/navigation";
import LearningProgress from "./history";
import { toast } from "@/hooks/use-toast"; // Import the toast function


export default async function Page() {
  const currentKeywords: string[] = await getKeywords();
  const isActive: boolean = await getAccountStatus();

  const user = await getUser();
  if (!user) {
    redirect("/sign-in");
  }

  if (!user.verified) {
    redirect("/sign-in");
  }

  if (!isActive && currentKeywords.length === 0) {
    redirect("/identity");
  }

  const userPodcasts = await fetchUserPodcasts(user.id);

  const formattedPodcasts = userPodcasts.map((podcast) => ({
    id: podcast.id,
    title: podcast.title,
    episodeNumber: podcast.episodeNumber,
    date: podcast.date.toISOString(),
    duration: "0:00",
    audioFileUrl: podcast.audioFileUrl ?? "",
    listened: podcast.completed,
    clusters: podcast.articles as { title: string; description: string; gov: string[]; news: string[] }[],
    script: podcast.script as string[],
  }));

  return (
    <div>
      <LearningProgress podcasts={formattedPodcasts} id={user.id} active={isActive} />
    </div>
  );
}
