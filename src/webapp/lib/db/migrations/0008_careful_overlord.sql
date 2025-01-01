ALTER TABLE "users" ALTER COLUMN "active" SET DEFAULT false;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "verified" boolean DEFAULT false NOT NULL;