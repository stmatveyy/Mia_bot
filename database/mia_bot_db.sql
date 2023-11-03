CREATE TABLE "public.users" (
	"id" serial NOT NULL UNIQUE,
	"name" char(45) NOT NULL,
	"number" integer NOT NULL,
	"group" char(10) NOT NULL,
	"rating" integer NOT NULL,
	CONSTRAINT "users_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.notes" (
	"id" serial NOT NULL UNIQUE,
	"note_text" character NOT NULL,
	"fk_user_note" integer NOT NULL,
	CONSTRAINT "notes_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.schedule_even" (
	"mon" character NOT NULL,
	"tue" character NOT NULL,
	"wen" character NOT NULL,
	"thu" character NOT NULL,
	"fri" character NOT NULL
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.schedule_uneven" (
	"mon" character NOT NULL,
	"tue" character NOT NULL,
	"wen" character NOT NULL,
	"thu" character NOT NULL,
	"fri" character NOT NULL
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.reminders" (
	"id" serial NOT NULL UNIQUE,
	"reminder_text" character NOT NULL,
	"fk_user_reminder" integer NOT NULL,
	"time_stamp" TIMESTAMP NOT NULL,
	CONSTRAINT "reminders_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.group" (
	"id" serial NOT NULL UNIQUE,
	"fk_group_user" serial NOT NULL,
	"mod" bool,
	"pe" bool,
	"faq" bool,
	CONSTRAINT "group_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);




ALTER TABLE "notes" ADD CONSTRAINT "notes_fk0" FOREIGN KEY ("fk_user_note") REFERENCES "users"("id");



ALTER TABLE "reminders" ADD CONSTRAINT "reminders_fk0" FOREIGN KEY ("fk_user_reminder") REFERENCES "users"("id");

ALTER TABLE "group" ADD CONSTRAINT "group_fk0" FOREIGN KEY ("fk_group_user") REFERENCES "users"("id");







