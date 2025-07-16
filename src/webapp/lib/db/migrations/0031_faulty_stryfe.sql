ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-07-15 01:35:57.570';--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "sources" jsonb DEFAULT '[]'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "featured" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "feed_index" jsonb DEFAULT '[]'::jsonb NOT NULL;