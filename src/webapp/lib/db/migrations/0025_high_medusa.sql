CREATE TABLE "clusters" (
	"id" serial PRIMARY KEY NOT NULL,
	"embedding" vector(1536),
	"metadata" jsonb NOT NULL
);