--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2026-04-28 20:41:19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 24591)
-- Name: atendimentos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atendimentos (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    status character varying(20) DEFAULT 'em_andamento'::character varying,
    data_inicio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    data_fim timestamp without time zone,
    transferido_para character varying(100)
);


ALTER TABLE public.atendimentos OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24590)
-- Name: atendimentos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.atendimentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.atendimentos_id_seq OWNER TO postgres;

--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 219
-- Name: atendimentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.atendimentos_id_seq OWNED BY public.atendimentos.id;


--
-- TOC entry 222 (class 1259 OID 24605)
-- Name: mensagens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mensagens (
    id integer NOT NULL,
    atendimento_id integer NOT NULL,
    remetente character varying(10) NOT NULL,
    conteudo text NOT NULL,
    data_envio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT mensagens_remetente_check CHECK (((remetente)::text = ANY ((ARRAY['usuario'::character varying, 'bot'::character varying])::text[])))
);


ALTER TABLE public.mensagens OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24604)
-- Name: mensagens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mensagens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mensagens_id_seq OWNER TO postgres;

--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 221
-- Name: mensagens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mensagens_id_seq OWNED BY public.mensagens.id;


--
-- TOC entry 218 (class 1259 OID 24581)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    username character varying(100),
    nome character varying(200),
    data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 24580)
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- TOC entry 4928 (class 0 OID 0)
-- Dependencies: 217
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- TOC entry 4754 (class 2604 OID 24594)
-- Name: atendimentos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atendimentos ALTER COLUMN id SET DEFAULT nextval('public.atendimentos_id_seq'::regclass);


--
-- TOC entry 4757 (class 2604 OID 24608)
-- Name: mensagens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensagens ALTER COLUMN id SET DEFAULT nextval('public.mensagens_id_seq'::regclass);


--
-- TOC entry 4752 (class 2604 OID 24584)
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- TOC entry 4918 (class 0 OID 24591)
-- Dependencies: 220
-- Data for Name: atendimentos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.atendimentos (id, usuario_id, status, data_inicio, data_fim, transferido_para) FROM stdin;
1	1	em_andamento	2026-04-28 20:26:56.167742	\N	\N
\.


--
-- TOC entry 4920 (class 0 OID 24605)
-- Dependencies: 222
-- Data for Name: mensagens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mensagens (id, atendimento_id, remetente, conteudo, data_envio) FROM stdin;
1	1	usuario	Explique em uma frase o que é um contrato de honorários advocatícios.	2026-04-28 20:27:01.91504
2	1	bot	É o acordo formal entre cliente e advogado que define os honorários e as condições de pagamento pelos serviços jurídicos prestados.	2026-04-28 20:27:01.917545
\.


--
-- TOC entry 4916 (class 0 OID 24581)
-- Dependencies: 218
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, telegram_id, username, nome, data_criacao) FROM stdin;
1	123456789	cliente_teste	Maria Silva	2026-04-28 20:26:56.15202
\.


--
-- TOC entry 4929 (class 0 OID 0)
-- Dependencies: 219
-- Name: atendimentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.atendimentos_id_seq', 1, true);


--
-- TOC entry 4930 (class 0 OID 0)
-- Dependencies: 221
-- Name: mensagens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mensagens_id_seq', 2, true);


--
-- TOC entry 4931 (class 0 OID 0)
-- Dependencies: 217
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);


--
-- TOC entry 4765 (class 2606 OID 24598)
-- Name: atendimentos atendimentos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atendimentos
    ADD CONSTRAINT atendimentos_pkey PRIMARY KEY (id);


--
-- TOC entry 4767 (class 2606 OID 24614)
-- Name: mensagens mensagens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensagens
    ADD CONSTRAINT mensagens_pkey PRIMARY KEY (id);


--
-- TOC entry 4761 (class 2606 OID 24587)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 4763 (class 2606 OID 24589)
-- Name: usuarios usuarios_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_telegram_id_key UNIQUE (telegram_id);


--
-- TOC entry 4768 (class 2606 OID 24599)
-- Name: atendimentos atendimentos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atendimentos
    ADD CONSTRAINT atendimentos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- TOC entry 4769 (class 2606 OID 24615)
-- Name: mensagens mensagens_atendimento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mensagens
    ADD CONSTRAINT mensagens_atendimento_id_fkey FOREIGN KEY (atendimento_id) REFERENCES public.atendimentos(id);


-- Completed on 2026-04-28 20:41:19

--
-- PostgreSQL database dump complete
--

