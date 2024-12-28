CREATE TABLE IF NOT EXISTS "emails" (
	"id" serial PRIMARY KEY NOT NULL,
	"email" varchar(255) NOT NULL,
	"subscribed" boolean DEFAULT true NOT NULL,
	CONSTRAINT "emails_email_unique" UNIQUE("email")
);
