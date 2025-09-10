CREATE TABLE "congress_bills" (
	"id" serial PRIMARY KEY NOT NULL,
	"bill_id" varchar(100) NOT NULL,
	"title" text NOT NULL,
	"url" varchar(512),
	"latest_action_date" varchar(50),
	"latest_action_text" text,
	"congress" integer,
	"bill_type" varchar(20),
	"bill_number" integer,
	"embedding" vector(384) NOT NULL,
	CONSTRAINT "congress_bills_bill_id_unique" UNIQUE("bill_id")
);
--> statement-breakpoint
ALTER TABLE "podcasts" ALTER COLUMN "date" SET DEFAULT '2025-08-27 18:41:46.101';--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "auth_user_id" text;--> statement-breakpoint
ALTER TABLE "users" ADD CONSTRAINT "users_auth_user_id_unique" UNIQUE("auth_user_id");