export function Toast({ title, description, variant }: { title: string; description: string; variant: "default" | "destructive" }) {
  console.log(`[${variant.toUpperCase()}] ${title}: ${description}`);
}
