--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO germush;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying NOT NULL,
    parent_id integer
);


ALTER TABLE public.categories OWNER TO germush;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO germush;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    inn character varying(12),
    name character varying(100),
    legal_name character varying(200),
    legal_address character varying(500),
    actual_address character varying(500)
);


ALTER TABLE public.companies OWNER TO germush;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO germush;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: company_item_categories; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.company_item_categories (
    id integer NOT NULL,
    company_item_id integer NOT NULL,
    category_id integer NOT NULL
);


ALTER TABLE public.company_item_categories OWNER TO germush;

--
-- Name: company_item_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.company_item_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_item_categories_id_seq OWNER TO germush;

--
-- Name: company_item_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.company_item_categories_id_seq OWNED BY public.company_item_categories.id;


--
-- Name: company_items; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.company_items (
    id integer NOT NULL,
    company_id integer NOT NULL,
    identifier character varying NOT NULL,
    ean13 character varying,
    name character varying NOT NULL,
    unit_id integer,
    stock integer,
    rrprice double precision,
    microwholeprice double precision,
    mediumwholeprice double precision,
    maxwholeprice double precision
);


ALTER TABLE public.company_items OWNER TO germush;

--
-- Name: company_items_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.company_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_items_id_seq OWNER TO germush;

--
-- Name: company_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.company_items_id_seq OWNED BY public.company_items.id;


--
-- Name: employee_companies; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.employee_companies (
    id integer NOT NULL,
    user_id integer NOT NULL,
    company_id integer NOT NULL
);


ALTER TABLE public.employee_companies OWNER TO germush;

--
-- Name: employee_companies_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.employee_companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_companies_id_seq OWNER TO germush;

--
-- Name: employee_companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.employee_companies_id_seq OWNED BY public.employee_companies.id;


--
-- Name: goods; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.goods (
    name character varying,
    ean13 character varying(13) NOT NULL,
    unit_id integer,
    description character varying(500),
    category character varying(50),
    stock integer DEFAULT 0
);


ALTER TABLE public.goods OWNER TO germush;

--
-- Name: goods_categories; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.goods_categories (
    id integer NOT NULL,
    category_id integer NOT NULL,
    goods_ean13 character varying(13) NOT NULL
);


ALTER TABLE public.goods_categories OWNER TO germush;

--
-- Name: goods_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.goods_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.goods_categories_id_seq OWNER TO germush;

--
-- Name: goods_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.goods_categories_id_seq OWNED BY public.goods_categories.id;


--
-- Name: price_history; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.price_history (
    id integer NOT NULL,
    company_item_id integer NOT NULL,
    price double precision NOT NULL,
    recorded_at timestamp without time zone NOT NULL,
    price_id integer,
    price_type character varying(20) DEFAULT 'unknown'::character varying NOT NULL
);


ALTER TABLE public.price_history OWNER TO germush;

--
-- Name: price_history_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.price_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.price_history_id_seq OWNER TO germush;

--
-- Name: price_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.price_history_id_seq OWNED BY public.price_history.id;


--
-- Name: prices; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.prices (
    id integer NOT NULL,
    goods_ean13 character varying(13) NOT NULL,
    company_id integer NOT NULL,
    price_type character varying(20) NOT NULL,
    price double precision NOT NULL
);


ALTER TABLE public.prices OWNER TO germush;

--
-- Name: prices_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prices_id_seq OWNER TO germush;

--
-- Name: prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.prices_id_seq OWNED BY public.prices.id;


--
-- Name: queries; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.queries (
    id integer NOT NULL,
    user_id integer NOT NULL,
    query_text character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    name character varying(100),
    author character varying(50),
    active boolean
);


ALTER TABLE public.queries OWNER TO germush;

--
-- Name: queries_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.queries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.queries_id_seq OWNER TO germush;

--
-- Name: queries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.queries_id_seq OWNED BY public.queries.id;


