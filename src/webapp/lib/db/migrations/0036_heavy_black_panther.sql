ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-07-17 02:45:53.271';--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "embedding" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "users" ALTER COLUMN "embedding" DROP NOT NULL;