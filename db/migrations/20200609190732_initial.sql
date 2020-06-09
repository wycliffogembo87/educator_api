-- migrate:up

CREATE TABLE "mentorship" (
  "id" UUID PRIMARY KEY,
  "learner" TEXT NOT NULL,
  "tutor" TEXT NOT NULL,
  "challenge_being_faced" TEXT NOT NULL,
  "is_active" BOOLEAN NOT NULL,
  "metadata" JSONB NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  "updated_at" TIMESTAMP NOT NULL
);

CREATE INDEX "idx_mentorship__created_at" ON "mentorship" ("created_at");

CREATE INDEX "idx_mentorship__learner" ON "mentorship" ("learner");

CREATE INDEX "idx_mentorship__tutor" ON "mentorship" ("tutor");

CREATE TABLE "user" (
  "id" UUID PRIMARY KEY,
  "username" TEXT UNIQUE NOT NULL,
  "password" TEXT NOT NULL,
  "phone_number" TEXT UNIQUE NOT NULL,
  "phone_number_verified" BOOLEAN NOT NULL,
  "email" TEXT UNIQUE NOT NULL,
  "email_verified" BOOLEAN NOT NULL,
  "role" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "level" INTEGER NOT NULL,
  "metadata" JSONB NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  "updated_at" TIMESTAMP NOT NULL
);

CREATE INDEX "idx_user__created_at" ON "user" ("created_at");

CREATE TABLE "exam" (
  "id" UUID PRIMARY KEY,
  "name" TEXT NOT NULL,
  "video_tutorial_name" TEXT NOT NULL,
  "metadata" JSONB NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  "updated_at" TIMESTAMP NOT NULL,
  "user" UUID NOT NULL
);

CREATE INDEX "idx_exam__created_at" ON "exam" ("created_at");

CREATE INDEX "idx_exam__name" ON "exam" ("name");

CREATE INDEX "idx_exam__user" ON "exam" ("user");

CREATE INDEX "idx_exam__video_tutorial_name" ON "exam" ("video_tutorial_name");

ALTER TABLE "exam" ADD CONSTRAINT "fk_exam__user" FOREIGN KEY ("user") REFERENCES "user" ("id") ON DELETE CASCADE;

CREATE TABLE "notification" (
  "id" UUID PRIMARY KEY,
  "metadata" JSONB NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  "updated_at" TIMESTAMP NOT NULL,
  "user" UUID NOT NULL
);

CREATE INDEX "idx_notification__created_at" ON "notification" ("created_at");

CREATE INDEX "idx_notification__user" ON "notification" ("user");

ALTER TABLE "notification" ADD CONSTRAINT "fk_notification__user" FOREIGN KEY ("user") REFERENCES "user" ("id") ON DELETE CASCADE;

CREATE TABLE "question" (
  "id" UUID PRIMARY KEY,
  "number" INTEGER NOT NULL,
  "text" TEXT NOT NULL,
  "multi_choice" TEXT[] NOT NULL,
  "answer" TEXT NOT NULL,
  "metadata" JSONB NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  "updated_at" TIMESTAMP NOT NULL,
  "exam" UUID NOT NULL
);

CREATE INDEX "idx_question__created_at" ON "question" ("created_at");

CREATE INDEX "idx_question__exam" ON "question" ("exam");

CREATE INDEX "idx_question__number" ON "question" ("number");

ALTER TABLE "question" ADD CONSTRAINT "fk_question__exam" FOREIGN KEY ("exam") REFERENCES "exam" ("id") ON DELETE CASCADE;

-- migrate:down

DROP TABLE "question";
DROP TABLE "exam";
DROP TABLE "mentorship";
DROP TABLE "notification";
DROP TABLE "user";