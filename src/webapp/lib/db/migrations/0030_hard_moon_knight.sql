ALTER TABLE "articles" RENAME COLUMN "created_at" TO "date";--> statement-breakpoint
ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-06-30 02:52:18.841';