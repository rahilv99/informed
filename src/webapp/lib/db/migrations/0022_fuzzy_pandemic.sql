ALTER TABLE "podcasts" ALTER COLUMN "audio_file_url" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-04-07 03:21:55.060';--> statement-breakpoint
ALTER TABLE "podcasts" ADD COLUMN "script" jsonb NOT NULL;