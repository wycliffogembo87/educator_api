SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: exam; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exam (
    id uuid NOT NULL,
    name text NOT NULL,
    video_tutorial_name text NOT NULL,
    time_duration integer NOT NULL,
    is_active boolean NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: grade; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grade (
    id uuid NOT NULL,
    starting_percentage integer NOT NULL,
    ending_percentage integer NOT NULL,
    letter_grade text NOT NULL,
    four_point_zero_grade double precision NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: mentorship; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mentorship (
    id uuid NOT NULL,
    tutor uuid NOT NULL,
    challenge_being_faced text NOT NULL,
    is_active boolean NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notification (
    id uuid NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: participant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.participant (
    id uuid NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    exam uuid NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: performance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.performance (
    id uuid NOT NULL,
    ticks integer NOT NULL,
    crosses integer NOT NULL,
    unmarked integer NOT NULL,
    marks_obtained integer NOT NULL,
    total_marks integer NOT NULL,
    total_number_of_questions integer NOT NULL,
    percentage integer NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    grade uuid NOT NULL,
    exam uuid NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: question; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.question (
    id uuid NOT NULL,
    number integer,
    text text NOT NULL,
    multi_choice text[] NOT NULL,
    marks integer NOT NULL,
    answer text NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    exam uuid NOT NULL
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(255) NOT NULL
);


--
-- Name: submission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submission (
    id uuid NOT NULL,
    answer text NOT NULL,
    mark character varying(30) NOT NULL,
    marks_obtained integer NOT NULL,
    comment text NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    question uuid NOT NULL,
    "user" uuid NOT NULL
);


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id uuid NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    phone_number text NOT NULL,
    phone_number_verified boolean NOT NULL,
    email text NOT NULL,
    email_verified boolean NOT NULL,
    role character varying(30) NOT NULL,
    status character varying(30) NOT NULL,
    level integer NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: exam exam_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_name_key UNIQUE (name);


--
-- Name: exam exam_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_pkey PRIMARY KEY (id);


--
-- Name: grade grade_ending_percentage_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_ending_percentage_key UNIQUE (ending_percentage);


--
-- Name: grade grade_letter_grade_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_letter_grade_key UNIQUE (letter_grade);


--
-- Name: grade grade_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_pkey PRIMARY KEY (id);


--
-- Name: grade grade_starting_percentage_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grade
    ADD CONSTRAINT grade_starting_percentage_key UNIQUE (starting_percentage);


--
-- Name: mentorship mentorship_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mentorship
    ADD CONSTRAINT mentorship_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: participant participant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT participant_pkey PRIMARY KEY (id);


--
-- Name: performance performance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_pkey PRIMARY KEY (id);


--
-- Name: question question_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.question
    ADD CONSTRAINT question_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: submission submission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission
    ADD CONSTRAINT submission_pkey PRIMARY KEY (id);


--
-- Name: participant unq_participant__user_exam; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT unq_participant__user_exam UNIQUE ("user", exam);


--
-- Name: performance unq_performance__user_exam; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT unq_performance__user_exam UNIQUE ("user", exam);


--
-- Name: question unq_question__exam_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.question
    ADD CONSTRAINT unq_question__exam_number UNIQUE (exam, number);


--
-- Name: submission unq_submission__user_question; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission
    ADD CONSTRAINT unq_submission__user_question UNIQUE ("user", question);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_phone_number_key UNIQUE (phone_number);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: idx_exam__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_exam__created_at ON public.exam USING btree (created_at);


--
-- Name: idx_exam__user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_exam__user ON public.exam USING btree ("user");


--
-- Name: idx_exam__video_tutorial_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_exam__video_tutorial_name ON public.exam USING btree (video_tutorial_name);


--
-- Name: idx_grade__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grade__created_at ON public.grade USING btree (created_at);


--
-- Name: idx_mentorship__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mentorship__created_at ON public.mentorship USING btree (created_at);


--
-- Name: idx_mentorship__tutor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mentorship__tutor ON public.mentorship USING btree (tutor);


--
-- Name: idx_mentorship__user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mentorship__user ON public.mentorship USING btree ("user");


--
-- Name: idx_notification__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notification__created_at ON public.notification USING btree (created_at);


--
-- Name: idx_notification__user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notification__user ON public.notification USING btree ("user");


--
-- Name: idx_participant__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_participant__created_at ON public.participant USING btree (created_at);


--
-- Name: idx_participant__exam; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_participant__exam ON public.participant USING btree (exam);


--
-- Name: idx_performance__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance__created_at ON public.performance USING btree (created_at);


--
-- Name: idx_performance__exam; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance__exam ON public.performance USING btree (exam);


--
-- Name: idx_performance__grade; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance__grade ON public.performance USING btree (grade);


--
-- Name: idx_question__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_question__created_at ON public.question USING btree (created_at);


--
-- Name: idx_question__number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_question__number ON public.question USING btree (number);


--
-- Name: idx_submission__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_submission__created_at ON public.submission USING btree (created_at);


--
-- Name: idx_submission__question; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_submission__question ON public.submission USING btree (question);


--
-- Name: idx_user__created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user__created_at ON public."user" USING btree (created_at);


--
-- Name: exam fk_exam__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT fk_exam__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: mentorship fk_mentorship__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mentorship
    ADD CONSTRAINT fk_mentorship__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: notification fk_notification__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT fk_notification__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: participant fk_participant__exam; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT fk_participant__exam FOREIGN KEY (exam) REFERENCES public.exam(id) ON DELETE CASCADE;


--
-- Name: participant fk_participant__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT fk_participant__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: performance fk_performance__exam; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT fk_performance__exam FOREIGN KEY (exam) REFERENCES public.exam(id) ON DELETE CASCADE;


--
-- Name: performance fk_performance__grade; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT fk_performance__grade FOREIGN KEY (grade) REFERENCES public.grade(id) ON DELETE CASCADE;


--
-- Name: performance fk_performance__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT fk_performance__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: question fk_question__exam; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.question
    ADD CONSTRAINT fk_question__exam FOREIGN KEY (exam) REFERENCES public.exam(id) ON DELETE CASCADE;


--
-- Name: submission fk_submission__question; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission
    ADD CONSTRAINT fk_submission__question FOREIGN KEY (question) REFERENCES public.question(id) ON DELETE CASCADE;


--
-- Name: submission fk_submission__user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission
    ADD CONSTRAINT fk_submission__user FOREIGN KEY ("user") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20200609190732');