--
-- Name: stock_history; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.stock_history (
    id integer NOT NULL,
    company_item_id integer NOT NULL,
    stock integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.stock_history OWNER TO germush;

--
-- Name: stock_history_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.stock_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_history_id_seq OWNER TO germush;

--
-- Name: stock_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.stock_history_id_seq OWNED BY public.stock_history.id;


--
-- Name: units; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.units (
    id integer NOT NULL,
    name character varying(50)
);


ALTER TABLE public.units OWNER TO germush;

--
-- Name: units_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.units_id_seq OWNER TO germush;

--
-- Name: units_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.units_id_seq OWNED BY public.units.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.users (
    id integer NOT NULL,
    login character varying(50),
    password character varying(50),
    role character varying(20) DEFAULT 'retail_client'::character varying
);


ALTER TABLE public.users OWNER TO germush;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO germush;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: germush
--

CREATE TABLE public.warehouses (
    id integer NOT NULL,
    name character varying NOT NULL,
    address character varying NOT NULL
);


ALTER TABLE public.warehouses OWNER TO germush;

--
-- Name: warehouses_id_seq; Type: SEQUENCE; Schema: public; Owner: germush
--

CREATE SEQUENCE public.warehouses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouses_id_seq OWNER TO germush;

--
-- Name: warehouses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: germush
--

ALTER SEQUENCE public.warehouses_id_seq OWNED BY public.warehouses.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: company_item_categories id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_item_categories ALTER COLUMN id SET DEFAULT nextval('public.company_item_categories_id_seq'::regclass);


--
-- Name: company_items id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_items ALTER COLUMN id SET DEFAULT nextval('public.company_items_id_seq'::regclass);


--
-- Name: employee_companies id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.employee_companies ALTER COLUMN id SET DEFAULT nextval('public.employee_companies_id_seq'::regclass);


--
-- Name: goods_categories id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods_categories ALTER COLUMN id SET DEFAULT nextval('public.goods_categories_id_seq'::regclass);


--
-- Name: price_history id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.price_history ALTER COLUMN id SET DEFAULT nextval('public.price_history_id_seq'::regclass);


--
-- Name: prices id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.prices ALTER COLUMN id SET DEFAULT nextval('public.prices_id_seq'::regclass);


--
-- Name: queries id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.queries ALTER COLUMN id SET DEFAULT nextval('public.queries_id_seq'::regclass);


--
-- Name: stock_history id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.stock_history ALTER COLUMN id SET DEFAULT nextval('public.stock_history_id_seq'::regclass);


--
-- Name: units id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.units ALTER COLUMN id SET DEFAULT nextval('public.units_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: warehouses id; Type: DEFAULT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN id SET DEFAULT nextval('public.warehouses_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.alembic_version (version_num) FROM stdin;
24f06da2a916
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.categories (id, name, parent_id) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.companies (id, inn, name, legal_name, legal_address, actual_address) FROM stdin;
1	123456789012	╨Ш╨▓╨░╨╜╨╛╨▓ ╨Ш╨Я	╨Л╨Л╨Л тАЩ╥Р╨▒╨▓┬о╤Ю┬а╨┐	╨К┬о╨▒╨Д╤Ю┬а, ╨│┬л. тА╣╥Р┬н╨Б┬н┬а, 1	╨К┬о╨▒╨Д╤Ю┬а, ╨│┬л. ╨К╨Б╨░┬а, 2
\.


--
-- Data for Name: company_item_categories; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.company_item_categories (id, company_item_id, category_id) FROM stdin;
\.


--
-- Data for Name: company_items; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.company_items (id, company_id, identifier, ean13, name, unit_id, stock, rrprice, microwholeprice, mediumwholeprice, maxwholeprice) FROM stdin;
1	1	10170322	4690636248059	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е120 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (30╤И╤В.) ╨С╨Р╨а╨в╨Х╨а	5	373	131.73	131.73	131.73	131.73
2	1	10000564	4690636166414	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е140 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (30╤И╤В.) 	5	3	134.7	134.7	134.7	134.7
3	1	10170323	4690636248080	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е140 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (30╤И╤В.) ╨С╨Р╨а╨в╨Х╨а	5	212	156.06	156.06	156.06	156.06
4	1	10000565	4690636166438	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е160 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (30╤И╤В.) 	5	71	137.8	137.8	137.8	137.8
5	1	10000566	4690636185545	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е180 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (30╤И╤В.) 	5	69	153.7	153.7	153.7	153.7
6	1	10170325	4690636248103	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е80 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (50╤И╤В.) ╨С╨Р╨а╨в╨Х╨а	5	20	167.49	167.49	167.49	167.49
7	1	10170326	4690636248110	 ╨Ф╤О╨▒╨╡╨╗╤М 10╤Е90 ╨┤╨╗╤П ╨╕╨╖╨╛╨╗. ╨╝╨░╤В. ╤Б ╨┐╨╗╨░╤Б╤В. ╨│╨▓╨╛╨╖╨┤╨╡╨╝ (50╤И╤В.) ╨С╨Р╨а╨в╨Х╨а	5	168	167.55	167.55	167.55	167.55
8	1	10000569	4690636161945	 ╨Ф╤О╨▒╨╡╨╗╤М Tchappai 12╤Е70 1000╨╝╨╗ (40╤И╤В)  (8)	5	9	150.6	150.6	150.6	150.6
9	1	10169613	4610119903640	 ╨Ъ╤Г╨╗╤М╤В╨╕╨▓╨░╤В╨╛╤А "╨У╨░╤А╨┤╨╡╨╜", 37╤Б╨╝ (60/12)	4	24	186.9	186.9	186.9	186.9
10	1	10169612	4610119904296	 ╨б╨╛╨▓╨╛╨║ ╨┐╨╛╤Б╨░╨┤╨╛╤З╨╜╤Л╨╣ "╨У╨░╤А╨┤╨╡╨╜", 31 ╤Б╨╝ (60/12)	4	5	186.9	186.9	186.9	186.9
11	1	10169615	4630058515650	 ╨б╨╛╨▓╨╛╨║ ╨┐╨╛╤Б╨░╨┤╨╛╤З╨╜╤Л╨╣ ╤Г╨╖╨║╨╕╨╣ ╨╖╨╡╨╗╨╡╨╜╨░╤П ╤А╤Г╤З╨║╨░, 27╤Б╨╝  (72/12)	4	1	130.5	130.5	130.5	130.5
13	1	10000718	4690636110097	 ╨в╨░╤А╨╡╨╗╨║╨░ ╨╛╨┐╨╛╤А╨╜╨░╤П Bohrer 125 ╨╝╨╝ (╨║╤А╨╡╨┐╨╗╨╡╨╜╨╕╨╡ ╨╜╨░ ╨╗╨╕╨┐╤Г╤З╨║╨╡) (╨┤╨╗╤П ╨┤╤А╨╡╨╗╨╕) ╨┤╨╗╤П ╨║╤А╤Г╨│╨╛╨▓ ╨░╨▒╤А╨░╨╖╨╕╨▓╨╜╤Л╤Е ╤Б╨░╨╝╨╛╨╖╨░╤Ж╨╡╨┐╨╜╤Л╤Е (100/25/1)	4	1127	241.2	241.2	241.2	241.2
14	1	10000719	4690636110103	 ╨в╨░╤А╨╡╨╗╨║╨░ ╨╛╨┐╨╛╤А╨╜╨░╤П Bohrer 150 ╨╝╨╝ (╨║╤А╨╡╨┐╨╗ ╨╜╨░ ╨╗╨╕╨┐╤Г╤З╨║╨╡ Velcro) (╨┤╨╗╤П ╨г╨и╨Ь ╨Ь14 +╨┐╨╡╤А╨╡╤Е╨╛╨┤╨╜╨╕╨║ ╨╜╨░ ╨┤╤А╨╡╨╗╤М) ╨┤╨╗╤П ╨║╤А╤Г╨│╨╛╨▓ ╨░╨▒╤А ╤Б╨░╨╝╨╛╨╖╨░╤Ж╨╡╨┐ (100/25/1)	4	814	221.9	221.9	221.9	221.9
15	1	10166057	4650199112020	OPPA, ╨У╨╡╤А╨╝╨╡╤В╨╕╨║ ╤Б╨╕╨╗╨╕╨║╨╛╨╜╨╛╨▓╤Л╨╣ ╤Б╨░╨╜╨╕╤В╨░╤А╨╜╤Л╨╣, ╨▒╨╡╨╗╤Л╨╣, 270╨│╤А (260╨╝╨╗)  (1╨║╨╛╤АтАУ24╤И╤В.)	4	30	153	153	153	153
16	1	10168471	4650199112341	OPPA, ╨┐╨╡╨╜╨░ ╨╝╨╛╨╜╤В╨░╨╢╨╜╨░╤П ╨┐╤А╨╛╤Д╨╡╤Б╤Б╨╕╨╛╨╜╨░╨╗╤М╨╜╨░╤П ╨▓╤Б╨╡╤Б╨╡╨╖╨╛╨╜╨╜╨░╤П, 750 ╨╝╨╗/700 ╨│╤А	4	63	412	412	412	412
17	1	10165157	4650199100614	Sila PRO Max Sealant, All weather, ╨║╨░╤Г╤З╤Г╨║╨╛╨▓╤Л╨╣ ╨│╨╡╤А╨╝╨╡╤В╨╕╨║ ╨┤╨╗╤П ╨║╤А╨╛╨▓╨╗╨╕, ╨▒╨╡╤Б╤Ж╨▓╨╡╤В╨╜╤Л╨╣, 290 ╨╝╨╗ (1╤Г╨┐.-12╤И╤В.)	4	6	662	662	662	662
19	1	10009160	4690636179452	╨Р╨┤╨░╨┐╤В╨╡╤А Bohrer 14-30 ╨╝╨╝ ╨┤╨╗╤П ╨║╨╛╤А╨╛╨╜╨╛╨║ ╨▒╨╕╨╝╨╡╤В╨░╨╗╨╗╨╕╤З╨╡╤Б╨║╨╕╤Е (╤Е╨▓╨╛╤Б╤В HEX) (100/10/1)	4	577	154.4	154.4	154.4	154.4
20	1	10009161	4690636179469	╨Р╨┤╨░╨┐╤В╨╡╤А Bohrer 14-30 ╨╝╨╝ ╨┤╨╗╤П ╨║╨╛╤А╨╛╨╜╨╛╨║ ╨▒╨╕╨╝╨╡╤В╨░╨╗╨╗╨╕╤З╨╡╤Б╨║╨╕╤Е (╤Е╨▓╨╛╤Б╤В SDS-PLUS) (100/10/1)	4	1798	213.2	213.2	213.2	213.2
21	1	10009162	4690636179476	╨Р╨┤╨░╨┐╤В╨╡╤А Bohrer 30-82 ╨╝╨╝ ╨┤╨╗╤П ╨║╨╛╤А╨╛╨╜╨╛╨║ ╨▒╨╕╨╝╨╡╤В╨░╨╗╨╗╨╕╤З╨╡╤Б╨║╨╕╤Е (╤Е╨▓╨╛╤Б╤В HEX) (60/10/1)	4	772	378	378	378	378
22	1	10009163	4690636179483	╨Р╨┤╨░╨┐╤В╨╡╤А Bohrer 30-82 ╨╝╨╝ ╨┤╨╗╤П ╨║╨╛╤А╨╛╨╜╨╛╨║ ╨▒╨╕╨╝╨╡╤В╨░╨╗╨╗╨╕╤З╨╡╤Б╨║╨╕╤Е (╤Е╨▓╨╛╤Б╤В SDS-PLUS) (60/10/1)	4	489	378	378	378	378
26	1	10011328	4690636003146	╨Р╨╜╨║╨╡╤А - ╨║╨╗╨╕╨╜ 6╤Е40 (20 ╤И╤В)  	5	50	69	69	69	69
27	1	10011329	4690636003153	╨Р╨╜╨║╨╡╤А - ╨║╨╗╨╕╨╜ 6╤Е60 (10 ╤И╤В)  	5	287	69	69	69	69
40	1	10011392	4690636014920	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь8╤Е10╤Е30 (100), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	10	2932.65	2932.65	2932.65	2932.65
18	1	10008003	4680015601087	ULTIMA, ╨┐╨╡╨╜╨░ ╨╝╨╛╨╜╤В╨░╨╢╨╜╨░╤П ╨▒╤Л╤В╨╛╨▓╨░╤П, 700 ml (600 ╨│╤А.), ╨▓╤Б╨╡╤Б╨╡╨╖╨╛╨╜╨╜╨░╤П (12/1) ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	244010	244010	244010	244010
23	1	10009164	4690636077215	╨Р╨┤╨░╨┐╤В╨╡╤А Bohrer SDS+ ╨┐╨╛╨┤ ╨┐╨░╤В╤А╨╛╨╜ 1/2" x 20 UNF (200/50/1)	6	1	107163	107163	107163	107163
24	1	10009189	4025691982561	╨Р╨┤╨░╨┐╤В╨╡╤А Ritter (╨┐╨╡╤А╨╡╤Е╨╛╨┤╨╜╨╕╨║ ╨┤╨╗╤П ╤Г╤Б╤В╨░╨╜╨╛╨▓╨║╨╕ ╨╜╨░ SDSmax - ╨╛╤Б╨╜╨░╤Б╤В╨║╤Г SDS+) (DreBo, ╨У╨╡╤А╨╝╨░╨╜╨╕╤П)	6	0	1650000	1650000	1650000	1650000
25	1	10009192	4025691081516	╨Р╨┤╨░╨┐╤В╨╡╤А Ritter ╤Б ╤А╨╡╨╖╤М╨▒╨╛╨╣ ╨Ь16 SDS+ ╨┐╨╛╨┤ ╨║╨╛╤А╨╛╨╜╨║╨╕ (╨┤╨╗╨╕╨╜╨░ 370 ╨╝╨╝) (DreBo, ╨У╨╡╤А╨╝╨░╨╜╨╕╤П)	6	0	917985	917985	917985	917985
28	1	10011330	4690636008318	╨Р╨╜╨║╨╡╤А - ╨║╨╗╨╕╨╜ 6╤Е60 (100╤Д), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛ 	6	9	6204.38	6204.38	6204.38	6204.38
29	1	10011367	4690636040493	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-S 10╤Е30 M6 L=95, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	86380.38	86380.38	86380.38	86380.38
30	1	10011368	4690636040486	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-S 10╤Е50 M6 L=115, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	272104.95	272104.95	272104.95	272104.95
31	1	10011370	4690636040462	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-S 12╤Е30 M8 L=107, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	647162.5	647162.5	647162.5	647162.5
32	1	10011371	4690636040455	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-S 12╤Е50 ╨Ь8 L=127, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	828517.04	828517.04	828517.04	828517.04
33	1	10011372	4690636040509	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-SK 10╤Е10 M6 L=70, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	493942.8	493942.8	493942.8	493942.8
34	1	10011373	4690636040479	╨Р╨╜╨║╨╡╤А ╨▓╤Л╤Б╨╛╨║╨╛╨╜╨░╨│╤А╤Г╨╖╨╛╤З╨╜╤Л╨╣ SZ-SK 12╤Е10 M8 L=80, ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	0	417363.24	417363.24	417363.24	417363.24
35	1	10011386	4690636014937	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь10╤Е12╤Е40 (40), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	1	4666.2	4666.2	4666.2	4666.2
36	1	10011387	4690636014944	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь12╤Е16╤Е50 (30), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	6	9908.17	9908.17	9908.17	9908.17
37	1	10011388	4690636014951	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь16╤Е20╤Е65(62) (25), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	9	24403.05	24403.05	24403.05	24403.05
38	1	10011389	4690636014968	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь20╤Е25╤Е80 (10), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	2	75768	75768	75768	75768
39	1	10011390	4690636014913	╨Р╨╜╨║╨╡╤А ╨╖╨░╨▒╨╕╨▓╨░╨╡╨╝╤Л╨╣ ╨Ь6╤Е8╤Е25 (100), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	6	2209.31	2209.31	2209.31	2209.31
41	1	10011403	4690636040943	╨Р╨╜╨║╨╡╤А ╨║╨╗╨╕╨╜╨╛╨▓╨╛╨╣ 10╤Е120 (15), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	12	15279.6	15279.6	15279.6	15279.6
42	1	10011404	4690636038834	╨Р╨╜╨║╨╡╤А ╨║╨╗╨╕╨╜╨╛╨▓╨╛╨╣ 10╤Е130 (15), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	8	16201.5	16201.5	16201.5	16201.5
43	1	10011405	4690636038827	╨Р╨╜╨║╨╡╤А ╨║╨╗╨╕╨╜╨╛╨▓╨╛╨╣ 10╤Е150 (20), ╨┐╨╛╤И╤В╤Г╤З╨╜╨╛	6	2	17929.8	17929.8	17929.8	17929.8
12	1	10000717	4690636110080	 ╨в╨░╤А╨╡╨╗╨║╨░ ╨╛╨┐╨╛╤А╨╜╨░╤П Bohrer 125 ╨╝╨╝ (╨║╤А╨╡╨┐╨╗. ╨╜╨░ ╨╗╨╕╨┐╤Г╤З╨║╨╡ Velcro) (╨┤╨╗╤П ╨г╨и╨Ь ╨Ь14 +╨┐╨╡╤А╨╡╤Е╨╛╨┤╨╜╨╕╨║ ╨╜╨░ ╨┤╤А╨╡╨╗╤М) ╨┤╨╗╤П ╨║╤А╤Г╨│╨╛╨▓ ╨░╨▒╤А. ╤Б╨░╨╝╨╛╨╖╨░╤Ж (100/25/1)	4	3000000	234234	163.8	567	163.8
\.


--
-- Data for Name: employee_companies; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.employee_companies (id, user_id, company_id) FROM stdin;
1	1	1
2	2	1
\.


--
-- Data for Name: goods; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.goods (name, ean13, unit_id, description, category, stock) FROM stdin;
\.


--
-- Data for Name: goods_categories; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.goods_categories (id, category_id, goods_ean13) FROM stdin;
\.


--
-- Data for Name: price_history; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.price_history (id, company_item_id, price, recorded_at, price_id, price_type) FROM stdin;
\.


--
-- Data for Name: prices; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.prices (id, goods_ean13, company_id, price_type, price) FROM stdin;
\.


--
-- Data for Name: queries; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.queries (id, user_id, query_text, created_at, name, author, active) FROM stdin;
\.


--
-- Data for Name: stock_history; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.stock_history (id, company_item_id, stock, created_at) FROM stdin;
\.


--
-- Data for Name: units; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.units (id, name) FROM stdin;
4	╤И╤В.
5	╤Г╨┐.
6	╤В╤Л╤Б. ╤И╤В
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.users (id, login, password, role) FROM stdin;
1	germush	Gremushka27112007	admin
2	petr	yacigan	moderator
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: germush
--

COPY public.warehouses (id, name, address) FROM stdin;
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.companies_id_seq', 1, true);


--
-- Name: company_item_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.company_item_categories_id_seq', 1, false);


--
-- Name: company_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.company_items_id_seq', 43, true);


--
-- Name: employee_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.employee_companies_id_seq', 1, false);


--
-- Name: goods_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.goods_categories_id_seq', 1, false);


--
-- Name: price_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.price_history_id_seq', 1, false);


--
-- Name: prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.prices_id_seq', 1, false);


--
-- Name: queries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.queries_id_seq', 1, false);


--
-- Name: stock_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.stock_history_id_seq', 1, false);


--
-- Name: units_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.units_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: warehouses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: germush
--

SELECT pg_catalog.setval('public.warehouses_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_item_categories company_item_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_item_categories
    ADD CONSTRAINT company_item_categories_pkey PRIMARY KEY (id);


--
-- Name: company_items company_items_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_items
    ADD CONSTRAINT company_items_pkey PRIMARY KEY (id);


--
-- Name: employee_companies employee_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.employee_companies
    ADD CONSTRAINT employee_companies_pkey PRIMARY KEY (id);


--
-- Name: goods_categories goods_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods_categories
    ADD CONSTRAINT goods_categories_pkey PRIMARY KEY (id);


--
-- Name: goods goods_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods
    ADD CONSTRAINT goods_pkey PRIMARY KEY (ean13);


--
-- Name: price_history price_history_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_pkey PRIMARY KEY (id);


--
-- Name: prices prices_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT prices_pkey PRIMARY KEY (id);


--
-- Name: queries queries_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_pkey PRIMARY KEY (id);


--
-- Name: stock_history stock_history_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.stock_history
    ADD CONSTRAINT stock_history_pkey PRIMARY KEY (id);


--
-- Name: units units_name_key; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_name_key UNIQUE (name);


--
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: ix_companies_id; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_companies_id ON public.companies USING btree (id);


--
-- Name: ix_companies_inn; Type: INDEX; Schema: public; Owner: germush
--

CREATE UNIQUE INDEX ix_companies_inn ON public.companies USING btree (inn);


--
-- Name: ix_company_items_id; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_company_items_id ON public.company_items USING btree (id);


--
-- Name: ix_company_items_identifier; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_company_items_identifier ON public.company_items USING btree (identifier);


--
-- Name: ix_goods_ean13; Type: INDEX; Schema: public; Owner: germush
--

CREATE UNIQUE INDEX ix_goods_ean13 ON public.goods USING btree (ean13);


--
-- Name: ix_prices_id; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_prices_id ON public.prices USING btree (id);


--
-- Name: ix_units_id; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_units_id ON public.units USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: germush
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_login; Type: INDEX; Schema: public; Owner: germush
--

CREATE UNIQUE INDEX ix_users_login ON public.users USING btree (login);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(id);


--
-- Name: company_item_categories company_item_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_item_categories
    ADD CONSTRAINT company_item_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: company_item_categories company_item_categories_company_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_item_categories
    ADD CONSTRAINT company_item_categories_company_item_id_fkey FOREIGN KEY (company_item_id) REFERENCES public.company_items(id);


--
-- Name: company_items company_items_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_items
    ADD CONSTRAINT company_items_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: company_items company_items_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.company_items
    ADD CONSTRAINT company_items_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id);


--
-- Name: employee_companies employee_companies_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.employee_companies
    ADD CONSTRAINT employee_companies_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: employee_companies employee_companies_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.employee_companies
    ADD CONSTRAINT employee_companies_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: goods_categories goods_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods_categories
    ADD CONSTRAINT goods_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: goods_categories goods_categories_goods_ean13_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods_categories
    ADD CONSTRAINT goods_categories_goods_ean13_fkey FOREIGN KEY (goods_ean13) REFERENCES public.goods(ean13);


--
-- Name: goods goods_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.goods
    ADD CONSTRAINT goods_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id);


--
-- Name: price_history price_history_company_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_company_item_id_fkey FOREIGN KEY (company_item_id) REFERENCES public.company_items(id);


--
-- Name: price_history price_history_price_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_price_id_fkey FOREIGN KEY (price_id) REFERENCES public.prices(id);


--
-- Name: prices prices_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT prices_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: prices prices_goods_ean13_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT prices_goods_ean13_fkey FOREIGN KEY (goods_ean13) REFERENCES public.goods(ean13);


--
-- Name: queries queries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stock_history stock_history_company_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: germush
--

ALTER TABLE ONLY public.stock_history
    ADD CONSTRAINT stock_history_company_item_id_fkey FOREIGN KEY (company_item_id) REFERENCES public.company_items(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO germush;


--
-- PostgreSQL database dump complete
--

