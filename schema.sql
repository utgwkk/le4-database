--
-- PostgreSQL database dump
--

-- Dumped from database version 10.1
-- Dumped by pg_dump version 10.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.relations DROP CONSTRAINT relations_following_id_fkey;
ALTER TABLE ONLY public.relations DROP CONSTRAINT relations_follower_id_fkey;
ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_user_id_fkey;
ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_user_id_fkey;
ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_post_id_fkey;
ALTER TABLE ONLY public.events DROP CONSTRAINT events_receiver_id_fkey;
ALTER TABLE ONLY public.events DROP CONSTRAINT events_invoker_id_fkey;
ALTER TABLE ONLY public.event_haveread DROP CONSTRAINT event_haveread_user_id_fkey;
ALTER TABLE ONLY public.comments DROP CONSTRAINT comments_user_id_fkey;
ALTER TABLE ONLY public.comments DROP CONSTRAINT comments_post_id_fkey;
CREATE OR REPLACE VIEW public.posts_with_full_info AS
SELECT
    NULL::integer AS id,
    NULL::integer AS user_id,
    NULL::text AS title,
    NULL::text AS description,
    NULL::text AS path,
    NULL::character varying(32) AS username,
    NULL::bigint AS favorites_count;
DROP INDEX public.posts_title;
DROP INDEX public.posts_description;
DROP INDEX public.events_receiver_id;
DROP INDEX public.created_at;
DROP INDEX public.comments_post_id;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
ALTER TABLE ONLY public.relations DROP CONSTRAINT relations_pkey;
ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_pkey;
ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_pkey;
ALTER TABLE ONLY public.events DROP CONSTRAINT events_pkey;
ALTER TABLE ONLY public.event_haveread DROP CONSTRAINT event_haveread_pkey;
ALTER TABLE ONLY public.comments DROP CONSTRAINT comments_pkey;
ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.posts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.events ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.comments ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.users_id_seq;
DROP TABLE public.users;
DROP TABLE public.relations;
DROP SEQUENCE public.posts_id_seq;
DROP MATERIALIZED VIEW public.posts_favorite_ranking;
DROP VIEW public.posts_with_full_info;
DROP TABLE public.posts;
DROP TABLE public.favorites;
DROP SEQUENCE public.events_id_seq;
DROP TABLE public.events;
DROP TABLE public.event_haveread;
DROP SEQUENCE public.comments_id_seq;
DROP TABLE public.comments;
DROP TYPE public.event_type;
DROP EXTENSION pg_bigm;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pg_bigm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_bigm WITH SCHEMA public;


--
-- Name: EXTENSION pg_bigm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_bigm IS 'text similarity measurement and index searching based on bigrams';


SET search_path = public, pg_catalog;

--
-- Name: event_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE event_type AS ENUM (
    'post',
    'favorite',
    'comment',
    'follow'
);


SET default_with_oids = false;

--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE comments (
    id integer NOT NULL,
    post_id integer,
    user_id integer,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE comments_id_seq OWNED BY comments.id;


--
-- Name: event_haveread; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE event_haveread (
    user_id integer NOT NULL,
    since timestamp without time zone DEFAULT now()
);


--
-- Name: events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE events (
    id integer NOT NULL,
    receiver_id integer,
    created_at timestamp without time zone DEFAULT now(),
    type event_type NOT NULL,
    source_id integer NOT NULL,
    invoker_id integer
);


--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE events_id_seq OWNED BY events.id;


--
-- Name: favorites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE favorites (
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE posts (
    id integer NOT NULL,
    user_id integer,
    title text NOT NULL,
    description text NOT NULL,
    path text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: posts_with_full_info; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW posts_with_full_info AS
SELECT
    NULL::integer AS id,
    NULL::integer AS user_id,
    NULL::text AS title,
    NULL::text AS description,
    NULL::text AS path,
    NULL::character varying(32) AS username,
    NULL::bigint AS favorites_count;


--
-- Name: posts_favorite_ranking; Type: MATERIALIZED VIEW; Schema: public; Owner: -
--

CREATE MATERIALIZED VIEW posts_favorite_ranking AS
 SELECT posts_with_full_info.id,
    posts_with_full_info.user_id,
    posts_with_full_info.title,
    posts_with_full_info.description,
    posts_with_full_info.path,
    posts_with_full_info.username,
    posts_with_full_info.favorites_count
   FROM posts_with_full_info
  ORDER BY posts_with_full_info.favorites_count DESC, posts_with_full_info.id
  WITH NO DATA;


--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE posts_id_seq OWNED BY posts.id;


--
-- Name: relations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE relations (
    follower_id integer NOT NULL,
    following_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT relations_check CHECK ((follower_id <> following_id))
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE users (
    id integer NOT NULL,
    username character varying(32) NOT NULL,
    salt character varying(32),
    password character varying(64),
    description text DEFAULT ''::text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT username_pattern CHECK (((username)::text ~ '[a-zA-Z_][0-9a-zA-Z_]{3,31}'::text))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY comments ALTER COLUMN id SET DEFAULT nextval('comments_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY events ALTER COLUMN id SET DEFAULT nextval('events_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY posts ALTER COLUMN id SET DEFAULT nextval('posts_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: event_haveread event_haveread_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY event_haveread
    ADD CONSTRAINT event_haveread_pkey PRIMARY KEY (user_id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (user_id, post_id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: relations relations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT relations_pkey PRIMARY KEY (follower_id, following_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: comments_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_post_id ON comments USING btree (post_id);


--
-- Name: created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX created_at ON favorites USING btree (created_at);


--
-- Name: events_receiver_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX events_receiver_id ON events USING btree (receiver_id);


--
-- Name: posts_description; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posts_description ON posts USING gin (description gin_bigm_ops);


--
-- Name: posts_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posts_title ON posts USING gin (title gin_bigm_ops);


--
-- Name: posts_with_full_info _RETURN; Type: RULE; Schema: public; Owner: -
--

CREATE OR REPLACE VIEW posts_with_full_info AS
 SELECT p.id,
    p.user_id,
    p.title,
    p.description,
    p.path,
    u.username,
    count(f.user_id) AS favorites_count
   FROM ((posts p
     JOIN users u ON ((p.user_id = u.id)))
     LEFT JOIN favorites f ON ((p.id = f.post_id)))
  GROUP BY p.id, u.username
  ORDER BY p.id DESC;


--
-- Name: comments comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: event_haveread event_haveread_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY event_haveread
    ADD CONSTRAINT event_haveread_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: events events_invoker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_invoker_id_fkey FOREIGN KEY (invoker_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: events events_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY events
    ADD CONSTRAINT events_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY favorites
    ADD CONSTRAINT favorites_post_id_fkey FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: relations relations_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT relations_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: relations relations_following_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT relations_following_id_fkey FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

