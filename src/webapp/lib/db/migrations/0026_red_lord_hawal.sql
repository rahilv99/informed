ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-05-30 03:32:15.818';--> statement-breakpoint
ALTER TABLE "clusters" ADD COLUMN "score" real DEFAULT 0 NOT NULL;