ALTER TABLE "clusters" RENAME TO "articles";--> statement-breakpoint
ALTER TABLE "articles" RENAME COLUMN "metadata" TO "key";--> statement-breakpoint
ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-06-30 02:51:22.707';--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "title" varchar(255);--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "content" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "summary" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "people" jsonb DEFAULT '[]'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "duration" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "topics" jsonb DEFAULT '[]'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "tags" jsonb DEFAULT '[]'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "articles" ADD COLUMN "created_at" timestamp NOT NULL;