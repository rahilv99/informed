ALTER TABLE "clusters" ALTER COLUMN "embedding" SET DATA TYPE vector(1024);--> statement-breakpoint
ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-05-29 12:38:09.922';