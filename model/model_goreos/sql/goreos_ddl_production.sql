--
-- PostgreSQL database dump
--

\restrict wnKeXLgaBV9DHH0Ave44DDZHUYKULcYedQbT7LkIj7xG32v4YWyyFAzdUlouLdU

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

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

--
-- Name: core; Type: SCHEMA; Schema: -; Owner: goreos
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO goreos;

--
-- Name: meta; Type: SCHEMA; Schema: -; Owner: goreos
--

CREATE SCHEMA meta;


ALTER SCHEMA meta OWNER TO goreos;

--
-- Name: ref; Type: SCHEMA; Schema: -; Owner: goreos
--

CREATE SCHEMA ref;


ALTER SCHEMA ref OWNER TO goreos;

--
-- Name: txn; Type: SCHEMA; Schema: -; Owner: goreos
--

CREATE SCHEMA txn;


ALTER SCHEMA txn OWNER TO goreos;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: agent_type_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.agent_type_enum AS ENUM (
    'HUMAN',
    'AI',
    'ALGORITHMIC',
    'ORGANIZATIONAL',
    'MACHINE',
    'MIXED'
);


ALTER TYPE public.agent_type_enum OWNER TO goreos;

--
-- Name: cognition_level_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.cognition_level_enum AS ENUM (
    'C0',
    'C1',
    'C2',
    'C3'
);


ALTER TYPE public.cognition_level_enum OWNER TO goreos;

--
-- Name: delegation_mode_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.delegation_mode_enum AS ENUM (
    'M1',
    'M2',
    'M3',
    'M4',
    'M5',
    'M6'
);


ALTER TYPE public.delegation_mode_enum OWNER TO goreos;

--
-- Name: ipr_nature_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.ipr_nature_enum AS ENUM (
    'PROYECTO',
    'PROGRAMA',
    'PROGRAMA_INVERSION',
    'ESTUDIO_BASICO',
    'ANF'
);


ALTER TYPE public.ipr_nature_enum OWNER TO goreos;

--
-- Name: process_layer_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.process_layer_enum AS ENUM (
    'STRATEGIC',
    'TACTICAL',
    'OPERATIONAL'
);


ALTER TYPE public.process_layer_enum OWNER TO goreos;

--
-- Name: story_status_enum; Type: TYPE; Schema: public; Owner: goreos
--

CREATE TYPE public.story_status_enum AS ENUM (
    'DRAFT',
    'ENRICHED',
    'APPROVED',
    'RETIRED'
);


ALTER TYPE public.story_status_enum OWNER TO goreos;

--
-- Name: fn_act_history(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_act_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.administrative_act_history (
            act_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_act_history() OWNER TO goreos;

--
-- Name: fn_agreement_history(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_agreement_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.agreement_history (
            agreement_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_agreement_history() OWNER TO goreos;

--
-- Name: fn_audit_to_event(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_audit_to_event() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_event_type_id UUID;
    v_user_id UUID;
    v_data JSONB;
BEGIN
    -- Obtener event_type según la operación
    SELECT id INTO v_event_type_id
    FROM ref.category
    WHERE scheme = 'event_type' AND code = 'STATE_TRANSITION';

    -- Determinar el usuario actor (del contexto de sesión si existe)
    -- CRIT-005: app.current_user_id es UUID de core.user, consistente con txn.event.actor_id
    v_user_id := current_setting('app.current_user_id', true)::UUID;

    -- Construir datos del evento
    v_data := jsonb_build_object(
        'table', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        'operation', TG_OP
    );

    IF TG_OP = 'UPDATE' THEN
        v_data := v_data || jsonb_build_object(
            'old', to_jsonb(OLD),
            'new', to_jsonb(NEW)
        );
    ELSIF TG_OP = 'INSERT' THEN
        v_data := v_data || jsonb_build_object('new', to_jsonb(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        v_data := v_data || jsonb_build_object('old', to_jsonb(OLD));
    END IF;

    -- Insertar evento (solo si hay event_type)
    IF v_event_type_id IS NOT NULL THEN
        INSERT INTO txn.event (event_type_id, subject_type, subject_id, actor_id, data, created_by_id)
        VALUES (
            v_event_type_id,
            TG_TABLE_NAME,
            COALESCE(NEW.id, OLD.id),
            v_user_id,
            v_data,
            v_user_id
        );
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_audit_to_event() OWNER TO goreos;

--
-- Name: FUNCTION fn_audit_to_event(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_audit_to_event() IS 'Registra cambios en txn.event para tablas críticas (event sourcing)';


--
-- Name: fn_budget_program_current_amount(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_budget_program_current_amount() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- En INSERT: inicializar current_amount = initial_amount si no se especifica
    IF TG_OP = 'INSERT' THEN
        IF NEW.current_amount IS NULL THEN
            NEW.current_amount := NEW.initial_amount;
        END IF;
    END IF;

    -- En UPDATE: si cambia initial_amount y current_amount no fue modificado explícitamente,
    -- ajustar current_amount proporcionalmente
    IF TG_OP = 'UPDATE' THEN
        IF OLD.initial_amount IS DISTINCT FROM NEW.initial_amount THEN
            -- Si current_amount no cambió en este UPDATE, ajustarlo
            IF OLD.current_amount IS NOT DISTINCT FROM NEW.current_amount THEN
                NEW.current_amount := NEW.current_amount + (NEW.initial_amount - OLD.initial_amount);
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_budget_program_current_amount() OWNER TO goreos;

--
-- Name: FUNCTION fn_budget_program_current_amount(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_budget_program_current_amount() IS 'Mantiene current_amount sincronizado con initial_amount. Modificaciones adicionales via txn.magnitude.';


--
-- Name: fn_commitment_history(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_commitment_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.commitment_history (
            commitment_id,
            previous_state_id,
            new_state_id,
            changed_by_id
        ) VALUES (
            NEW.id,
            OLD.state_id,
            NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_commitment_history() OWNER TO goreos;

--
-- Name: FUNCTION fn_commitment_history(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_commitment_history() IS 'Registra cambios de estado en commitment_history';


--
-- Name: fn_ensure_single_primary_party(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_ensure_single_primary_party() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.is_primary = TRUE THEN
        -- Desmarcar otros primarios del mismo rol
        UPDATE core.ipr_party
        SET is_primary = FALSE, updated_at = now()
        WHERE ipr_id = NEW.ipr_id
          AND party_role_id = NEW.party_role_id
          AND id != NEW.id
          AND is_primary = TRUE
          AND deleted_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_ensure_single_primary_party() OWNER TO goreos;

--
-- Name: fn_ensure_single_primary_territory(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_ensure_single_primary_territory() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.is_primary = TRUE THEN
        -- Desmarcar otros primarios
        UPDATE core.ipr_territory
        SET is_primary = FALSE, updated_at = now()
        WHERE ipr_id = NEW.ipr_id
          AND id != NEW.id
          AND is_primary = TRUE
          AND deleted_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_ensure_single_primary_territory() OWNER TO goreos;

--
-- Name: fn_generate_code(character varying, character varying); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_generate_code(p_prefix character varying, p_table_name character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
DECLARE
    v_year INTEGER;
    v_seq INTEGER;
    v_lock_key BIGINT;
BEGIN
    v_year := EXTRACT(YEAR FROM CURRENT_DATE);

    -- HIGH-007 FIX: Generar clave única de lock basada en prefix, tabla y año
    -- hashtext retorna un entero que usamos como lock key
    v_lock_key := hashtext(p_prefix || '|' || p_table_name || '|' || v_year::TEXT);

    -- Adquirir advisory lock de transacción (se libera automáticamente al commit/rollback)
    PERFORM pg_advisory_xact_lock(v_lock_key);

    -- Obtener siguiente secuencia (ahora protegido por lock)
    EXECUTE format('
        SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM ''[0-9]+$'') AS INTEGER)), 0) + 1
        FROM %I
        WHERE code LIKE $1
    ', p_table_name)
    INTO v_seq
    USING p_prefix || '-' || v_year || '-%';

    RETURN p_prefix || '-' || v_year || '-' || LPAD(v_seq::TEXT, 5, '0');
END;
$_$;


ALTER FUNCTION public.fn_generate_code(p_prefix character varying, p_table_name character varying) OWNER TO goreos;

--
-- Name: FUNCTION fn_generate_code(p_prefix character varying, p_table_name character varying); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_generate_code(p_prefix character varying, p_table_name character varying) IS 'Genera código secuencial thread-safe: PREFIX-YYYY-NNNNN (usa advisory lock)';


--
-- Name: fn_rendition_history(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_rendition_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.rendition_history (
            rendition_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_rendition_history() OWNER TO goreos;

--
-- Name: fn_soft_delete(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_soft_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
    v_user_id UUID;
BEGIN
    -- Obtener usuario del contexto
    v_user_id := current_setting('app.current_user_id', true)::UUID;

    -- En lugar de DELETE, marcamos como eliminado
    EXECUTE format('
        UPDATE %I.%I
        SET deleted_at = now(),
            deleted_by_id = $1,
            updated_at = now(),
            updated_by_id = $1
        WHERE id = $2
    ', TG_TABLE_SCHEMA, TG_TABLE_NAME)
    USING v_user_id, OLD.id;

    -- Retornar NULL cancela el DELETE original
    RETURN NULL;
END;
$_$;


ALTER FUNCTION public.fn_soft_delete() OWNER TO goreos;

--
-- Name: FUNCTION fn_soft_delete(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_soft_delete() IS 'Convierte DELETE en soft delete (marca deleted_at en lugar de eliminar)';


--
-- Name: fn_sync_category_parent(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_sync_category_parent() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Si se especifica parent_code, resolver parent_id
    IF NEW.parent_code IS NOT NULL THEN
        SELECT id INTO NEW.parent_id
        FROM ref.category
        WHERE scheme = NEW.scheme
          AND code = NEW.parent_code;

        IF NEW.parent_id IS NULL THEN
            RAISE EXCEPTION 'parent_code "%" no encontrado en scheme "%"', NEW.parent_code, NEW.scheme;
        END IF;
    ELSE
        -- Si no hay parent_code, limpiar parent_id
        NEW.parent_id := NULL;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_sync_category_parent() OWNER TO goreos;

--
-- Name: FUNCTION fn_sync_category_parent(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_sync_category_parent() IS 'STR-001 FIX: Mantiene parent_id sincronizado con parent_code en ref.category';


--
-- Name: fn_update_ipr_problems_flag(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_update_ipr_problems_flag() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Actualizar flag en IPR relacionada
    IF TG_OP = 'DELETE' THEN
        UPDATE core.ipr SET
            has_open_problems = EXISTS (
                SELECT 1 FROM core.ipr_problem
                WHERE ipr_id = OLD.ipr_id
                AND resolved_at IS NULL
                AND deleted_at IS NULL
            ),
            updated_at = now()
        WHERE id = OLD.ipr_id;
        RETURN OLD;
    ELSE
        UPDATE core.ipr SET
            has_open_problems = EXISTS (
                SELECT 1 FROM core.ipr_problem
                WHERE ipr_id = NEW.ipr_id
                AND resolved_at IS NULL
                AND deleted_at IS NULL
            ),
            updated_at = now()
        WHERE id = NEW.ipr_id;
        RETURN NEW;
    END IF;
END;
$$;


ALTER FUNCTION public.fn_update_ipr_problems_flag() OWNER TO goreos;

--
-- Name: FUNCTION fn_update_ipr_problems_flag(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_update_ipr_problems_flag() IS 'Mantiene actualizado has_open_problems en core.ipr';


--
-- Name: fn_update_timestamp(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_update_timestamp() OWNER TO goreos;

--
-- Name: FUNCTION fn_update_timestamp(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_update_timestamp() IS 'Actualiza automaticamente updated_at en UPDATE';


--
-- Name: fn_validate_agreement_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_agreement_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.agreement_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.agreement_type_id, 'agreement_type') THEN
            RAISE EXCEPTION 'agreement_type_id debe pertenecer al scheme "agreement_type"';
        END IF;
    END IF;

    IF NEW.state_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.state_id, 'agreement_state') THEN
            RAISE EXCEPTION 'state_id debe pertenecer al scheme "agreement_state"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_agreement_schemes() OWNER TO goreos;

--
-- Name: fn_validate_category_scheme(uuid, character varying); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_category_scheme(p_category_id uuid, p_expected_scheme character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_actual_scheme VARCHAR(32);
BEGIN
    SELECT scheme INTO v_actual_scheme
    FROM ref.category
    WHERE id = p_category_id;

    IF v_actual_scheme IS NULL THEN
        RETURN FALSE;
    END IF;

    RETURN v_actual_scheme = p_expected_scheme;
END;
$$;


ALTER FUNCTION public.fn_validate_category_scheme(p_category_id uuid, p_expected_scheme character varying) OWNER TO goreos;

--
-- Name: FUNCTION fn_validate_category_scheme(p_category_id uuid, p_expected_scheme character varying); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_validate_category_scheme(p_category_id uuid, p_expected_scheme character varying) IS 'Valida que un category_id pertenece al scheme esperado';


--
-- Name: fn_validate_commitment_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_commitment_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.state_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.state_id, 'commitment_state') THEN
            RAISE EXCEPTION 'state_id debe pertenecer al scheme "commitment_state"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_commitment_schemes() OWNER TO goreos;

--
-- Name: fn_validate_ipr_milestone_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_ipr_milestone_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.milestone_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.milestone_type_id, 'milestone_type') THEN
            RAISE EXCEPTION 'milestone_type_id debe pertenecer al scheme "milestone_type"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_ipr_milestone_schemes() OWNER TO goreos;

--
-- Name: fn_validate_ipr_party_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_ipr_party_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.party_role_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.party_role_id, 'ipr_party_role') THEN
            RAISE EXCEPTION 'party_role_id debe pertenecer al scheme "ipr_party_role"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_ipr_party_schemes() OWNER TO goreos;

--
-- Name: fn_validate_ipr_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_ipr_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- ── Columnas existentes ──

    IF NEW.mcd_phase_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mcd_phase_id, 'mcd_phase') THEN
            RAISE EXCEPTION 'mcd_phase_id debe pertenecer al scheme "mcd_phase"';
        END IF;
    END IF;

    IF NEW.status_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.status_id, 'ipr_state') THEN
            RAISE EXCEPTION 'status_id debe pertenecer al scheme "ipr_state"';
        END IF;
    END IF;

    IF NEW.mechanism_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mechanism_id, 'mechanism') THEN
            RAISE EXCEPTION 'mechanism_id debe pertenecer al scheme "mechanism"';
        END IF;
    END IF;

    IF NEW.budget_subtitle_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.budget_subtitle_id, 'budget_subtitle') THEN
            RAISE EXCEPTION 'budget_subtitle_id debe pertenecer al scheme "budget_subtitle"';
        END IF;
    END IF;

    IF NEW.alert_level_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.alert_level_id, 'alert_level') THEN
            RAISE EXCEPTION 'alert_level_id debe pertenecer al scheme "alert_level"';
        END IF;
    END IF;

    -- ── Columnas añadidas (R-02) ──

    IF NEW.ipr_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.ipr_type_id, 'ipr_type') THEN
            RAISE EXCEPTION 'ipr_type_id debe pertenecer al scheme "ipr_type"';
        END IF;
    END IF;

    IF NEW.funding_source_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.funding_source_id, 'funding_source') THEN
            RAISE EXCEPTION 'funding_source_id debe pertenecer al scheme "funding_source"';
        END IF;
    END IF;

    IF NEW.investment_sector_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.investment_sector_id, 'investment_sector') THEN
            RAISE EXCEPTION 'investment_sector_id debe pertenecer al scheme "investment_sector"';
        END IF;
    END IF;

    IF NEW.fund_category_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.fund_category_id, 'fondo_8pct') THEN
            RAISE EXCEPTION 'fund_category_id debe pertenecer al scheme "fondo_8pct"';
        END IF;
    END IF;

    IF NEW.resolution_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.resolution_type_id, 'resolution_type') THEN
            RAISE EXCEPTION 'resolution_type_id debe pertenecer al scheme "resolution_type"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_ipr_schemes() OWNER TO goreos;

--
-- Name: FUNCTION fn_validate_ipr_schemes(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_validate_ipr_schemes() IS 'R-01/R-02 FIX: Valida 10 FK→ref.category en core.ipr (5 originales + 5 añadidos en migración categorical_univocity)';


--
-- Name: fn_validate_ipr_territory_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_ipr_territory_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.impact_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.impact_type_id, 'territory_impact') THEN
            RAISE EXCEPTION 'impact_type_id debe pertenecer al scheme "territory_impact"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_ipr_territory_schemes() OWNER TO goreos;

--
-- Name: fn_validate_mechanism_attrs(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_mechanism_attrs() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_mechanism_code VARCHAR;
BEGIN
    -- Obtener código del mecanismo desde core.ipr
    SELECT c.code INTO v_mechanism_code
    FROM core.ipr i
    JOIN ref.category c ON i.mechanism_id = c.id
    WHERE i.id = NEW.ipr_id;

    IF v_mechanism_code IS NULL THEN
        RAISE EXCEPTION 'IPR % no tiene mechanism_id asignado', NEW.ipr_id;
    END IF;

    -- Validar atributos requeridos por mecanismo
    CASE v_mechanism_code
        WHEN 'SNI' THEN
            -- SNI requiere: rate_mdsf, etapa_bip
            IF NEW.rate_mdsf IS NULL THEN
                RAISE EXCEPTION 'Mecanismo SNI requiere rate_mdsf (RS, FI, FC, OT)';
            END IF;
            -- Validar valores permitidos de rate
            IF NEW.rate_mdsf NOT IN ('RS', 'FI', 'FC', 'OT') THEN
                RAISE EXCEPTION 'rate_mdsf debe ser RS, FI, FC u OT para SNI';
            END IF;

        WHEN 'C33' THEN
            -- C33 requiere: categoria_c33
            IF NEW.categoria_c33 IS NULL THEN
                RAISE EXCEPTION 'Mecanismo C33 requiere categoria_c33';
            END IF;

        WHEN 'FRIL' THEN
            -- FRIL requiere: tipo_fril, cumple_norma_5k_utm
            IF NEW.tipo_fril IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRIL requiere tipo_fril';
            END IF;
            IF NEW.cumple_norma_5k_utm IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRIL requiere cumple_norma_5k_utm';
            END IF;

        WHEN 'GLOSA06' THEN
            -- Glosa06 requiere: fase_eval_central
            IF NEW.fase_eval_central IS NULL THEN
                RAISE EXCEPTION 'Mecanismo GLOSA06 requiere fase_eval_central';
            END IF;

        WHEN 'TRANSFER' THEN
            -- Transfer: sin atributos obligatorios específicos
            NULL;

        WHEN 'SUBV8' THEN
            -- Subv8 requiere: puntaje_evaluacion
            IF NEW.puntaje_evaluacion IS NULL THEN
                RAISE EXCEPTION 'Mecanismo SUBV8 requiere puntaje_evaluacion';
            END IF;

        WHEN 'FRPD' THEN
            -- FRPD requiere: eje_fomento
            IF NEW.eje_fomento IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRPD requiere eje_fomento';
            END IF;

        ELSE
            RAISE EXCEPTION 'Mecanismo desconocido: %', v_mechanism_code;
    END CASE;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_mechanism_attrs() OWNER TO goreos;

--
-- Name: FUNCTION fn_validate_mechanism_attrs(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_validate_mechanism_attrs() IS 'PRO-001 FIX (Auditoría v5): Valida atributos requeridos según mecanismo de la IPR.
Garantiza coproducto disjunto (SNI, C33, FRIL, GLOSA06, TRANSFER, SUBV8, FRPD).';


--
-- Name: fn_validate_state_transition(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_state_transition() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
    v_col  TEXT := COALESCE(TG_ARGV[0], 'state_id');
    v_old_id UUID;
    v_new_id UUID;
    v_old_code VARCHAR(32);
    v_new_code VARCHAR(32);
    v_valid_transitions JSONB;
BEGIN
    -- Extraer IDs dinámicamente según la columna del trigger
    EXECUTE format('SELECT ($1).%I, ($2).%I', v_col, v_col)
        INTO v_old_id, v_new_id
        USING OLD, NEW;

    -- Si no hay cambio de estado, no validar transición
    IF v_old_id IS NOT DISTINCT FROM v_new_id THEN
        RETURN NEW;
    END IF;

    -- Obtener código del estado anterior
    SELECT code INTO v_old_code
    FROM ref.category WHERE id = v_old_id;

    -- Obtener código del nuevo estado
    SELECT code INTO v_new_code
    FROM ref.category WHERE id = v_new_id;

    -- Obtener transiciones válidas del estado anterior
    SELECT valid_transitions INTO v_valid_transitions
    FROM ref.category WHERE id = v_old_id;

    -- Si hay transiciones definidas, validar (incluye [] como estado terminal)
    IF v_valid_transitions IS NOT NULL THEN
        IF NOT (v_valid_transitions ? v_new_code) THEN
            RAISE EXCEPTION 'Transición de estado inválida: % -> %. Transiciones válidas: %',
                v_old_code, v_new_code, v_valid_transitions;
        END IF;
    END IF;

    RETURN NEW;
END;
$_$;


ALTER FUNCTION public.fn_validate_state_transition() OWNER TO goreos;

--
-- Name: FUNCTION fn_validate_state_transition(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_validate_state_transition() IS 'Valida transiciones de estado usando TG_ARGV[0] como nombre de columna (default: state_id)';


--
-- Name: fn_validate_work_item_schemes(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_validate_work_item_schemes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.status_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.status_id, 'work_item_status') THEN
            RAISE EXCEPTION 'status_id debe pertenecer al scheme "work_item_status"';
        END IF;
    END IF;

    IF NEW.priority_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.priority_id, 'work_item_priority') THEN
            RAISE EXCEPTION 'priority_id debe pertenecer al scheme "work_item_priority"';
        END IF;
    END IF;

    IF NEW.origin_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.origin_id, 'work_item_origin') THEN
            RAISE EXCEPTION 'origin_id debe pertenecer al scheme "work_item_origin"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validate_work_item_schemes() OWNER TO goreos;

--
-- Name: fn_work_item_history(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.fn_work_item_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_event_type_id UUID;
    v_event_code VARCHAR(32);
    v_previous_status_id UUID;
    v_previous_assignee_id UUID;
BEGIN
    -- Determinar tipo de evento
    IF TG_OP = 'INSERT' THEN
        v_event_code := 'CREATED';
        -- En INSERT, OLD no existe, usar NULL para valores previos
        v_previous_status_id := NULL;
        v_previous_assignee_id := NULL;
    ELSE
        -- En UPDATE, OLD existe y podemos usarlo
        v_previous_status_id := OLD.status_id;
        v_previous_assignee_id := OLD.assignee_id;

        IF OLD.status_id IS DISTINCT FROM NEW.status_id THEN
            v_event_code := 'STATUS_CHANGE';
        ELSIF OLD.assignee_id IS DISTINCT FROM NEW.assignee_id THEN
            v_event_code := 'REASSIGNED';
        ELSIF OLD.blocked_by_item_id IS NULL AND NEW.blocked_by_item_id IS NOT NULL THEN
            v_event_code := 'BLOCKED';
        ELSIF OLD.blocked_by_item_id IS NOT NULL AND NEW.blocked_by_item_id IS NULL THEN
            v_event_code := 'UNBLOCKED';
        ELSIF NEW.verified_at IS NOT NULL AND OLD.verified_at IS NULL THEN
            v_event_code := 'VERIFIED';
        ELSE
            -- No registrar si no hay cambio significativo
            RETURN NEW;
        END IF;
    END IF;

    -- Obtener ID del tipo de evento
    SELECT id INTO v_event_type_id
    FROM ref.category
    WHERE scheme = 'work_item_event' AND code = v_event_code;

    IF v_event_type_id IS NOT NULL THEN
        INSERT INTO core.work_item_history (
            work_item_id,
            event_type_id,
            previous_status_id,
            new_status_id,
            previous_assignee_id,
            new_assignee_id,
            performed_by_id
        ) VALUES (
            NEW.id,
            v_event_type_id,
            v_previous_status_id,
            NEW.status_id,
            v_previous_assignee_id,
            NEW.assignee_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_work_item_history() OWNER TO goreos;

--
-- Name: FUNCTION fn_work_item_history(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.fn_work_item_history() IS 'Registra cambios de work_item en work_item_history';


--
-- Name: get_current_user(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.get_current_user() RETURNS uuid
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.get_current_user() OWNER TO goreos;

--
-- Name: FUNCTION get_current_user(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.get_current_user() IS 'Obtiene el usuario actual del contexto de sesión';


--
-- Name: get_current_user_safe(); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.get_current_user_safe() RETURNS uuid
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_user_id_text TEXT;
    v_user_id UUID;
BEGIN
    -- Obtener valor como texto
    v_user_id_text := current_setting('app.current_user_id', true);

    IF v_user_id_text IS NULL OR v_user_id_text = '' THEN
        RETURN NULL;
    END IF;

    -- Intentar convertir a UUID con manejo de error
    BEGIN
        v_user_id := v_user_id_text::UUID;
        RETURN v_user_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'app.current_user_id contiene valor no-UUID: "%". Retornando NULL.', v_user_id_text;
        RETURN NULL;
    END;
END;
$$;


ALTER FUNCTION public.get_current_user_safe() OWNER TO goreos;

--
-- Name: FUNCTION get_current_user_safe(); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.get_current_user_safe() IS 'BEH-002 FIX: Versión defensiva de get_current_user() con validación de formato UUID';


--
-- Name: set_current_user(uuid); Type: FUNCTION; Schema: public; Owner: goreos
--

CREATE FUNCTION public.set_current_user(p_user_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
END;
$$;


ALTER FUNCTION public.set_current_user(p_user_id uuid) OWNER TO goreos;

--
-- Name: FUNCTION set_current_user(p_user_id uuid); Type: COMMENT; Schema: public; Owner: goreos
--

COMMENT ON FUNCTION public.set_current_user(p_user_id uuid) IS 'Establece el usuario actual para auditoría. Llamar al inicio de cada request.';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administrative_act; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.administrative_act (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    act_number character varying(32) NOT NULL,
    act_type_id uuid NOT NULL,
    subject text NOT NULL,
    issuer_id uuid,
    signer_id uuid,
    issued_at timestamp with time zone NOT NULL,
    effective_from timestamp with time zone,
    effective_to timestamp with time zone,
    state_id uuid,
    requires_cgr boolean DEFAULT false,
    cgr_outcome_id uuid,
    cgr_submitted_at date,
    cgr_resolved_at date,
    parent_act_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_act_type_scheme CHECK (((act_type_id IS NULL) OR public.fn_validate_category_scheme(act_type_id, 'act_type'::character varying)))
);


ALTER TABLE core.administrative_act OWNER TO goreos;

--
-- Name: TABLE administrative_act; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.administrative_act IS 'Acto administrativo - manifestacion de voluntad con efectos juridicos';


--
-- Name: administrative_act_history; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.administrative_act_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    act_id uuid NOT NULL,
    previous_state_id uuid,
    new_state_id uuid NOT NULL,
    changed_by_id uuid NOT NULL,
    comment text,
    changed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.administrative_act_history OWNER TO goreos;

--
-- Name: TABLE administrative_act_history; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.administrative_act_history IS 'Historial de cambios de estado de actos administrativos';


--
-- Name: administrative_procedure; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.administrative_procedure (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    procedure_type_id uuid NOT NULL,
    name text NOT NULL,
    state_id uuid,
    initiated_at date NOT NULL,
    resolved_at date,
    initiator_id uuid,
    responsible_id uuid,
    resolution_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.administrative_procedure OWNER TO goreos;

--
-- Name: TABLE administrative_procedure; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.administrative_procedure IS 'Procedimiento administrativo - secuencia de tramites';


--
-- Name: admissibility_check; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.admissibility_check (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    item_id uuid NOT NULL,
    verified_by_id uuid NOT NULL,
    verified_at timestamp with time zone DEFAULT now() NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.admissibility_check OWNER TO goreos;

--
-- Name: admissibility_item; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.admissibility_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    financing_track_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    label text NOT NULL,
    description text,
    responsible_role character varying(50) NOT NULL,
    sort_order integer DEFAULT 0,
    is_required boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE core.admissibility_item OWNER TO goreos;

--
-- Name: agenda_item_context; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.agenda_item_context (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_agreement_id uuid,
    target_type character varying(20) NOT NULL,
    target_id uuid NOT NULL,
    ipr_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.agenda_item_context OWNER TO goreos;

--
-- Name: agreement; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.agreement (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_number character varying(32),
    agreement_type_id uuid,
    state_id uuid,
    ipr_id uuid,
    giver_id uuid,
    receiver_id uuid,
    total_amount numeric(18,2),
    signed_at timestamp with time zone,
    valid_from timestamp with time zone,
    valid_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    technical_referent_id uuid,
    cgr_outcome_id uuid,
    CONSTRAINT chk_agreement_cgr_outcome_scheme CHECK (((cgr_outcome_id IS NULL) OR public.fn_validate_category_scheme(cgr_outcome_id, 'cgr_outcome'::character varying)))
);


ALTER TABLE core.agreement OWNER TO goreos;

--
-- Name: TABLE agreement; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.agreement IS 'Convenio GORE - transferencia, mandato, colaboracion';


--
-- Name: COLUMN agreement.technical_referent_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.agreement.technical_referent_id IS 'gnub:TechnicalReferent, tde:ResponsableAsignado - Persona responsable del seguimiento técnico del convenio. Normalized from metadata.referente_tecnico on 2026-01-30.';


--
-- Name: agreement_history; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.agreement_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid NOT NULL,
    previous_state_id uuid,
    new_state_id uuid NOT NULL,
    changed_by_id uuid NOT NULL,
    comment text,
    changed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.agreement_history OWNER TO goreos;

--
-- Name: agreement_installment; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.agreement_installment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid NOT NULL,
    installment_number integer NOT NULL,
    amount numeric(18,2) NOT NULL,
    due_date date NOT NULL,
    payment_status_id uuid NOT NULL,
    paid_at timestamp with time zone,
    paid_amount numeric(18,2),
    payment_reference character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_paid_lte_amount CHECK (((paid_amount IS NULL) OR (paid_amount <= amount))),
    CONSTRAINT chk_payment_status_scheme CHECK (((payment_status_id IS NULL) OR public.fn_validate_category_scheme(payment_status_id, 'payment_status'::character varying)))
);


ALTER TABLE core.agreement_installment OWNER TO goreos;

--
-- Name: TABLE agreement_installment; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.agreement_installment IS 'Cuota de pago programada de un convenio';


--
-- Name: CONSTRAINT chk_paid_lte_amount ON agreement_installment; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON CONSTRAINT chk_paid_lte_amount ON core.agreement_installment IS 'PRO-002 FIX (Auditoría v5): Garantiza que el monto pagado no exceda el monto de la cuota';


--
-- Name: alert; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.alert (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    alert_type_id uuid NOT NULL,
    severity_id uuid,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    target_type character varying(30),
    target_id uuid,
    message text NOT NULL,
    triggered_at timestamp with time zone DEFAULT now(),
    acknowledged_at timestamp with time zone,
    acknowledged_by_id uuid,
    attended_by_id uuid,
    attended_at timestamp with time zone,
    action_taken text,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_alert_type_scheme CHECK (((alert_type_id IS NULL) OR public.fn_validate_category_scheme(alert_type_id, 'alert_type'::character varying)))
);


ALTER TABLE core.alert OWNER TO goreos;

--
-- Name: TABLE alert; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.alert IS 'Alerta del sistema nervioso digital';


--
-- Name: budget_carryover; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.budget_carryover (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    budget_program_id uuid NOT NULL,
    fiscal_year smallint NOT NULL,
    amount numeric(18,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_amount_positive CHECK ((amount >= (0)::numeric)),
    CONSTRAINT chk_fiscal_year_range CHECK (((fiscal_year >= 2000) AND (fiscal_year <= 2100)))
);


ALTER TABLE core.budget_carryover OWNER TO goreos;

--
-- Name: TABLE budget_carryover; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.budget_carryover IS 'gnub:BudgetCarryover - Arrastres presupuestarios anuales por programa. Modelo time-series para tracking de saldos arrastrados entre ejercicios fiscales.';


--
-- Name: COLUMN budget_carryover.budget_program_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_carryover.budget_program_id IS 'FK al programa presupuestario origen del arrastre';


--
-- Name: COLUMN budget_carryover.fiscal_year; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_carryover.fiscal_year IS 'Anio fiscal destino del arrastre (ej: 2024 = arrastre hacia 2024)';


--
-- Name: COLUMN budget_carryover.amount; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_carryover.amount IS 'Monto arrastrado en CLP';


--
-- Name: budget_commitment; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.budget_commitment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    commitment_number character varying(32) NOT NULL,
    commitment_type_id uuid,
    budget_program_id uuid NOT NULL,
    ipr_id uuid,
    agreement_id uuid,
    amount numeric(18,2) NOT NULL,
    issued_at date NOT NULL,
    expires_at date,
    status_id uuid,
    resolution_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_budget_commit_status_scheme CHECK (((status_id IS NULL) OR public.fn_validate_category_scheme(status_id, 'budget_commitment_status'::character varying))),
    CONSTRAINT chk_budget_commitment_amount CHECK ((amount > (0)::numeric)),
    CONSTRAINT chk_commitment_type_scheme CHECK (((commitment_type_id IS NULL) OR public.fn_validate_category_scheme(commitment_type_id, 'commitment_type'::character varying)))
);


ALTER TABLE core.budget_commitment OWNER TO goreos;

--
-- Name: TABLE budget_commitment; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.budget_commitment IS 'Compromiso presupuestario (CDP, Compromiso, Devengado)';


--
-- Name: budget_cycle_milestone; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.budget_cycle_milestone (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    phase character varying(4) NOT NULL,
    quarter character varying(4),
    ordinal smallint NOT NULL,
    month_label character varying(32) NOT NULL,
    name text NOT NULL,
    responsible text NOT NULL,
    deliverable text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT budget_cycle_milestone_ordinal_check CHECK (((ordinal >= 1) AND (ordinal <= 30))),
    CONSTRAINT budget_cycle_milestone_phase_check CHECK (((phase)::text = ANY ((ARRAY['T-1'::character varying, 'T'::character varying, 'T+1'::character varying])::text[]))),
    CONSTRAINT budget_cycle_milestone_quarter_check CHECK (((quarter)::text = ANY ((ARRAY['Q1'::character varying, 'Q2'::character varying, 'Q3'::character varying, 'Q4'::character varying])::text[])))
);


ALTER TABLE core.budget_cycle_milestone OWNER TO goreos;

--
-- Name: budget_cycle_tracking; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.budget_cycle_tracking (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    milestone_id uuid NOT NULL,
    fiscal_year smallint NOT NULL,
    status character varying(16) DEFAULT 'PENDIENTE'::character varying NOT NULL,
    planned_date date,
    completed_at timestamp with time zone,
    completed_by_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT budget_cycle_tracking_fiscal_year_check CHECK (((fiscal_year >= 2020) AND (fiscal_year <= 2040))),
    CONSTRAINT budget_cycle_tracking_status_check CHECK (((status)::text = ANY ((ARRAY['PENDIENTE'::character varying, 'EN_CURSO'::character varying, 'COMPLETADO'::character varying, 'OMITIDO'::character varying])::text[])))
);


ALTER TABLE core.budget_cycle_tracking OWNER TO goreos;

--
-- Name: budget_program; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.budget_program (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    fiscal_year integer NOT NULL,
    program_type_id uuid,
    subtitle_id uuid,
    initial_amount numeric(18,2) NOT NULL,
    current_amount numeric(18,2),
    committed_amount numeric(18,2) DEFAULT 0,
    accrued_amount numeric(18,2) DEFAULT 0,
    paid_amount numeric(18,2) DEFAULT 0,
    owner_division_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    item_id uuid,
    allocation_id uuid,
    fndr_amount numeric(18,2),
    sectorial_amount numeric(18,2),
    program_code_id uuid,
    CONSTRAINT chk_allocation_scheme CHECK (((allocation_id IS NULL) OR public.fn_validate_category_scheme(allocation_id, 'budget_allocation'::character varying))),
    CONSTRAINT chk_item_scheme CHECK (((item_id IS NULL) OR public.fn_validate_category_scheme(item_id, 'budget_item'::character varying))),
    CONSTRAINT chk_program_code_scheme CHECK (((program_code_id IS NULL) OR public.fn_validate_category_scheme(program_code_id, 'budget_program_code'::character varying))),
    CONSTRAINT chk_program_type_scheme CHECK (((program_type_id IS NULL) OR public.fn_validate_category_scheme(program_type_id, 'program_type'::character varying))),
    CONSTRAINT chk_subtitle_scheme CHECK (((subtitle_id IS NULL) OR public.fn_validate_category_scheme(subtitle_id, 'budget_subtitle'::character varying)))
);


ALTER TABLE core.budget_program OWNER TO goreos;

--
-- Name: TABLE budget_program; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.budget_program IS 'Programa de Presupuesto Publico Regional (PPR)';


--
-- Name: COLUMN budget_program.item_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_program.item_id IS 'gnub:BudgetItem - Item del Clasificador Presupuestario Publico (Ley de Presupuestos Chile). Normalizado desde metadata.item en 2026-01-30.';


--
-- Name: COLUMN budget_program.allocation_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_program.allocation_id IS 'gnub:BudgetAllocation - Asignacion del Clasificador Presupuestario Publico. Normalizado desde metadata.asignacion en 2026-01-30.';


--
-- Name: COLUMN budget_program.fndr_amount; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_program.fndr_amount IS 'Monto FNDR (Fondo Nacional de Desarrollo Regional) asignado al programa. Normalizado desde metadata.monto_fndr en 2026-01-30.';


--
-- Name: COLUMN budget_program.sectorial_amount; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.budget_program.sectorial_amount IS 'Monto de origen sectorial (ministerial) asignado al programa. Normalizado desde metadata.monto_sectorial en 2026-01-30.';


--
-- Name: commitment_history; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.commitment_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    commitment_id uuid NOT NULL,
    previous_state_id uuid,
    new_state_id uuid NOT NULL,
    changed_by_id uuid NOT NULL,
    comment text,
    changed_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_commit_hist_new_scheme CHECK (((new_state_id IS NULL) OR public.fn_validate_category_scheme(new_state_id, 'commitment_state'::character varying))),
    CONSTRAINT chk_commit_hist_prev_scheme CHECK (((previous_state_id IS NULL) OR public.fn_validate_category_scheme(previous_state_id, 'commitment_state'::character varying)))
);


ALTER TABLE core.commitment_history OWNER TO goreos;

--
-- Name: TABLE commitment_history; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.commitment_history IS 'Historial de cambios de estado en compromisos operativos';


--
-- Name: committee; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.committee (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    committee_type_id uuid,
    parent_org_id uuid,
    is_permanent boolean DEFAULT true,
    legal_basis text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_committee_type_scheme CHECK (((committee_type_id IS NULL) OR public.fn_validate_category_scheme(committee_type_id, 'committee_type'::character varying)))
);


ALTER TABLE core.committee OWNER TO goreos;

--
-- Name: TABLE committee; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.committee IS 'Organo colegiado de decision (CORE, Comite Inversiones)';


--
-- Name: committee_member; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.committee_member (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    committee_id uuid NOT NULL,
    person_id uuid,
    role_in_committee_id uuid,
    start_date date NOT NULL,
    end_date date,
    is_voting_member boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    CONSTRAINT chk_role_in_committee_scheme CHECK (((role_in_committee_id IS NULL) OR public.fn_validate_category_scheme(role_in_committee_id, 'role_in_committee'::character varying)))
);


ALTER TABLE core.committee_member OWNER TO goreos;

--
-- Name: TABLE committee_member; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.committee_member IS 'Membresia en comite';


--
-- Name: crisis_meeting; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.crisis_meeting (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    summary text,
    organizer_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.crisis_meeting OWNER TO goreos;

--
-- Name: dgi_bpmn_model; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_bpmn_model (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(30),
    process_name character varying(200) NOT NULL,
    division_id uuid,
    version character varying(10) DEFAULT 'v1.0'::character varying,
    status_id uuid NOT NULL,
    description text,
    file_url text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.dgi_bpmn_model OWNER TO goreos;

--
-- Name: TABLE dgi_bpmn_model; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_bpmn_model IS 'Metadata de modelos BPMN de procesos institucionales';


--
-- Name: dgi_committee_session; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_committee_session (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_date timestamp with time zone NOT NULL,
    status_id uuid NOT NULL,
    agenda jsonb DEFAULT '[]'::jsonb,
    agreements jsonb DEFAULT '[]'::jsonb,
    attendees jsonb DEFAULT '[]'::jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.dgi_committee_session OWNER TO goreos;

--
-- Name: TABLE dgi_committee_session; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_committee_session IS 'Sesiones del Comité de Transformación Digital';


--
-- Name: dgi_data_source_status; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_data_source_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    division_id uuid NOT NULL,
    source_name character varying(100) NOT NULL,
    status_id uuid NOT NULL,
    last_data_at timestamp with time zone,
    days_behind integer DEFAULT 0,
    contact_info text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.dgi_data_source_status OWNER TO goreos;

--
-- Name: TABLE dgi_data_source_status; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_data_source_status IS 'Estado de las fuentes de datos por división';


--
-- Name: dgi_decree; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_decree (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    description text,
    status_id uuid NOT NULL,
    deadline date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_dgi_decree_status CHECK (public.fn_validate_category_scheme(status_id, 'dgi_decree_status'::character varying))
);


ALTER TABLE core.dgi_decree OWNER TO goreos;

--
-- Name: dgi_indicator; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_indicator (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(200) NOT NULL,
    dimension_id uuid NOT NULL,
    description text,
    current_value numeric(10,2),
    target_value numeric(10,2),
    unit character varying(20) DEFAULT '%'::character varying,
    signal_id uuid,
    trend character varying(10),
    division_id uuid,
    source_description text,
    last_updated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT dgi_indicator_trend_check CHECK (((trend)::text = ANY ((ARRAY['up'::character varying, 'down'::character varying, 'flat'::character varying])::text[])))
);


ALTER TABLE core.dgi_indicator OWNER TO goreos;

--
-- Name: TABLE dgi_indicator; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_indicator IS 'Indicadores institucionales del semáforo DGI';


--
-- Name: dgi_indicator_snapshot; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_indicator_snapshot (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    indicator_id uuid NOT NULL,
    value numeric(18,4),
    signal_id uuid,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_dgi_signal_scheme CHECK (((signal_id IS NULL) OR public.fn_validate_category_scheme(signal_id, 'dgi_signal'::character varying)))
);


ALTER TABLE core.dgi_indicator_snapshot OWNER TO goreos;

--
-- Name: dgi_initiative; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_initiative (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20),
    name character varying(200) NOT NULL,
    description text,
    responsible_id uuid NOT NULL,
    status_id uuid NOT NULL,
    dmaic_phase_id uuid,
    division_id uuid,
    start_date date,
    target_date date,
    current_day integer DEFAULT 0,
    total_days integer,
    progress numeric(5,2) DEFAULT 0,
    wip_column character varying(30),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    sort_order integer DEFAULT 0 NOT NULL
);


ALTER TABLE core.dgi_initiative OWNER TO goreos;

--
-- Name: TABLE dgi_initiative; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_initiative IS 'Iniciativas de mejora DGI con tracking Kanban/DMAIC';


--
-- Name: dgi_report; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.dgi_report (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(30),
    report_type_id uuid NOT NULL,
    status_id uuid NOT NULL,
    title character varying(300) NOT NULL,
    period_start date,
    period_end date,
    recipient text,
    content jsonb DEFAULT '{}'::jsonb,
    generated_by_id uuid,
    approved_by_id uuid,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.dgi_report OWNER TO goreos;

--
-- Name: TABLE dgi_report; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.dgi_report IS 'Informes institucionales DGI (Flash, Semanal, Mensual, Temático)';


--
-- Name: digital_platform; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.digital_platform (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    platform_type_id uuid,
    url text,
    owner_id uuid,
    is_external boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.digital_platform OWNER TO goreos;

--
-- Name: TABLE digital_platform; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.digital_platform IS 'Sistema o plataforma digital (SIGFE, BIP, Portal)';


--
-- Name: document; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.document (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(64),
    name text NOT NULL,
    document_type_id uuid,
    file_id uuid,
    ipr_id uuid,
    agreement_id uuid,
    storage_url text,
    sort_order integer,
    folio_number character varying(20),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.document OWNER TO goreos;

--
-- Name: TABLE document; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.document IS 'Documento digital o fisico en el sistema';


--
-- Name: COLUMN document.sort_order; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.document.sort_order IS 'TDE-001: Orden de foliación digital en expediente (Art. 20 DS10)';


--
-- Name: COLUMN document.folio_number; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.document.folio_number IS 'TDE-001: Número de folio asignado al documento';


--
-- Name: electronic_file; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.electronic_file (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    file_number character varying(32) NOT NULL,
    procedure_id uuid,
    requester_id uuid,
    subject text NOT NULL,
    status_id uuid,
    resolved_at timestamp with time zone,
    resolution_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.electronic_file OWNER TO goreos;

--
-- Name: TABLE electronic_file; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.electronic_file IS 'Expediente electronico de un tramite';


--
-- Name: evaluation_assignment; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.evaluation_assignment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    evaluator_type_id uuid NOT NULL,
    evaluator_organization_id uuid,
    evaluator_name character varying(200),
    assigned_at timestamp with time zone DEFAULT now() NOT NULL,
    deadline_at timestamp with time zone,
    completed_at timestamp with time zone,
    result_id uuid,
    result_code character varying(10),
    observations text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    numeric_score numeric(5,2),
    rank_position integer,
    rank_total integer,
    convocatoria_code character varying(32)
);


ALTER TABLE core.evaluation_assignment OWNER TO goreos;

--
-- Name: TABLE evaluation_assignment; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.evaluation_assignment IS 'Asignación de evaluación: quién evalúa un IPR y con qué resultado (Poly-Switch Wave 7)';


--
-- Name: COLUMN evaluation_assignment.numeric_score; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.evaluation_assignment.numeric_score IS 'Numeric evaluation score (0-100). Used by FRPD puntaje_min gate at F2→F3.';


--
-- Name: financial_threshold; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.financial_threshold (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(64) NOT NULL,
    label text NOT NULL,
    value_utm numeric(10,2),
    value_pct numeric(5,2),
    enforcement_point character varying(32) NOT NULL,
    source_normativa text,
    applies_to_track character varying(32),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.financial_threshold OWNER TO goreos;

--
-- Name: TABLE financial_threshold; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.financial_threshold IS 'Umbrales financieros parametrizables (universales + glosa). Administrables sin code change.';


--
-- Name: COLUMN financial_threshold.code; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.code IS 'Identificador unico del umbral (e.g. CORE_APPROVAL, GLOSA_ADMIN_MAX)';


--
-- Name: COLUMN financial_threshold.value_utm; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.value_utm IS 'Valor en UTM (NULL si es porcentual)';


--
-- Name: COLUMN financial_threshold.value_pct; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.value_pct IS 'Valor porcentual (NULL si es UTM)';


--
-- Name: COLUMN financial_threshold.enforcement_point; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.enforcement_point IS 'Punto de aplicacion: F3_F4, F1_F2, ACTO, CONVENIO, GLOSA, CONFIG';


--
-- Name: COLUMN financial_threshold.source_normativa; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.source_normativa IS 'Fuente legal: LOC GORE Art. 36, Ley Presupuestos, etc.';


--
-- Name: COLUMN financial_threshold.applies_to_track; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.financial_threshold.applies_to_track IS 'NULL = universal, codigo track = track-especifico';


--
-- Name: financing_track; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.financing_track (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    label text NOT NULL,
    evaluator_code character varying(32) NOT NULL,
    evaluator_label text NOT NULL,
    favorable_products text[] DEFAULT '{}'::text[] NOT NULL,
    unfavorable_products text[] DEFAULT '{}'::text[] NOT NULL,
    terminal_negative text[] DEFAULT '{}'::text[] NOT NULL,
    thresholds jsonb DEFAULT '{}'::jsonb NOT NULL,
    required_attrs text[] DEFAULT '{}'::text[] NOT NULL,
    sla_days jsonb DEFAULT '{}'::jsonb NOT NULL,
    rs_validity_years integer,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.financing_track OWNER TO goreos;

--
-- Name: fril_category; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.fril_category (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(3) NOT NULL,
    name text NOT NULL,
    group_code character varying(1) NOT NULL,
    group_name text NOT NULL,
    description text,
    examples text,
    max_utm numeric(12,2) DEFAULT 4545 NOT NULL,
    is_exempt_commune_limit boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT fril_category_group_code_check CHECK (((group_code)::text = ANY ((ARRAY['A'::character varying, 'B'::character varying, 'C'::character varying, 'D'::character varying])::text[])))
);


ALTER TABLE core.fril_category OWNER TO goreos;

--
-- Name: TABLE fril_category; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.fril_category IS 'TP-04: FRIL project categories (12 types in 4 groups A-D)';


--
-- Name: fund_program; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.fund_program (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    fund_source_id uuid NOT NULL,
    fiscal_year integer NOT NULL,
    total_amount numeric(18,2) NOT NULL,
    state_id uuid,
    call_open_date date,
    call_close_date date,
    resolution_id uuid,
    budget_program_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.fund_program OWNER TO goreos;

--
-- Name: TABLE fund_program; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.fund_program IS 'Programa especifico financiado por un fondo';


--
-- Name: installment_milestone; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.installment_milestone (
    installment_id uuid NOT NULL,
    milestone_id uuid NOT NULL,
    is_required boolean DEFAULT true,
    notes text
);


ALTER TABLE core.installment_milestone OWNER TO goreos;

--
-- Name: TABLE installment_milestone; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.installment_milestone IS 'OO-008: Relación N:M cuota↔hito siguiendo gnub:triggersPayment';


--
-- Name: COLUMN installment_milestone.is_required; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.installment_milestone.is_required IS 'Si TRUE, el hito es requisito para liberar el pago de la cuota';


--
-- Name: inventory_item; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.inventory_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    item_type_id uuid,
    location_id uuid,
    responsible_id uuid,
    acquisition_date date,
    acquisition_value numeric(18,2),
    current_status_id uuid,
    ipr_origin_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.inventory_item OWNER TO goreos;

--
-- Name: TABLE inventory_item; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.inventory_item IS 'Bien mueble o activo del GORE';


--
-- Name: ipr; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    codigo_bip character varying(20) NOT NULL,
    name text NOT NULL,
    ipr_nature public.ipr_nature_enum NOT NULL,
    ipr_type_id uuid,
    mcd_phase_id uuid,
    status_id uuid,
    budget_subtitle_id uuid,
    funding_source_id uuid,
    mechanism_id uuid,
    crea_activo boolean DEFAULT true,
    formulator_id uuid,
    executor_id uuid,
    sponsor_division_id uuid,
    max_execution_months integer,
    intended_outcome text,
    resolution_type_id uuid,
    requires_cgr boolean DEFAULT false,
    requires_dipres boolean DEFAULT false,
    has_open_problems boolean DEFAULT false,
    alert_level_id uuid,
    assignee_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    investment_sector_id uuid,
    fund_category_id uuid,
    is_municipal_origin boolean DEFAULT false,
    CONSTRAINT chk_budget_subtitle_scheme CHECK (((budget_subtitle_id IS NULL) OR public.fn_validate_category_scheme(budget_subtitle_id, 'budget_subtitle'::character varying))),
    CONSTRAINT chk_fund_category_scheme CHECK (((fund_category_id IS NULL) OR public.fn_validate_category_scheme(fund_category_id, 'fondo_8pct'::character varying))),
    CONSTRAINT chk_funding_source_scheme CHECK (((funding_source_id IS NULL) OR public.fn_validate_category_scheme(funding_source_id, 'funding_source'::character varying))),
    CONSTRAINT chk_investment_sector_scheme CHECK (((investment_sector_id IS NULL) OR public.fn_validate_category_scheme(investment_sector_id, 'investment_sector'::character varying))),
    CONSTRAINT chk_ipr_type_scheme CHECK (((ipr_type_id IS NULL) OR public.fn_validate_category_scheme(ipr_type_id, 'ipr_type'::character varying))),
    CONSTRAINT chk_mcd_phase_scheme CHECK (((mcd_phase_id IS NULL) OR public.fn_validate_category_scheme(mcd_phase_id, 'mcd_phase'::character varying))),
    CONSTRAINT chk_mechanism_scheme CHECK (((mechanism_id IS NULL) OR public.fn_validate_category_scheme(mechanism_id, 'mechanism'::character varying))),
    CONSTRAINT chk_resolution_type_scheme CHECK (((resolution_type_id IS NULL) OR public.fn_validate_category_scheme(resolution_type_id, 'resolution_type'::character varying))),
    CONSTRAINT chk_status_scheme CHECK (((status_id IS NULL) OR public.fn_validate_category_scheme(status_id, 'ipr_state'::character varying)))
);


ALTER TABLE core.ipr OWNER TO goreos;

--
-- Name: TABLE ipr; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr IS 'Iniciativa de Inversion Publica Regional - transformacion territorial';


--
-- Name: COLUMN ipr.ipr_nature; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr.ipr_nature IS 'PROYECTO|PROGRAMA (ENUM)';


--
-- Name: COLUMN ipr.mcd_phase_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr.mcd_phase_id IS 'scheme=mcd_phase: F0|F1|F2|F3|F4|F5 (6 fases MCD)';


--
-- Name: COLUMN ipr.mechanism_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr.mechanism_id IS 'scheme=mechanism: SNI|C33|FRIL|GLOSA06|TRANSFER|SUBV8|FRPD';


--
-- Name: COLUMN ipr.investment_sector_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr.investment_sector_id IS 'gnub:InvestmentTypology - Thematic sector of the investment initiative. Determines applicable Sectoral Information Requirements (RIS). Normalized from metadata.tipologia_original (sectoral codes only) on 2026-01-30.';


--
-- Name: ipr_mechanism; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr_mechanism (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    rate_mdsf character varying(4),
    etapa_bip character varying(16),
    sector character varying(64),
    categoria_c33 character varying(32),
    vida_util_residual integer,
    informe_tecnico_favorable boolean,
    cofinanciamiento_anf numeric(5,2),
    tipo_fril character varying(32),
    cumple_norma_5k_utm boolean,
    res_subdere character varying(32),
    plazo_licitacion_dias integer,
    fase_eval_central character varying(16),
    rate_ses character varying(4),
    gasto_admin_max numeric(5,2),
    eje_fomento character varying(64),
    nivel_trl integer,
    innovacion_ctci boolean,
    fondo_tematico character varying(32),
    puntaje_evaluacion numeric(5,2),
    asignacion_directa boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.ipr_mechanism OWNER TO goreos;

--
-- Name: TABLE ipr_mechanism; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr_mechanism IS 'Atributos especificos por mecanismo (el mecanismo se obtiene de core.ipr.mechanism_id)';


--
-- Name: ipr_milestone; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr_milestone (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    milestone_type_id uuid NOT NULL,
    code character varying(20),
    description text,
    planned_date date NOT NULL,
    actual_date date,
    deviation_days integer GENERATED ALWAYS AS (
CASE
    WHEN (actual_date IS NOT NULL) THEN (actual_date - planned_date)
    ELSE NULL::integer
END) STORED,
    completed_by_id uuid,
    verification_notes text,
    evidence_document_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.ipr_milestone OWNER TO goreos;

--
-- Name: TABLE ipr_milestone; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr_milestone IS 'OO-002: Hitos de proyecto (gnub:ProjectMilestone) con fechas planificadas vs reales';


--
-- Name: COLUMN ipr_milestone.deviation_days; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr_milestone.deviation_days IS 'Desviación calculada: actual - planned. Positivo = atraso, Negativo = adelanto';


--
-- Name: ipr_party; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr_party (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    party_role_id uuid NOT NULL,
    is_primary boolean DEFAULT false,
    valid_from date,
    valid_to date,
    responsibility_description text,
    contact_person text,
    contact_email character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    agreement_id uuid,
    sponsor_division_id uuid
);


ALTER TABLE core.ipr_party OWNER TO goreos;

--
-- Name: TABLE ipr_party; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr_party IS 'OO-003: Partes de IPR siguiendo gist:hasParty con roles categorizados (N:M)';


--
-- Name: COLUMN ipr_party.is_primary; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr_party.is_primary IS 'Parte principal para este rol (cuando hay múltiples ejecutores, uno es el principal)';


--
-- Name: ipr_problem; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr_problem (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20),
    ipr_id uuid NOT NULL,
    agreement_id uuid,
    problem_type_id uuid NOT NULL,
    impact_id uuid,
    description text NOT NULL,
    impact_description text,
    detected_by_id uuid,
    detected_at timestamp with time zone DEFAULT now(),
    state_id uuid NOT NULL,
    proposed_solution text,
    solution_applied text,
    resolved_by_id uuid,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_problem_impact_scheme CHECK (((impact_id IS NULL) OR public.fn_validate_category_scheme(impact_id, 'problem_impact'::character varying))),
    CONSTRAINT chk_problem_state_scheme CHECK (((state_id IS NULL) OR public.fn_validate_category_scheme(state_id, 'problem_state'::character varying))),
    CONSTRAINT chk_problem_type_scheme CHECK (((problem_type_id IS NULL) OR public.fn_validate_category_scheme(problem_type_id, 'problem_type'::character varying)))
);


ALTER TABLE core.ipr_problem OWNER TO goreos;

--
-- Name: TABLE ipr_problem; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr_problem IS 'Problema/nudo detectado en una IPR que bloquea avance';


--
-- Name: ipr_territory; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.ipr_territory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    territory_id uuid NOT NULL,
    impact_type_id uuid NOT NULL,
    is_primary boolean DEFAULT false,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.ipr_territory OWNER TO goreos;

--
-- Name: TABLE ipr_territory; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.ipr_territory IS 'OO-001: Relación N:M IPR↔Territory siguiendo gnub:isLocatedIn con tipo de impacto';


--
-- Name: COLUMN ipr_territory.is_primary; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.ipr_territory.is_primary IS 'Territorio principal de la IPR (para queries rápidas)';


--
-- Name: kinship_declaration; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.kinship_declaration (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    person_id uuid NOT NULL,
    declaration_type character varying(32) NOT NULL,
    declares_no_conflict boolean NOT NULL,
    related_authority_id uuid,
    relationship_type character varying(16),
    relationship_degree integer,
    declared_at timestamp with time zone DEFAULT now() NOT NULL,
    validated_by_id uuid,
    validated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT kinship_declaration_declaration_type_check CHECK (((declaration_type)::text = ANY ((ARRAY['EVALUADOR'::character varying, 'REPRESENTANTE_LEGAL'::character varying, 'PERSONAL_CONTRATADO'::character varying])::text[]))),
    CONSTRAINT kinship_declaration_relationship_degree_check CHECK (((relationship_degree IS NULL) OR ((relationship_degree >= 1) AND (relationship_degree <= 4)))),
    CONSTRAINT kinship_declaration_relationship_type_check CHECK (((relationship_type IS NULL) OR ((relationship_type)::text = ANY ((ARRAY['CONSANGUINIDAD'::character varying, 'AFINIDAD'::character varying])::text[]))))
);


ALTER TABLE core.kinship_declaration OWNER TO goreos;

--
-- Name: legal_document; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.legal_document (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(64) NOT NULL,
    name text NOT NULL,
    doc_type_id uuid,
    publication_date date,
    source_url text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_doc_type_scheme CHECK (((doc_type_id IS NULL) OR public.fn_validate_category_scheme(doc_type_id, 'document_type'::character varying)))
);


ALTER TABLE core.legal_document OWNER TO goreos;

--
-- Name: TABLE legal_document; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.legal_document IS 'Documento legal (Ley, DFL, Reglamento)';


--
-- Name: legal_mandate; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.legal_mandate (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    legal_document_id uuid NOT NULL,
    article_reference character varying(32),
    mandate_text text NOT NULL,
    applies_to_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.legal_mandate OWNER TO goreos;

--
-- Name: TABLE legal_mandate; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.legal_mandate IS 'Mandato legal - constraint institucional derivado de norma';


--
-- Name: minute; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.minute (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    minute_number character varying(32) NOT NULL,
    approved_at date,
    content text,
    resolution_id uuid,
    signed_by_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.minute OWNER TO goreos;

--
-- Name: operational_commitment; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.operational_commitment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20),
    problem_id uuid,
    ipr_id uuid,
    agreement_id uuid,
    budget_commitment_id uuid,
    commitment_type_id uuid NOT NULL,
    description text NOT NULL,
    responsible_id uuid NOT NULL,
    division_id uuid,
    due_date date NOT NULL,
    priority_id uuid,
    state_id uuid NOT NULL,
    observations text,
    completed_at timestamp with time zone,
    verified_by_id uuid,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.operational_commitment OWNER TO goreos;

--
-- Name: TABLE operational_commitment; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.operational_commitment IS 'Tarea asignada a un responsable con plazo y seguimiento';


--
-- Name: organization; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.organization (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    short_name character varying(32),
    org_type_id uuid,
    parent_id uuid,
    valid_from timestamp with time zone,
    valid_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    rut character varying(12),
    CONSTRAINT chk_org_type_scheme CHECK (((org_type_id IS NULL) OR public.fn_validate_category_scheme(org_type_id, 'org_type'::character varying))),
    CONSTRAINT chk_rut_format CHECK (((rut IS NULL) OR ((rut)::text ~ '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'::text)))
);


ALTER TABLE core.organization OWNER TO goreos;

--
-- Name: TABLE organization; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.organization IS 'Organizacion - Division, Departamento, Unidad';


--
-- Name: COLUMN organization.rut; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.organization.rut IS 'tde:RUT, gnub:IdentificadorTributario - Rol Único Tributario. Identificador único de personas jurídicas en Chile (SII). Formato: XX.XXX.XXX-X. Normalizado desde metadata.rut el 2026-01-30.';


--
-- Name: person; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.person (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    rut character varying(12),
    names text NOT NULL,
    paternal_surname text NOT NULL,
    maternal_surname text,
    email character varying(255),
    phone character varying(20),
    person_type_id uuid,
    organization_id uuid,
    role_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    estamento_id uuid,
    position_id uuid,
    qualification_id uuid,
    CONSTRAINT chk_estamento_scheme CHECK (((estamento_id IS NULL) OR public.fn_validate_category_scheme(estamento_id, 'estamento'::character varying))),
    CONSTRAINT chk_person_type_scheme CHECK (((person_type_id IS NULL) OR public.fn_validate_category_scheme(person_type_id, 'person_type'::character varying)))
);


ALTER TABLE core.person OWNER TO goreos;

--
-- Name: TABLE person; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.person IS 'Persona natural - funcionario, ciudadano, proveedor';


--
-- Name: COLUMN person.estamento_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.person.estamento_id IS 'tde:Estamento - Clasificación funcionaria según Ley 18.834. Normalized from metadata.estamento on 2026-01-30. Valid values: PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD.';


--
-- Name: planning_instrument; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.planning_instrument (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    instrument_type_id uuid,
    valid_from date,
    valid_to date,
    approved_by uuid,
    parent_instrument_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.planning_instrument OWNER TO goreos;

--
-- Name: TABLE planning_instrument; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.planning_instrument IS 'Instrumento de planificacion (ERD, PROT, ARI)';


--
-- Name: position; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core."position" (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(255) NOT NULL,
    name text NOT NULL,
    organization_id uuid,
    level smallint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core."position" OWNER TO goreos;

--
-- Name: TABLE "position"; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core."position" IS 'Cargos y posiciones laborales (tde:Cargo, v3.0 MEDIA)';


--
-- Name: procedure; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.procedure (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    procedure_type_id uuid,
    responsible_division_id uuid,
    platform_id uuid,
    max_days integer,
    is_online boolean DEFAULT false,
    legal_basis text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.procedure OWNER TO goreos;

--
-- Name: TABLE procedure; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.procedure IS 'Tramite o servicio ofrecido al ciudadano';


--
-- Name: progress_report; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.progress_report (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ipr_id uuid NOT NULL,
    report_number integer NOT NULL,
    report_date date NOT NULL,
    physical_progress numeric(5,2),
    financial_progress numeric(5,2),
    description text,
    issues_detected text,
    reported_by_id uuid NOT NULL,
    attachment_url text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_financial_progress CHECK (((financial_progress IS NULL) OR ((financial_progress >= (0)::numeric) AND (financial_progress <= (100)::numeric)))),
    CONSTRAINT chk_physical_progress CHECK (((physical_progress IS NULL) OR ((physical_progress >= (0)::numeric) AND (physical_progress <= (100)::numeric))))
);


ALTER TABLE core.progress_report OWNER TO goreos;

--
-- Name: TABLE progress_report; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.progress_report IS 'Reporte periodico de avance fisico/financiero de IPR';


--
-- Name: rendition; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.rendition (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    renderer_id uuid,
    state_id uuid,
    period_start date,
    period_end date,
    submitted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    ipr_id uuid,
    amount numeric(18,2),
    phase_entered_at timestamp with time zone DEFAULT now(),
    responsible_id uuid,
    archived_at timestamp with time zone,
    CONSTRAINT chk_rendition_link CHECK (((agreement_id IS NOT NULL) OR (ipr_id IS NOT NULL))),
    CONSTRAINT chk_rendition_state_scheme CHECK (((state_id IS NULL) OR public.fn_validate_category_scheme(state_id, 'rendition_state'::character varying)))
);


ALTER TABLE core.rendition OWNER TO goreos;

--
-- Name: TABLE rendition; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.rendition IS 'Rendicion de cuentas de un convenio';


--
-- Name: COLUMN rendition.amount; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core.rendition.amount IS 'Monto rendido en la rendición';


--
-- Name: rendition_escalation; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.rendition_escalation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    rendition_id uuid NOT NULL,
    phase_id uuid NOT NULL,
    escalation_level integer NOT NULL,
    detected_at timestamp with time zone DEFAULT now() NOT NULL,
    alert_id uuid,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT rendition_escalation_escalation_level_check CHECK (((escalation_level >= 1) AND (escalation_level <= 3)))
);


ALTER TABLE core.rendition_escalation OWNER TO goreos;

--
-- Name: rendition_history; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.rendition_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    rendition_id uuid NOT NULL,
    previous_state_id uuid,
    new_state_id uuid NOT NULL,
    changed_by_id uuid NOT NULL,
    comment text,
    changed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.rendition_history OWNER TO goreos;

--
-- Name: TABLE rendition_history; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.rendition_history IS 'Historial de cambios de estado de rendiciones (SISREC)';


--
-- Name: rendition_phase; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.rendition_phase (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ordinal integer NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    responsible_role text NOT NULL,
    sla_days integer NOT NULL,
    escalation_action text,
    is_internal boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT rendition_phase_ordinal_check CHECK (((ordinal >= 1) AND (ordinal <= 8)))
);


ALTER TABLE core.rendition_phase OWNER TO goreos;

--
-- Name: resolution; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.resolution (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    administrative_act_id uuid NOT NULL,
    resolution_type_id uuid NOT NULL,
    resolution_subtype_id uuid,
    ipr_id uuid,
    agreement_id uuid,
    budget_amount numeric(18,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_res_subtype_scheme CHECK (((resolution_subtype_id IS NULL) OR public.fn_validate_category_scheme(resolution_subtype_id, 'resolution_subtype'::character varying))),
    CONSTRAINT chk_res_type_scheme CHECK (((resolution_type_id IS NULL) OR public.fn_validate_category_scheme(resolution_type_id, 'resolution_type'::character varying)))
);


ALTER TABLE core.resolution OWNER TO goreos;

--
-- Name: TABLE resolution; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.resolution IS 'Resolucion - EXENTA, AFECTA o CONJUNTA';


--
-- Name: risk; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.risk (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    risk_type_id uuid,
    probability_id uuid,
    impact_id uuid,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    mitigation_plan text,
    status_id uuid,
    identified_at date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.risk OWNER TO goreos;

--
-- Name: TABLE risk; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.risk IS 'Riesgo identificado en un proceso o IPR';


--
-- Name: schema_migration; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.schema_migration (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    applied_at timestamp with time zone DEFAULT now() NOT NULL,
    checksum character varying(64),
    applied_by character varying(128)
);


ALTER TABLE core.schema_migration OWNER TO goreos;

--
-- Name: schema_migration_id_seq; Type: SEQUENCE; Schema: core; Owner: goreos
--

CREATE SEQUENCE core.schema_migration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.schema_migration_id_seq OWNER TO goreos;

--
-- Name: schema_migration_id_seq; Type: SEQUENCE OWNED BY; Schema: core; Owner: goreos
--

ALTER SEQUENCE core.schema_migration_id_seq OWNED BY core.schema_migration.id;


--
-- Name: session; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.session (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    committee_id uuid NOT NULL,
    session_number integer NOT NULL,
    session_type_id uuid,
    scheduled_at timestamp with time zone NOT NULL,
    started_at timestamp with time zone,
    ended_at timestamp with time zone,
    quorum_reached boolean,
    location text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_session_type_scheme CHECK (((session_type_id IS NULL) OR public.fn_validate_category_scheme(session_type_id, 'session_type'::character varying)))
);


ALTER TABLE core.session OWNER TO goreos;

--
-- Name: session_agreement; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.session_agreement (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    minute_id uuid NOT NULL,
    agreement_number integer NOT NULL,
    subject text NOT NULL,
    decision text NOT NULL,
    responsible_id uuid,
    due_date date,
    status_id uuid,
    ipr_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.session_agreement OWNER TO goreos;

--
-- Name: session_vote; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.session_vote (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_agreement_id uuid NOT NULL,
    voter_id uuid NOT NULL,
    vote_option_id uuid NOT NULL,
    recorded_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE core.session_vote OWNER TO goreos;

--
-- Name: sni_level_config; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.sni_level_config (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    level_number integer NOT NULL,
    label text NOT NULL,
    min_utm numeric(12,2) DEFAULT 0 NOT NULL,
    max_utm numeric(12,2),
    evaluator_code text NOT NULL,
    requires_external_eval boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.sni_level_config OWNER TO goreos;

--
-- Name: TABLE sni_level_config; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.sni_level_config IS 'SNI proporcionalidad: evaluation levels by project amount (HΩ-11)';


--
-- Name: subv8_fund; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.subv8_fund (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    budget_regular numeric,
    budget_special numeric,
    budget_total numeric,
    is_exclusive boolean DEFAULT false NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.subv8_fund OWNER TO goreos;

--
-- Name: TABLE subv8_fund; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.subv8_fund IS 'TP-02: Subvención 8% thematic funds with budget ceilings';


--
-- Name: subv8_fund_ceiling; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.subv8_fund_ceiling (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fund_id uuid NOT NULL,
    institution_type character varying(64) NOT NULL,
    area character varying(64),
    max_amount numeric NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT subv8_fund_ceiling_max_amount_check CHECK ((max_amount > (0)::numeric))
);


ALTER TABLE core.subv8_fund_ceiling OWNER TO goreos;

--
-- Name: TABLE subv8_fund_ceiling; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.subv8_fund_ceiling IS 'TP-02: Max project amount per fund × institution type × area';


--
-- Name: territorial_indicator; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.territorial_indicator (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    indicator_type_id uuid,
    territory_id uuid,
    fiscal_year integer,
    numeric_value numeric(18,4),
    unit_id uuid,
    source text,
    measured_at date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.territorial_indicator OWNER TO goreos;

--
-- Name: TABLE territorial_indicator; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.territorial_indicator IS 'Indicador socioeconomico o de gestion territorial';


--
-- Name: territory; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.territory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(16) NOT NULL,
    name text NOT NULL,
    territory_type_id uuid NOT NULL,
    parent_id uuid,
    population integer,
    area_km2 numeric(12,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_territory_type_scheme CHECK (((territory_type_id IS NULL) OR public.fn_validate_category_scheme(territory_type_id, 'territory_type'::character varying)))
);


ALTER TABLE core.territory OWNER TO goreos;

--
-- Name: TABLE territory; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.territory IS 'Unidad territorial (Region, Provincia, Comuna)';


--
-- Name: user; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core."user" (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    system_role_id uuid NOT NULL,
    division_id uuid,
    is_active boolean DEFAULT true NOT NULL,
    last_login_at timestamp with time zone,
    failed_login_attempts integer DEFAULT 0,
    locked_until timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_system_role_scheme CHECK (((system_role_id IS NULL) OR public.fn_validate_category_scheme(system_role_id, 'system_role'::character varying)))
);


ALTER TABLE core."user" OWNER TO goreos;

--
-- Name: TABLE "user"; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core."user" IS 'Usuario del sistema con credenciales de autenticacion';


--
-- Name: COLUMN "user".system_role_id; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON COLUMN core."user".system_role_id IS 'scheme=system_role: ADMIN_SISTEMA|ADMIN_REGIONAL|JEFE_DIVISION|ENCARGADO';


--
-- Name: vehicle; Type: TABLE; Schema: core; Owner: goreos
--

CREATE TABLE core.vehicle (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventory_item_id uuid,
    plate character varying(10) NOT NULL,
    brand character varying(64),
    model character varying(64),
    year integer,
    vehicle_type_id uuid,
    fuel_type_id uuid,
    assigned_division_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE core.vehicle OWNER TO goreos;

--
-- Name: TABLE vehicle; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TABLE core.vehicle IS 'Vehiculo institucional';


--
-- Name: category; Type: TABLE; Schema: ref; Owner: goreos
--

CREATE TABLE ref.category (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scheme character varying(32) NOT NULL,
    code character varying(32) NOT NULL,
    label text NOT NULL,
    label_en text,
    description text,
    parent_id uuid,
    parent_code character varying(32),
    phase_id uuid,
    valid_transitions jsonb,
    sort_order integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_category_metadata_object CHECK (((metadata IS NULL) OR (jsonb_typeof(metadata) = 'object'::text)))
);


ALTER TABLE ref.category OWNER TO goreos;

--
-- Name: TABLE category; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON TABLE ref.category IS 'Patron Category (Gist 14.0) - 75+ schemes de taxonomias flexibles';


--
-- Name: COLUMN category.phase_id; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON COLUMN ref.category.phase_id IS 'Para scheme=ipr_state: FK a mcd_phase al que pertenece este estado';


--
-- Name: COLUMN category.valid_transitions; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON COLUMN ref.category.valid_transitions IS 'Array JSON de codigos de estado validos como destino';


--
-- Name: CONSTRAINT chk_category_metadata_object ON category; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON CONSTRAINT chk_category_metadata_object ON ref.category IS 'STR-003 FIX: Garantiza que metadata sea objeto JSON, no array o primitivo';


--
-- Name: vw_ipr_applicant; Type: VIEW; Schema: core; Owner: goreos
--

CREATE VIEW core.vw_ipr_applicant AS
 SELECT p.ipr_id,
    p.organization_id AS applicant_id,
    o.name AS applicant_name
   FROM ((core.ipr_party p
     JOIN ref.category c ON ((c.id = p.party_role_id)))
     JOIN core.organization o ON ((o.id = p.organization_id)))
  WHERE (((c.scheme)::text = 'ipr_party_role'::text) AND ((c.code)::text = 'POSTULANTE'::text) AND (p.is_primary = true) AND (p.deleted_at IS NULL));


ALTER VIEW core.vw_ipr_applicant OWNER TO goreos;

--
-- Name: VIEW vw_ipr_applicant; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON VIEW core.vw_ipr_applicant IS 'Vista de compatibilidad: Postulante principal de cada IPR';


--
-- Name: vw_ipr_executor; Type: VIEW; Schema: core; Owner: goreos
--

CREATE VIEW core.vw_ipr_executor AS
 SELECT p.ipr_id,
    p.organization_id AS executor_id,
    o.name AS executor_name
   FROM ((core.ipr_party p
     JOIN ref.category c ON ((c.id = p.party_role_id)))
     JOIN core.organization o ON ((o.id = p.organization_id)))
  WHERE (((c.scheme)::text = 'ipr_party_role'::text) AND ((c.code)::text = 'EJECUTOR'::text) AND (p.is_primary = true) AND (p.deleted_at IS NULL));


ALTER VIEW core.vw_ipr_executor OWNER TO goreos;

--
-- Name: VIEW vw_ipr_executor; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON VIEW core.vw_ipr_executor IS 'Vista de compatibilidad: Ejecutor principal de cada IPR';


--
-- Name: vw_ipr_formulator; Type: VIEW; Schema: core; Owner: goreos
--

CREATE VIEW core.vw_ipr_formulator AS
 SELECT p.ipr_id,
    p.organization_id AS formulator_id,
    o.name AS formulator_name
   FROM ((core.ipr_party p
     JOIN ref.category c ON ((c.id = p.party_role_id)))
     JOIN core.organization o ON ((o.id = p.organization_id)))
  WHERE (((c.scheme)::text = 'ipr_party_role'::text) AND ((c.code)::text = 'FORMULADOR'::text) AND (p.is_primary = true) AND (p.deleted_at IS NULL));


ALTER VIEW core.vw_ipr_formulator OWNER TO goreos;

--
-- Name: VIEW vw_ipr_formulator; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON VIEW core.vw_ipr_formulator IS 'Vista de compatibilidad: Formulador principal de cada IPR';


--
-- Name: vw_ipr_parties; Type: VIEW; Schema: core; Owner: goreos
--

CREATE VIEW core.vw_ipr_parties AS
 SELECT p.ipr_id,
    i.codigo_bip,
    p.organization_id,
    o.name AS organization_name,
    c.code AS role_code,
    c.label AS role_label,
    p.is_primary,
    p.valid_from,
    p.valid_to,
    p.responsibility_description
   FROM (((core.ipr_party p
     JOIN core.ipr i ON ((i.id = p.ipr_id)))
     JOIN core.organization o ON ((o.id = p.organization_id)))
     JOIN ref.category c ON ((c.id = p.party_role_id)))
  WHERE ((p.deleted_at IS NULL) AND ((c.scheme)::text = 'ipr_party_role'::text));


ALTER VIEW core.vw_ipr_parties OWNER TO goreos;

--
-- Name: VIEW vw_ipr_parties; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON VIEW core.vw_ipr_parties IS 'Vista consolidada de todas las partes de cada IPR con sus roles';


--
-- Name: entity; Type: TABLE; Schema: meta; Owner: goreos
--

CREATE TABLE meta.entity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    ontology_uri text,
    domain character varying(16),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE meta.entity OWNER TO goreos;

--
-- Name: TABLE entity; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON TABLE meta.entity IS 'Entidad del dominio - estructura de informacion';


--
-- Name: process; Type: TABLE; Schema: meta; Owner: goreos
--

CREATE TABLE meta.process (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    layer public.process_layer_enum,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE meta.process OWNER TO goreos;

--
-- Name: TABLE process; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON TABLE meta.process IS 'Proceso - perspectiva dinamica del sistema';


--
-- Name: COLUMN process.layer; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON COLUMN meta.process.layer IS 'STRATEGIC|TACTICAL|OPERATIONAL';


--
-- Name: role; Type: TABLE; Schema: meta; Owner: goreos
--

CREATE TABLE meta.role (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    agent_type public.agent_type_enum DEFAULT 'HUMAN'::public.agent_type_enum NOT NULL,
    cognition_level public.cognition_level_enum,
    human_accountable_id uuid,
    delegation_mode public.delegation_mode_enum,
    ontology_uri text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_human_accountable CHECK (((agent_type = 'HUMAN'::public.agent_type_enum) OR (human_accountable_id IS NOT NULL)))
);


ALTER TABLE meta.role OWNER TO goreos;

--
-- Name: TABLE role; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON TABLE meta.role IS 'Rol con soporte HAIC - capacidad de ejecutar transformacion';


--
-- Name: COLUMN role.agent_type; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON COLUMN meta.role.agent_type IS 'HUMAN|AI|ALGORITHMIC|ORGANIZATIONAL|MACHINE|MIXED (Sustrato)';


--
-- Name: COLUMN role.cognition_level; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON COLUMN meta.role.cognition_level IS 'C0|C1|C2|C3 (Nivel de decision ORKO)';


--
-- Name: COLUMN role.delegation_mode; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON COLUMN meta.role.delegation_mode IS 'M1-M6 (modo de delegacion ORKO)';


--
-- Name: story; Type: TABLE; Schema: meta; Owner: goreos
--

CREATE TABLE meta.story (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    as_a text NOT NULL,
    i_want text NOT NULL,
    so_that text NOT NULL,
    role_id uuid,
    process_id uuid,
    domain character varying(16),
    priority character varying(4),
    status public.story_status_enum DEFAULT 'ENRICHED'::public.story_status_enum,
    user_description text,
    aspect_id uuid,
    scope_id uuid,
    extra_tags text[],
    acceptance_criteria text[],
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE meta.story OWNER TO goreos;

--
-- Name: TABLE story; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON TABLE meta.story IS 'Historia de usuario - atomo fundamental, origen de todo requerimiento';


--
-- Name: story_entity; Type: TABLE; Schema: meta; Owner: goreos
--

CREATE TABLE meta.story_entity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    story_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    status public.story_status_enum,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid
);


ALTER TABLE meta.story_entity OWNER TO goreos;

--
-- Name: TABLE story_entity; Type: COMMENT; Schema: meta; Owner: goreos
--

COMMENT ON TABLE meta.story_entity IS 'Relacion N:M entre historias y entidades';


--
-- Name: acceptance_criteria; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.acceptance_criteria (
    id integer NOT NULL,
    us_id character varying(100),
    description text
);


ALTER TABLE public.acceptance_criteria OWNER TO goreos;

--
-- Name: acceptance_criteria_id_seq; Type: SEQUENCE; Schema: public; Owner: goreos
--

CREATE SEQUENCE public.acceptance_criteria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.acceptance_criteria_id_seq OWNER TO goreos;

--
-- Name: acceptance_criteria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: goreos
--

ALTER SEQUENCE public.acceptance_criteria_id_seq OWNED BY public.acceptance_criteria.id;


--
-- Name: bridge_us_entity; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.bridge_us_entity (
    us_id character varying(100) NOT NULL,
    entity_id character varying(100) NOT NULL,
    status character varying(20)
);


ALTER TABLE public.bridge_us_entity OWNER TO goreos;

--
-- Name: bridge_us_extra_tag; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.bridge_us_extra_tag (
    us_id character varying(100) NOT NULL,
    tag character varying(100) NOT NULL
);


ALTER TABLE public.bridge_us_extra_tag OWNER TO goreos;

--
-- Name: dim_entity; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.dim_entity (
    id character varying(100) NOT NULL,
    domain character varying(20),
    usage_count integer DEFAULT 0
);


ALTER TABLE public.dim_entity OWNER TO goreos;

--
-- Name: dim_extra_tag; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.dim_extra_tag (
    tag character varying(100) NOT NULL,
    usage_count integer DEFAULT 0
);


ALTER TABLE public.dim_extra_tag OWNER TO goreos;

--
-- Name: dim_process; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.dim_process (
    id character varying(100) NOT NULL,
    usage_count integer DEFAULT 0
);


ALTER TABLE public.dim_process OWNER TO goreos;

--
-- Name: dim_role; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.dim_role (
    id character varying(100) NOT NULL,
    label text,
    agent_type character varying(20) DEFAULT 'HUMAN'::character varying,
    description text,
    usage_count integer DEFAULT 0,
    canonical_id character varying(50),
    especialidad character varying(50)
);


ALTER TABLE public.dim_role OWNER TO goreos;

--
-- Name: dim_role_canonical; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.dim_role_canonical (
    id character varying(50) NOT NULL,
    division character varying(20) NOT NULL,
    funcion character varying(30) NOT NULL,
    label text NOT NULL,
    agent_type character varying(20) DEFAULT 'HUMAN'::character varying,
    descripcion text,
    nivel_jerarquico integer DEFAULT 3,
    usage_count integer DEFAULT 0,
    CONSTRAINT dim_role_canonical_agent_type_check CHECK (((agent_type)::text = ANY ((ARRAY['HUMAN'::character varying, 'AGENT'::character varying, 'EXTERNAL'::character varying])::text[]))),
    CONSTRAINT dim_role_canonical_nivel_jerarquico_check CHECK (((nivel_jerarquico >= 1) AND (nivel_jerarquico <= 4)))
);


ALTER TABLE public.dim_role_canonical OWNER TO goreos;

--
-- Name: fact_user_story; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.fact_user_story (
    id character varying(100) NOT NULL,
    urn text,
    name text,
    as_a text,
    i_want text,
    so_that text,
    status character varying(20),
    role_id character varying(100),
    role_canonical_id character varying(50),
    process_id character varying(100),
    process_status character varying(20),
    domain character varying(50),
    aspect character varying(50),
    priority character varying(10),
    scope character varying(50)
);


ALTER TABLE public.fact_user_story OWNER TO goreos;

--
-- Name: role_especialidad; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.role_especialidad (
    role_id character varying(50) NOT NULL,
    especialidad character varying(50) NOT NULL,
    descripcion text
);


ALTER TABLE public.role_especialidad OWNER TO goreos;

--
-- Name: role_mapping; Type: TABLE; Schema: public; Owner: goreos
--

CREATE TABLE public.role_mapping (
    legacy_id character varying(100) NOT NULL,
    canonical_id character varying(50),
    especialidad character varying(50),
    notas text
);


ALTER TABLE public.role_mapping OWNER TO goreos;

--
-- Name: v_role_mapping; Type: VIEW; Schema: public; Owner: goreos
--

CREATE VIEW public.v_role_mapping AS
 SELECT dr.id AS legacy_id,
    dr.label AS legacy_label,
    dr.canonical_id,
    drc.label AS canonical_label,
    dr.especialidad,
    drc.division
   FROM (public.dim_role dr
     LEFT JOIN public.dim_role_canonical drc ON (((dr.canonical_id)::text = (drc.id)::text)));


ALTER VIEW public.v_role_mapping OWNER TO goreos;

--
-- Name: v_roles_por_division; Type: VIEW; Schema: public; Owner: goreos
--

CREATE VIEW public.v_roles_por_division AS
 SELECT division,
    count(*) AS total_roles,
    sum(usage_count) AS total_usage,
    count(
        CASE
            WHEN ((agent_type)::text = 'HUMAN'::text) THEN 1
            ELSE NULL::integer
        END) AS roles_humanos,
    count(
        CASE
            WHEN ((agent_type)::text = 'AGENT'::text) THEN 1
            ELSE NULL::integer
        END) AS roles_agente,
    count(
        CASE
            WHEN ((agent_type)::text = 'EXTERNAL'::text) THEN 1
            ELSE NULL::integer
        END) AS roles_externos
   FROM public.dim_role_canonical
  GROUP BY division
  ORDER BY (sum(usage_count)) DESC;


ALTER VIEW public.v_roles_por_division OWNER TO goreos;

--
-- Name: v_roles_summary; Type: VIEW; Schema: public; Owner: goreos
--

CREATE VIEW public.v_roles_summary AS
 SELECT r.id,
    r.division,
    r.funcion,
    r.label,
    r.agent_type,
    r.usage_count,
    COALESCE(e.num_especialidades, (0)::bigint) AS num_especialidades
   FROM (public.dim_role_canonical r
     LEFT JOIN ( SELECT role_especialidad.role_id,
            count(*) AS num_especialidades
           FROM public.role_especialidad
          GROUP BY role_especialidad.role_id) e ON (((r.id)::text = (e.role_id)::text)))
  ORDER BY r.division, r.funcion;


ALTER VIEW public.v_roles_summary OWNER TO goreos;

--
-- Name: actor; Type: TABLE; Schema: ref; Owner: goreos
--

CREATE TABLE ref.actor (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(32) NOT NULL,
    name text NOT NULL,
    full_name text,
    agent_type public.agent_type_enum DEFAULT 'HUMAN'::public.agent_type_enum NOT NULL,
    emoji character varying(8),
    style character varying(100),
    agent_definition_uri text,
    agent_version character varying(16),
    organization_id uuid,
    is_internal boolean DEFAULT true,
    sort_order integer,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_actor_type CHECK ((((agent_type = 'HUMAN'::public.agent_type_enum) AND (agent_definition_uri IS NULL)) OR ((agent_type = 'ALGORITHMIC'::public.agent_type_enum) AND (agent_definition_uri IS NOT NULL)) OR (agent_type = 'ORGANIZATIONAL'::public.agent_type_enum) OR (agent_type = ANY (ARRAY['AI'::public.agent_type_enum, 'MACHINE'::public.agent_type_enum, 'MIXED'::public.agent_type_enum]))))
);


ALTER TABLE ref.actor OWNER TO goreos;

--
-- Name: TABLE actor; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON TABLE ref.actor IS 'Actores en flujos de proceso - humanos, algoritmicos, organizacionales';


--
-- Name: COLUMN actor.agent_type; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON COLUMN ref.actor.agent_type IS 'HUMAN|AI|ALGORITHMIC|ORGANIZATIONAL|MACHINE|MIXED';


--
-- Name: COLUMN actor.agent_definition_uri; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON COLUMN ref.actor.agent_definition_uri IS 'URI al YAML/JSON de definicion del agente (koda://...)';


--
-- Name: operational_commitment_type; Type: TABLE; Schema: ref; Owner: goreos
--

CREATE TABLE ref.operational_commitment_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    requires_ipr_link boolean DEFAULT true,
    default_days integer DEFAULT 7,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    updated_by_id uuid,
    deleted_at timestamp with time zone,
    deleted_by_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE ref.operational_commitment_type OWNER TO goreos;

--
-- Name: TABLE operational_commitment_type; Type: COMMENT; Schema: ref; Owner: goreos
--

COMMENT ON TABLE ref.operational_commitment_type IS 'Tipos de compromiso operativo para gestion';


--
-- Name: event; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
)
PARTITION BY RANGE (occurred_at);


ALTER TABLE txn.event OWNER TO goreos;

--
-- Name: TABLE event; Type: COMMENT; Schema: txn; Owner: goreos
--

COMMENT ON TABLE txn.event IS 'Evento del sistema - Event Sourcing (particionado por mes)';


--
-- Name: COLUMN event.subject_id; Type: COMMENT; Schema: txn; Owner: goreos
--

COMMENT ON COLUMN txn.event.subject_id IS 'UUID del sujeto';


--
-- Name: COLUMN event.actor_id; Type: COMMENT; Schema: txn; Owner: goreos
--

COMMENT ON COLUMN txn.event.actor_id IS 'UUID del usuario que ejecuta la acción (core.user)';


--
-- Name: COLUMN event.actor_ref_id; Type: COMMENT; Schema: txn; Owner: goreos
--

COMMENT ON COLUMN txn.event.actor_ref_id IS 'UUID opcional del actor en ref.actor (agentes algorítmicos)';


--
-- Name: event_2026_01; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_01 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_01 OWNER TO goreos;

--
-- Name: event_2026_02; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_02 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_02 OWNER TO goreos;

--
-- Name: event_2026_03; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_03 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_03 OWNER TO goreos;

--
-- Name: event_2026_04; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_04 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_04 OWNER TO goreos;

--
-- Name: event_2026_05; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_05 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_05 OWNER TO goreos;

--
-- Name: event_2026_06; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_06 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_06 OWNER TO goreos;

--
-- Name: event_2026_07; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_07 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_07 OWNER TO goreos;

--
-- Name: event_2026_08; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_08 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_08 OWNER TO goreos;

--
-- Name: event_2026_09; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_09 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_09 OWNER TO goreos;

--
-- Name: event_2026_10; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_10 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_10 OWNER TO goreos;

--
-- Name: event_2026_11; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_11 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_11 OWNER TO goreos;

--
-- Name: event_2026_12; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_2026_12 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_2026_12 OWNER TO goreos;

--
-- Name: event_default; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.event_default (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type_id uuid NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    actor_id uuid,
    actor_ref_id uuid,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by_id uuid,
    CONSTRAINT chk_event_type_scheme CHECK (((event_type_id IS NULL) OR public.fn_validate_category_scheme(event_type_id, 'event_type'::character varying)))
);


ALTER TABLE txn.event_default OWNER TO goreos;

--
-- Name: magnitude; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
)
PARTITION BY RANGE (as_of_date);


ALTER TABLE txn.magnitude OWNER TO goreos;

--
-- Name: TABLE magnitude; Type: COMMENT; Schema: txn; Owner: goreos
--

COMMENT ON TABLE txn.magnitude IS 'Magnitude Pattern (Gist 14.0) - particionado por fecha';


--
-- Name: magnitude_2026_q1; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude_2026_q1 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
);


ALTER TABLE txn.magnitude_2026_q1 OWNER TO goreos;

--
-- Name: magnitude_2026_q2; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude_2026_q2 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
);


ALTER TABLE txn.magnitude_2026_q2 OWNER TO goreos;

--
-- Name: magnitude_2026_q3; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude_2026_q3 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
);


ALTER TABLE txn.magnitude_2026_q3 OWNER TO goreos;

--
-- Name: magnitude_2026_q4; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude_2026_q4 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
);


ALTER TABLE txn.magnitude_2026_q4 OWNER TO goreos;

--
-- Name: magnitude_default; Type: TABLE; Schema: txn; Owner: goreos
--

CREATE TABLE txn.magnitude_default (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject_type character varying(32) NOT NULL,
    subject_id uuid NOT NULL,
    aspect_id uuid NOT NULL,
    numeric_value numeric(18,2),
    unit_id uuid,
    as_of_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid,
    CONSTRAINT chk_magnitude_aspect_scheme CHECK (((aspect_id IS NULL) OR public.fn_validate_category_scheme(aspect_id, 'aspect'::character varying)))
);


ALTER TABLE txn.magnitude_default OWNER TO goreos;

--
-- Name: event_2026_01; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_01 FOR VALUES FROM ('2026-01-01 00:00:00+00') TO ('2026-02-01 00:00:00+00');


--
-- Name: event_2026_02; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_02 FOR VALUES FROM ('2026-02-01 00:00:00+00') TO ('2026-03-01 00:00:00+00');


--
-- Name: event_2026_03; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_03 FOR VALUES FROM ('2026-03-01 00:00:00+00') TO ('2026-04-01 00:00:00+00');


--
-- Name: event_2026_04; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_04 FOR VALUES FROM ('2026-04-01 00:00:00+00') TO ('2026-05-01 00:00:00+00');


--
-- Name: event_2026_05; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_05 FOR VALUES FROM ('2026-05-01 00:00:00+00') TO ('2026-06-01 00:00:00+00');


--
-- Name: event_2026_06; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_06 FOR VALUES FROM ('2026-06-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');


--
-- Name: event_2026_07; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_07 FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-08-01 00:00:00+00');


--
-- Name: event_2026_08; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_08 FOR VALUES FROM ('2026-08-01 00:00:00+00') TO ('2026-09-01 00:00:00+00');


--
-- Name: event_2026_09; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_09 FOR VALUES FROM ('2026-09-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');


--
-- Name: event_2026_10; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_10 FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');


--
-- Name: event_2026_11; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_11 FOR VALUES FROM ('2026-11-01 00:00:00+00') TO ('2026-12-01 00:00:00+00');


--
-- Name: event_2026_12; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_2026_12 FOR VALUES FROM ('2026-12-01 00:00:00+00') TO ('2027-01-01 00:00:00+00');


--
-- Name: event_default; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event ATTACH PARTITION txn.event_default DEFAULT;


--
-- Name: magnitude_2026_q1; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude ATTACH PARTITION txn.magnitude_2026_q1 FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');


--
-- Name: magnitude_2026_q2; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude ATTACH PARTITION txn.magnitude_2026_q2 FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');


--
-- Name: magnitude_2026_q3; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude ATTACH PARTITION txn.magnitude_2026_q3 FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');


--
-- Name: magnitude_2026_q4; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude ATTACH PARTITION txn.magnitude_2026_q4 FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');


--
-- Name: magnitude_default; Type: TABLE ATTACH; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude ATTACH PARTITION txn.magnitude_default DEFAULT;


--
-- Name: schema_migration id; Type: DEFAULT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.schema_migration ALTER COLUMN id SET DEFAULT nextval('core.schema_migration_id_seq'::regclass);


--
-- Name: acceptance_criteria id; Type: DEFAULT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.acceptance_criteria ALTER COLUMN id SET DEFAULT nextval('public.acceptance_criteria_id_seq'::regclass);


--
-- Name: administrative_act_history administrative_act_history_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act_history
    ADD CONSTRAINT administrative_act_history_pkey PRIMARY KEY (id);


--
-- Name: administrative_act administrative_act_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_pkey PRIMARY KEY (id);


--
-- Name: administrative_procedure administrative_procedure_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_code_key UNIQUE (code);


--
-- Name: administrative_procedure administrative_procedure_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_pkey PRIMARY KEY (id);


--
-- Name: admissibility_check admissibility_check_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_check
    ADD CONSTRAINT admissibility_check_pkey PRIMARY KEY (id);


--
-- Name: admissibility_item admissibility_item_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_item
    ADD CONSTRAINT admissibility_item_pkey PRIMARY KEY (id);


--
-- Name: agenda_item_context agenda_item_context_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agenda_item_context
    ADD CONSTRAINT agenda_item_context_pkey PRIMARY KEY (id);


--
-- Name: agenda_item_context agenda_item_context_session_agreement_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agenda_item_context
    ADD CONSTRAINT agenda_item_context_session_agreement_id_key UNIQUE (session_agreement_id);


--
-- Name: agreement_history agreement_history_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_history
    ADD CONSTRAINT agreement_history_pkey PRIMARY KEY (id);


--
-- Name: agreement_installment agreement_installment_agreement_id_installment_number_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_agreement_id_installment_number_key UNIQUE (agreement_id, installment_number);


--
-- Name: agreement_installment agreement_installment_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_pkey PRIMARY KEY (id);


--
-- Name: agreement agreement_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_pkey PRIMARY KEY (id);


--
-- Name: alert alert_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_pkey PRIMARY KEY (id);


--
-- Name: budget_carryover budget_carryover_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_carryover
    ADD CONSTRAINT budget_carryover_pkey PRIMARY KEY (id);


--
-- Name: budget_carryover budget_carryover_unique_year; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_carryover
    ADD CONSTRAINT budget_carryover_unique_year UNIQUE (budget_program_id, fiscal_year);


--
-- Name: budget_commitment budget_commitment_commitment_number_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_commitment_number_key UNIQUE (commitment_number);


--
-- Name: budget_commitment budget_commitment_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_pkey PRIMARY KEY (id);


--
-- Name: budget_cycle_milestone budget_cycle_milestone_ordinal_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_milestone
    ADD CONSTRAINT budget_cycle_milestone_ordinal_key UNIQUE (ordinal);


--
-- Name: budget_cycle_milestone budget_cycle_milestone_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_milestone
    ADD CONSTRAINT budget_cycle_milestone_pkey PRIMARY KEY (id);


--
-- Name: budget_cycle_tracking budget_cycle_tracking_milestone_id_fiscal_year_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_tracking
    ADD CONSTRAINT budget_cycle_tracking_milestone_id_fiscal_year_key UNIQUE (milestone_id, fiscal_year);


--
-- Name: budget_cycle_tracking budget_cycle_tracking_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_tracking
    ADD CONSTRAINT budget_cycle_tracking_pkey PRIMARY KEY (id);


--
-- Name: budget_program budget_program_code_fiscal_year_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_code_fiscal_year_key UNIQUE (code, fiscal_year);


--
-- Name: budget_program budget_program_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_pkey PRIMARY KEY (id);


--
-- Name: commitment_history commitment_history_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.commitment_history
    ADD CONSTRAINT commitment_history_pkey PRIMARY KEY (id);


--
-- Name: committee committee_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_code_key UNIQUE (code);


--
-- Name: committee_member committee_member_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_pkey PRIMARY KEY (id);


--
-- Name: committee committee_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_pkey PRIMARY KEY (id);


--
-- Name: crisis_meeting crisis_meeting_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_pkey PRIMARY KEY (id);


--
-- Name: crisis_meeting crisis_meeting_session_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_session_id_key UNIQUE (session_id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_code_key UNIQUE (code);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_pkey PRIMARY KEY (id);


--
-- Name: dgi_committee_session dgi_committee_session_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_committee_session
    ADD CONSTRAINT dgi_committee_session_pkey PRIMARY KEY (id);


--
-- Name: dgi_data_source_status dgi_data_source_status_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_pkey PRIMARY KEY (id);


--
-- Name: dgi_decree dgi_decree_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_decree
    ADD CONSTRAINT dgi_decree_code_key UNIQUE (code);


--
-- Name: dgi_decree dgi_decree_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_decree
    ADD CONSTRAINT dgi_decree_pkey PRIMARY KEY (id);


--
-- Name: dgi_indicator dgi_indicator_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_code_key UNIQUE (code);


--
-- Name: dgi_indicator dgi_indicator_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_pkey PRIMARY KEY (id);


--
-- Name: dgi_indicator_snapshot dgi_indicator_snapshot_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator_snapshot
    ADD CONSTRAINT dgi_indicator_snapshot_pkey PRIMARY KEY (id);


--
-- Name: dgi_initiative dgi_initiative_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_code_key UNIQUE (code);


--
-- Name: dgi_initiative dgi_initiative_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_pkey PRIMARY KEY (id);


--
-- Name: dgi_report dgi_report_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_code_key UNIQUE (code);


--
-- Name: dgi_report dgi_report_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_pkey PRIMARY KEY (id);


--
-- Name: digital_platform digital_platform_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_code_key UNIQUE (code);


--
-- Name: digital_platform digital_platform_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_pkey PRIMARY KEY (id);


--
-- Name: document document_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_code_key UNIQUE (code);


--
-- Name: document document_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_pkey PRIMARY KEY (id);


--
-- Name: electronic_file electronic_file_file_number_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_file_number_key UNIQUE (file_number);


--
-- Name: electronic_file electronic_file_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_pkey PRIMARY KEY (id);


--
-- Name: evaluation_assignment evaluation_assignment_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_pkey PRIMARY KEY (id);


--
-- Name: financial_threshold financial_threshold_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.financial_threshold
    ADD CONSTRAINT financial_threshold_code_key UNIQUE (code);


--
-- Name: financial_threshold financial_threshold_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.financial_threshold
    ADD CONSTRAINT financial_threshold_pkey PRIMARY KEY (id);


--
-- Name: financing_track financing_track_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.financing_track
    ADD CONSTRAINT financing_track_code_key UNIQUE (code);


--
-- Name: financing_track financing_track_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.financing_track
    ADD CONSTRAINT financing_track_pkey PRIMARY KEY (id);


--
-- Name: fril_category fril_category_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fril_category
    ADD CONSTRAINT fril_category_code_key UNIQUE (code);


--
-- Name: fril_category fril_category_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fril_category
    ADD CONSTRAINT fril_category_pkey PRIMARY KEY (id);


--
-- Name: fund_program fund_program_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_code_key UNIQUE (code);


--
-- Name: fund_program fund_program_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_pkey PRIMARY KEY (id);


--
-- Name: installment_milestone installment_milestone_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.installment_milestone
    ADD CONSTRAINT installment_milestone_pkey PRIMARY KEY (installment_id, milestone_id);


--
-- Name: inventory_item inventory_item_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_code_key UNIQUE (code);


--
-- Name: inventory_item inventory_item_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_pkey PRIMARY KEY (id);


--
-- Name: ipr ipr_codigo_bip_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_codigo_bip_key UNIQUE (codigo_bip);


--
-- Name: ipr_mechanism ipr_mechanism_ipr_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_ipr_id_key UNIQUE (ipr_id);


--
-- Name: ipr_mechanism ipr_mechanism_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_pkey PRIMARY KEY (id);


--
-- Name: ipr_milestone ipr_milestone_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_pkey PRIMARY KEY (id);


--
-- Name: ipr_party ipr_party_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_pkey PRIMARY KEY (id);


--
-- Name: ipr ipr_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_pkey PRIMARY KEY (id);


--
-- Name: ipr_problem ipr_problem_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_code_key UNIQUE (code);


--
-- Name: ipr_problem ipr_problem_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_pkey PRIMARY KEY (id);


--
-- Name: ipr_territory ipr_territory_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_pkey PRIMARY KEY (id);


--
-- Name: kinship_declaration kinship_declaration_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT kinship_declaration_pkey PRIMARY KEY (id);


--
-- Name: legal_document legal_document_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_code_key UNIQUE (code);


--
-- Name: legal_document legal_document_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_pkey PRIMARY KEY (id);


--
-- Name: legal_mandate legal_mandate_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_pkey PRIMARY KEY (id);


--
-- Name: minute minute_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_pkey PRIMARY KEY (id);


--
-- Name: minute minute_session_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_session_id_key UNIQUE (session_id);


--
-- Name: operational_commitment operational_commitment_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_code_key UNIQUE (code);


--
-- Name: operational_commitment operational_commitment_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_pkey PRIMARY KEY (id);


--
-- Name: organization organization_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT organization_code_key UNIQUE (code);


--
-- Name: organization organization_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT organization_pkey PRIMARY KEY (id);


--
-- Name: person person_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);


--
-- Name: person person_rut_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_rut_key UNIQUE (rut);


--
-- Name: planning_instrument planning_instrument_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_code_key UNIQUE (code);


--
-- Name: planning_instrument planning_instrument_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_pkey PRIMARY KEY (id);


--
-- Name: position position_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."position"
    ADD CONSTRAINT position_code_key UNIQUE (code);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (id);


--
-- Name: procedure procedure_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_code_key UNIQUE (code);


--
-- Name: procedure procedure_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_pkey PRIMARY KEY (id);


--
-- Name: progress_report progress_report_ipr_id_report_number_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_ipr_id_report_number_key UNIQUE (ipr_id, report_number);


--
-- Name: progress_report progress_report_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_pkey PRIMARY KEY (id);


--
-- Name: rendition_escalation rendition_escalation_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_escalation
    ADD CONSTRAINT rendition_escalation_pkey PRIMARY KEY (id);


--
-- Name: rendition_history rendition_history_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_history
    ADD CONSTRAINT rendition_history_pkey PRIMARY KEY (id);


--
-- Name: rendition_phase rendition_phase_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_phase
    ADD CONSTRAINT rendition_phase_code_key UNIQUE (code);


--
-- Name: rendition_phase rendition_phase_ordinal_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_phase
    ADD CONSTRAINT rendition_phase_ordinal_key UNIQUE (ordinal);


--
-- Name: rendition_phase rendition_phase_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_phase
    ADD CONSTRAINT rendition_phase_pkey PRIMARY KEY (id);


--
-- Name: rendition rendition_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_pkey PRIMARY KEY (id);


--
-- Name: resolution resolution_administrative_act_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_administrative_act_id_key UNIQUE (administrative_act_id);


--
-- Name: resolution resolution_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_pkey PRIMARY KEY (id);


--
-- Name: risk risk_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_code_key UNIQUE (code);


--
-- Name: risk risk_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_pkey PRIMARY KEY (id);


--
-- Name: schema_migration schema_migration_filename_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.schema_migration
    ADD CONSTRAINT schema_migration_filename_key UNIQUE (filename);


--
-- Name: schema_migration schema_migration_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.schema_migration
    ADD CONSTRAINT schema_migration_pkey PRIMARY KEY (id);


--
-- Name: session_agreement session_agreement_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_pkey PRIMARY KEY (id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: session_vote session_vote_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_vote
    ADD CONSTRAINT session_vote_pkey PRIMARY KEY (id);


--
-- Name: session_vote session_vote_session_agreement_id_voter_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_vote
    ADD CONSTRAINT session_vote_session_agreement_id_voter_id_key UNIQUE (session_agreement_id, voter_id);


--
-- Name: sni_level_config sni_level_config_level_number_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.sni_level_config
    ADD CONSTRAINT sni_level_config_level_number_key UNIQUE (level_number);


--
-- Name: sni_level_config sni_level_config_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.sni_level_config
    ADD CONSTRAINT sni_level_config_pkey PRIMARY KEY (id);


--
-- Name: subv8_fund_ceiling subv8_fund_ceiling_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.subv8_fund_ceiling
    ADD CONSTRAINT subv8_fund_ceiling_pkey PRIMARY KEY (id);


--
-- Name: subv8_fund subv8_fund_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.subv8_fund
    ADD CONSTRAINT subv8_fund_code_key UNIQUE (code);


--
-- Name: subv8_fund subv8_fund_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.subv8_fund
    ADD CONSTRAINT subv8_fund_pkey PRIMARY KEY (id);


--
-- Name: territorial_indicator territorial_indicator_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_code_key UNIQUE (code);


--
-- Name: territorial_indicator territorial_indicator_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_pkey PRIMARY KEY (id);


--
-- Name: territory territory_code_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_code_key UNIQUE (code);


--
-- Name: territory territory_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_pkey PRIMARY KEY (id);


--
-- Name: admissibility_check uq_admissibility_check_ipr_item; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_check
    ADD CONSTRAINT uq_admissibility_check_ipr_item UNIQUE (ipr_id, item_id);


--
-- Name: admissibility_item uq_admissibility_item_track_code; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_item
    ADD CONSTRAINT uq_admissibility_item_track_code UNIQUE (financing_track_id, code);


--
-- Name: ipr_party uq_ipr_party_role; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT uq_ipr_party_role UNIQUE (ipr_id, organization_id, party_role_id);


--
-- Name: ipr_territory uq_ipr_territory_impact; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT uq_ipr_territory_impact UNIQUE (ipr_id, territory_id, impact_type_id);


--
-- Name: kinship_declaration uq_kinship_decl; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT uq_kinship_decl UNIQUE (ipr_id, person_id, declaration_type);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_person_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_person_id_key UNIQUE (person_id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_inventory_item_id_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_inventory_item_id_key UNIQUE (inventory_item_id);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_plate_key; Type: CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_plate_key UNIQUE (plate);


--
-- Name: entity entity_code_key; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.entity
    ADD CONSTRAINT entity_code_key UNIQUE (code);


--
-- Name: entity entity_pkey; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.entity
    ADD CONSTRAINT entity_pkey PRIMARY KEY (id);


--
-- Name: process process_code_key; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.process
    ADD CONSTRAINT process_code_key UNIQUE (code);


--
-- Name: process process_pkey; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.process
    ADD CONSTRAINT process_pkey PRIMARY KEY (id);


--
-- Name: role role_code_key; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT role_code_key UNIQUE (code);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: story story_code_key; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT story_code_key UNIQUE (code);


--
-- Name: story_entity story_entity_pkey; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT story_entity_pkey PRIMARY KEY (id);


--
-- Name: story_entity story_entity_story_id_entity_id_key; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT story_entity_story_id_entity_id_key UNIQUE (story_id, entity_id);


--
-- Name: story story_pkey; Type: CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT story_pkey PRIMARY KEY (id);


--
-- Name: acceptance_criteria acceptance_criteria_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.acceptance_criteria
    ADD CONSTRAINT acceptance_criteria_pkey PRIMARY KEY (id);


--
-- Name: bridge_us_entity bridge_us_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_entity
    ADD CONSTRAINT bridge_us_entity_pkey PRIMARY KEY (us_id, entity_id);


--
-- Name: bridge_us_extra_tag bridge_us_extra_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_extra_tag
    ADD CONSTRAINT bridge_us_extra_tag_pkey PRIMARY KEY (us_id, tag);


--
-- Name: dim_entity dim_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_entity
    ADD CONSTRAINT dim_entity_pkey PRIMARY KEY (id);


--
-- Name: dim_extra_tag dim_extra_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_extra_tag
    ADD CONSTRAINT dim_extra_tag_pkey PRIMARY KEY (tag);


--
-- Name: dim_process dim_process_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_process
    ADD CONSTRAINT dim_process_pkey PRIMARY KEY (id);


--
-- Name: dim_role_canonical dim_role_canonical_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_role_canonical
    ADD CONSTRAINT dim_role_canonical_pkey PRIMARY KEY (id);


--
-- Name: dim_role dim_role_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_role
    ADD CONSTRAINT dim_role_pkey PRIMARY KEY (id);


--
-- Name: fact_user_story fact_user_story_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.fact_user_story
    ADD CONSTRAINT fact_user_story_pkey PRIMARY KEY (id);


--
-- Name: role_especialidad role_especialidad_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.role_especialidad
    ADD CONSTRAINT role_especialidad_pkey PRIMARY KEY (role_id, especialidad);


--
-- Name: role_mapping role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.role_mapping
    ADD CONSTRAINT role_mapping_pkey PRIMARY KEY (legacy_id);


--
-- Name: actor actor_code_key; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT actor_code_key UNIQUE (code);


--
-- Name: actor actor_pkey; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id);


--
-- Name: category category_scheme_code_key; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT category_scheme_code_key UNIQUE (scheme, code);


--
-- Name: operational_commitment_type operational_commitment_type_code_key; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.operational_commitment_type
    ADD CONSTRAINT operational_commitment_type_code_key UNIQUE (code);


--
-- Name: operational_commitment_type operational_commitment_type_pkey; Type: CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.operational_commitment_type
    ADD CONSTRAINT operational_commitment_type_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_01 event_2026_01_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_01
    ADD CONSTRAINT event_2026_01_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_02 event_2026_02_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_02
    ADD CONSTRAINT event_2026_02_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_03 event_2026_03_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_03
    ADD CONSTRAINT event_2026_03_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_04 event_2026_04_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_04
    ADD CONSTRAINT event_2026_04_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_05 event_2026_05_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_05
    ADD CONSTRAINT event_2026_05_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_06 event_2026_06_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_06
    ADD CONSTRAINT event_2026_06_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_07 event_2026_07_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_07
    ADD CONSTRAINT event_2026_07_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_08 event_2026_08_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_08
    ADD CONSTRAINT event_2026_08_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_09 event_2026_09_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_09
    ADD CONSTRAINT event_2026_09_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_10 event_2026_10_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_10
    ADD CONSTRAINT event_2026_10_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_11 event_2026_11_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_11
    ADD CONSTRAINT event_2026_11_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_2026_12 event_2026_12_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_2026_12
    ADD CONSTRAINT event_2026_12_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: event_default event_default_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.event_default
    ADD CONSTRAINT event_default_pkey PRIMARY KEY (id, occurred_at);


--
-- Name: magnitude magnitude_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude
    ADD CONSTRAINT magnitude_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude_2026_q1 magnitude_2026_q1_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q1
    ADD CONSTRAINT magnitude_2026_q1_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude magnitude_subject_type_subject_id_aspect_id_as_of_date_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude
    ADD CONSTRAINT magnitude_subject_type_subject_id_aspect_id_as_of_date_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: magnitude_2026_q1 magnitude_2026_q1_subject_type_subject_id_aspect_id_as_of_d_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q1
    ADD CONSTRAINT magnitude_2026_q1_subject_type_subject_id_aspect_id_as_of_d_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: magnitude_2026_q2 magnitude_2026_q2_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q2
    ADD CONSTRAINT magnitude_2026_q2_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude_2026_q2 magnitude_2026_q2_subject_type_subject_id_aspect_id_as_of_d_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q2
    ADD CONSTRAINT magnitude_2026_q2_subject_type_subject_id_aspect_id_as_of_d_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: magnitude_2026_q3 magnitude_2026_q3_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q3
    ADD CONSTRAINT magnitude_2026_q3_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude_2026_q3 magnitude_2026_q3_subject_type_subject_id_aspect_id_as_of_d_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q3
    ADD CONSTRAINT magnitude_2026_q3_subject_type_subject_id_aspect_id_as_of_d_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: magnitude_2026_q4 magnitude_2026_q4_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q4
    ADD CONSTRAINT magnitude_2026_q4_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude_2026_q4 magnitude_2026_q4_subject_type_subject_id_aspect_id_as_of_d_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_2026_q4
    ADD CONSTRAINT magnitude_2026_q4_subject_type_subject_id_aspect_id_as_of_d_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: magnitude_default magnitude_default_pkey; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_default
    ADD CONSTRAINT magnitude_default_pkey PRIMARY KEY (id, as_of_date);


--
-- Name: magnitude_default magnitude_default_subject_type_subject_id_aspect_id_as_of_d_key; Type: CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE ONLY txn.magnitude_default
    ADD CONSTRAINT magnitude_default_subject_type_subject_id_aspect_id_as_of_d_key UNIQUE (subject_type, subject_id, aspect_id, as_of_date);


--
-- Name: idx_act_history_act; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_act_history_act ON core.administrative_act_history USING btree (act_id);


--
-- Name: idx_admin_act_state; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_admin_act_state ON core.administrative_act USING btree (state_id);


--
-- Name: idx_admin_act_type; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_admin_act_type ON core.administrative_act USING btree (act_type_id);


--
-- Name: idx_admissibility_check_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_admissibility_check_ipr ON core.admissibility_check USING btree (ipr_id);


--
-- Name: idx_agreement_active; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_active ON core.agreement USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_agreement_giver; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_giver ON core.agreement USING btree (giver_id);


--
-- Name: idx_agreement_history_agreement; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_history_agreement ON core.agreement_history USING btree (agreement_id);


--
-- Name: idx_agreement_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_ipr ON core.agreement USING btree (ipr_id);


--
-- Name: idx_agreement_metadata; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_metadata ON core.agreement USING gin (metadata jsonb_path_ops);


--
-- Name: idx_agreement_receiver; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_receiver ON core.agreement USING btree (receiver_id);


--
-- Name: idx_agreement_state; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_state ON core.agreement USING btree (state_id);


--
-- Name: idx_agreement_technical_referent; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_technical_referent ON core.agreement USING btree (technical_referent_id) WHERE (technical_referent_id IS NOT NULL);


--
-- Name: idx_agreement_valid_to; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_agreement_valid_to ON core.agreement USING btree (valid_to) WHERE (valid_to IS NOT NULL);


--
-- Name: idx_alert_severity; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_alert_severity ON core.alert USING btree (severity_id, triggered_at);


--
-- Name: idx_alert_subject; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_alert_subject ON core.alert USING btree (subject_type, subject_id);


--
-- Name: idx_alert_unattended; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_alert_unattended ON core.alert USING btree (alert_type_id, severity_id) WHERE (attended_at IS NULL);


--
-- Name: idx_bct_fiscal_year; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_bct_fiscal_year ON core.budget_cycle_tracking USING btree (fiscal_year);


--
-- Name: idx_budget_carryover_program; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_carryover_program ON core.budget_carryover USING btree (budget_program_id);


--
-- Name: idx_budget_carryover_year; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_carryover_year ON core.budget_carryover USING btree (fiscal_year);


--
-- Name: idx_budget_commitment_agreement; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_commitment_agreement ON core.budget_commitment USING btree (agreement_id) WHERE (agreement_id IS NOT NULL);


--
-- Name: idx_budget_commitment_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_commitment_ipr ON core.budget_commitment USING btree (ipr_id) WHERE (ipr_id IS NOT NULL);


--
-- Name: idx_budget_commitment_program; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_commitment_program ON core.budget_commitment USING btree (budget_program_id);


--
-- Name: idx_budget_program_allocation; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_allocation ON core.budget_program USING btree (allocation_id) WHERE (allocation_id IS NOT NULL);


--
-- Name: idx_budget_program_item; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_item ON core.budget_program USING btree (item_id) WHERE (item_id IS NOT NULL);


--
-- Name: idx_budget_program_metadata_gin; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_metadata_gin ON core.budget_program USING gin (metadata);


--
-- Name: idx_budget_program_subtitle; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_subtitle ON core.budget_program USING btree (subtitle_id) WHERE (subtitle_id IS NOT NULL);


--
-- Name: idx_budget_program_year; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_year ON core.budget_program USING btree (fiscal_year);


--
-- Name: idx_budget_program_year_item_allocation; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_budget_program_year_item_allocation ON core.budget_program USING btree (fiscal_year, item_id, allocation_id) WHERE (((fiscal_year >= 2023) AND (fiscal_year <= 2026)) AND (item_id IS NOT NULL) AND (allocation_id IS NOT NULL));


--
-- Name: idx_commitment_division; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_division ON core.operational_commitment USING btree (division_id) WHERE (division_id IS NOT NULL);


--
-- Name: idx_commitment_due; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_due ON core.operational_commitment USING btree (due_date);


--
-- Name: idx_commitment_history_commitment; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_history_commitment ON core.commitment_history USING btree (commitment_id);


--
-- Name: idx_commitment_history_date; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_history_date ON core.commitment_history USING btree (changed_at);


--
-- Name: idx_commitment_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_ipr ON core.operational_commitment USING btree (ipr_id);


--
-- Name: idx_commitment_responsible; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_responsible ON core.operational_commitment USING btree (responsible_id);


--
-- Name: idx_commitment_state; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_commitment_state ON core.operational_commitment USING btree (state_id);


--
-- Name: idx_dgi_decree_status; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_dgi_decree_status ON core.dgi_decree USING btree (status_id);


--
-- Name: idx_dgi_indicator_dimension; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_dgi_indicator_dimension ON core.dgi_indicator USING btree (dimension_id);


--
-- Name: idx_dgi_initiative_responsible; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_dgi_initiative_responsible ON core.dgi_initiative USING btree (responsible_id);


--
-- Name: idx_dgi_initiative_status; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_dgi_initiative_status ON core.dgi_initiative USING btree (status_id);


--
-- Name: idx_dgi_report_type; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_dgi_report_type ON core.dgi_report USING btree (report_type_id);


--
-- Name: idx_document_folio; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_document_folio ON core.document USING btree (file_id, sort_order);


--
-- Name: idx_eval_assignment_evaluator; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_eval_assignment_evaluator ON core.evaluation_assignment USING btree (evaluator_type_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_eval_assignment_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_eval_assignment_ipr ON core.evaluation_assignment USING btree (ipr_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_eval_convocatoria; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_eval_convocatoria ON core.evaluation_assignment USING btree (convocatoria_code) WHERE (convocatoria_code IS NOT NULL);


--
-- Name: idx_indicator_snapshot_lookup; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_indicator_snapshot_lookup ON core.dgi_indicator_snapshot USING btree (indicator_id, recorded_at);


--
-- Name: idx_inst_milestone_inst; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_inst_milestone_inst ON core.installment_milestone USING btree (installment_id);


--
-- Name: idx_inst_milestone_mile; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_inst_milestone_mile ON core.installment_milestone USING btree (milestone_id);


--
-- Name: idx_inst_milestone_required; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_inst_milestone_required ON core.installment_milestone USING btree (installment_id) WHERE (is_required = true);


--
-- Name: idx_installment_agreement; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_installment_agreement ON core.agreement_installment USING btree (agreement_id);


--
-- Name: idx_installment_due; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_installment_due ON core.agreement_installment USING btree (due_date, payment_status_id);


--
-- Name: idx_ipr_active; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_active ON core.ipr USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_ipr_alert; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_alert ON core.ipr USING btree (alert_level_id) WHERE (alert_level_id IS NOT NULL);


--
-- Name: idx_ipr_assignee; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_assignee ON core.ipr USING btree (assignee_id) WHERE (assignee_id IS NOT NULL);


--
-- Name: idx_ipr_fts; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_fts ON core.ipr USING gin (to_tsvector('spanish'::regconfig, COALESCE(name, ''::text)));


--
-- Name: idx_ipr_fund_category; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_fund_category ON core.ipr USING btree (fund_category_id) WHERE (fund_category_id IS NOT NULL);


--
-- Name: idx_ipr_investment_sector; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_investment_sector ON core.ipr USING btree (investment_sector_id) WHERE (investment_sector_id IS NOT NULL);


--
-- Name: idx_ipr_mechanism; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_mechanism ON core.ipr USING btree (mechanism_id);


--
-- Name: idx_ipr_metadata; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_metadata ON core.ipr USING gin (metadata jsonb_path_ops);


--
-- Name: idx_ipr_metadata_gin; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_metadata_gin ON core.ipr USING gin (metadata);


--
-- Name: idx_ipr_municipal_origin; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_municipal_origin ON core.ipr USING btree (is_municipal_origin) WHERE (is_municipal_origin = true);


--
-- Name: idx_ipr_party_agreement; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_agreement ON core.ipr_party USING btree (agreement_id) WHERE (agreement_id IS NOT NULL);


--
-- Name: idx_ipr_party_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_ipr ON core.ipr_party USING btree (ipr_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_ipr_party_org; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_org ON core.ipr_party USING btree (organization_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_ipr_party_primary; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_primary ON core.ipr_party USING btree (ipr_id, party_role_id) WHERE ((is_primary = true) AND (deleted_at IS NULL));


--
-- Name: idx_ipr_party_role; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_role ON core.ipr_party USING btree (party_role_id);


--
-- Name: idx_ipr_party_sponsor_division; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_party_sponsor_division ON core.ipr_party USING btree (sponsor_division_id) WHERE (sponsor_division_id IS NOT NULL);


--
-- Name: idx_ipr_phase; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_phase ON core.ipr USING btree (mcd_phase_id);


--
-- Name: idx_ipr_phase_mechanism; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_phase_mechanism ON core.ipr USING btree (mcd_phase_id, mechanism_id);


--
-- Name: idx_ipr_problem_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_problem_ipr ON core.ipr_problem USING btree (ipr_id);


--
-- Name: idx_ipr_problem_state; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_problem_state ON core.ipr_problem USING btree (state_id);


--
-- Name: idx_ipr_problems; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_problems ON core.ipr USING btree (has_open_problems) WHERE (has_open_problems = true);


--
-- Name: idx_ipr_status; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_status ON core.ipr USING btree (status_id);


--
-- Name: idx_ipr_territory_impact; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_territory_impact ON core.ipr_territory USING btree (impact_type_id);


--
-- Name: idx_ipr_territory_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_territory_ipr ON core.ipr_territory USING btree (ipr_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_ipr_territory_primary; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_territory_primary ON core.ipr_territory USING btree (ipr_id) WHERE ((is_primary = true) AND (deleted_at IS NULL));


--
-- Name: idx_ipr_territory_territory; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_territory_territory ON core.ipr_territory USING btree (territory_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_ipr_year; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_ipr_year ON core.ipr USING btree (EXTRACT(year FROM (created_at AT TIME ZONE 'UTC'::text)));


--
-- Name: idx_kinship_declaration_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_kinship_declaration_ipr ON core.kinship_declaration USING btree (ipr_id);


--
-- Name: idx_milestone_actual; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_actual ON core.ipr_milestone USING btree (actual_date) WHERE (actual_date IS NOT NULL);


--
-- Name: idx_milestone_deviation; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_deviation ON core.ipr_milestone USING btree (deviation_days) WHERE (deviation_days IS NOT NULL);


--
-- Name: idx_milestone_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_ipr ON core.ipr_milestone USING btree (ipr_id) WHERE (deleted_at IS NULL);


--
-- Name: idx_milestone_pending; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_pending ON core.ipr_milestone USING btree (ipr_id, planned_date) WHERE ((actual_date IS NULL) AND (deleted_at IS NULL));


--
-- Name: idx_milestone_planned; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_planned ON core.ipr_milestone USING btree (planned_date);


--
-- Name: idx_milestone_type; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_milestone_type ON core.ipr_milestone USING btree (milestone_type_id);


--
-- Name: idx_org_active; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_org_active ON core.organization USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_org_parent; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_org_parent ON core.organization USING btree (parent_id);


--
-- Name: idx_org_rut; Type: INDEX; Schema: core; Owner: goreos
--

CREATE UNIQUE INDEX idx_org_rut ON core.organization USING btree (rut) WHERE (rut IS NOT NULL);


--
-- Name: idx_org_type; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_org_type ON core.organization USING btree (org_type_id);


--
-- Name: idx_person_active; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_person_active ON core.person USING btree (id) WHERE ((deleted_at IS NULL) AND (is_active = true));


--
-- Name: idx_person_estamento; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_person_estamento ON core.person USING btree (estamento_id) WHERE (estamento_id IS NOT NULL);


--
-- Name: idx_person_org; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_person_org ON core.person USING btree (organization_id);


--
-- Name: idx_problem_fts; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_problem_fts ON core.ipr_problem USING gin (to_tsvector('spanish'::regconfig, ((COALESCE(description, ''::text) || ' '::text) || COALESCE(solution_applied, ''::text))));


--
-- Name: idx_problem_unresolved; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_problem_unresolved ON core.ipr_problem USING btree (detected_at) WHERE ((resolved_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: idx_progress_report_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_progress_report_ipr ON core.progress_report USING btree (ipr_id);


--
-- Name: idx_rendition_archived; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_rendition_archived ON core.rendition USING btree (archived_at) WHERE ((archived_at IS NOT NULL) AND (deleted_at IS NULL));


--
-- Name: idx_rendition_escalation_rendition; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_rendition_escalation_rendition ON core.rendition_escalation USING btree (rendition_id);


--
-- Name: idx_rendition_history_rendition; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_rendition_history_rendition ON core.rendition_history USING btree (rendition_id);


--
-- Name: idx_rendition_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_rendition_ipr ON core.rendition USING btree (ipr_id) WHERE (ipr_id IS NOT NULL);


--
-- Name: idx_rendition_responsible; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_rendition_responsible ON core.rendition USING btree (responsible_id) WHERE ((responsible_id IS NOT NULL) AND (deleted_at IS NULL));


--
-- Name: idx_resolution_ipr; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_resolution_ipr ON core.resolution USING btree (ipr_id);


--
-- Name: idx_session_vote_agreement; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_session_vote_agreement ON core.session_vote USING btree (session_agreement_id);


--
-- Name: idx_session_vote_voter; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_session_vote_voter ON core.session_vote USING btree (voter_id);


--
-- Name: idx_subv8_fund_ceiling_fund; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_subv8_fund_ceiling_fund ON core.subv8_fund_ceiling USING btree (fund_id);


--
-- Name: idx_territory_parent; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_territory_parent ON core.territory USING btree (parent_id, territory_type_id);


--
-- Name: idx_user_active; Type: INDEX; Schema: core; Owner: goreos
--

CREATE INDEX idx_user_active ON core."user" USING btree (is_active, system_role_id) WHERE ((is_active = true) AND (deleted_at IS NULL));


--
-- Name: uq_subv8_ceiling_fund_type_area; Type: INDEX; Schema: core; Owner: goreos
--

CREATE UNIQUE INDEX uq_subv8_ceiling_fund_type_area ON core.subv8_fund_ceiling USING btree (fund_id, institution_type, COALESCE(area, ''::character varying));


--
-- Name: idx_entity_active; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_entity_active ON meta.entity USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_entity_domain; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_entity_domain ON meta.entity USING btree (domain);


--
-- Name: idx_process_active; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_process_active ON meta.process USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_process_layer; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_process_layer ON meta.process USING btree (layer);


--
-- Name: idx_role_active; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_role_active ON meta.role USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_role_agent_type; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_role_agent_type ON meta.role USING btree (agent_type);


--
-- Name: idx_story_active; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_active ON meta.story USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_story_domain; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_domain ON meta.story USING btree (domain);


--
-- Name: idx_story_entity_entity; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_entity_entity ON meta.story_entity USING btree (entity_id);


--
-- Name: idx_story_entity_story; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_entity_story ON meta.story_entity USING btree (story_id);


--
-- Name: idx_story_process; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_process ON meta.story USING btree (process_id);


--
-- Name: idx_story_role; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_role ON meta.story USING btree (role_id);


--
-- Name: idx_story_status; Type: INDEX; Schema: meta; Owner: goreos
--

CREATE INDEX idx_story_status ON meta.story USING btree (status);


--
-- Name: idx_role_canonical_agent_type; Type: INDEX; Schema: public; Owner: goreos
--

CREATE INDEX idx_role_canonical_agent_type ON public.dim_role_canonical USING btree (agent_type);


--
-- Name: idx_role_canonical_division; Type: INDEX; Schema: public; Owner: goreos
--

CREATE INDEX idx_role_canonical_division ON public.dim_role_canonical USING btree (division);


--
-- Name: idx_role_legacy_canonical; Type: INDEX; Schema: public; Owner: goreos
--

CREATE INDEX idx_role_legacy_canonical ON public.dim_role USING btree (canonical_id);


--
-- Name: idx_actor_active; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_actor_active ON ref.actor USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_actor_agent_type; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_actor_agent_type ON ref.actor USING btree (agent_type);


--
-- Name: idx_actor_internal; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_actor_internal ON ref.actor USING btree (is_internal);


--
-- Name: idx_category_active; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_category_active ON ref.category USING btree (id) WHERE (deleted_at IS NULL);


--
-- Name: idx_category_parent; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_category_parent ON ref.category USING btree (parent_id) WHERE (parent_id IS NOT NULL);


--
-- Name: idx_category_phase; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_category_phase ON ref.category USING btree (phase_id) WHERE (phase_id IS NOT NULL);


--
-- Name: idx_category_scheme; Type: INDEX; Schema: ref; Owner: goreos
--

CREATE INDEX idx_category_scheme ON ref.category USING btree (scheme);


--
-- Name: idx_event_actor; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_actor ON ONLY txn.event USING btree (actor_id);


--
-- Name: event_2026_01_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_actor_id_idx ON txn.event_2026_01 USING btree (actor_id);


--
-- Name: idx_event_actor_ref; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_actor_ref ON ONLY txn.event USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_01_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_actor_ref_id_idx ON txn.event_2026_01 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: idx_event_created_by; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_created_by ON ONLY txn.event USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_01_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_created_by_id_idx ON txn.event_2026_01 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: idx_event_type; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_type ON ONLY txn.event USING btree (event_type_id);


--
-- Name: event_2026_01_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_event_type_id_idx ON txn.event_2026_01 USING btree (event_type_id);


--
-- Name: idx_event_occurred; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_occurred ON ONLY txn.event USING btree (occurred_at);


--
-- Name: event_2026_01_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_occurred_at_idx ON txn.event_2026_01 USING btree (occurred_at);


--
-- Name: idx_event_subject; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_event_subject ON ONLY txn.event USING btree (subject_type, subject_id);


--
-- Name: event_2026_01_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_01_subject_type_subject_id_idx ON txn.event_2026_01 USING btree (subject_type, subject_id);


--
-- Name: event_2026_02_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_actor_id_idx ON txn.event_2026_02 USING btree (actor_id);


--
-- Name: event_2026_02_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_actor_ref_id_idx ON txn.event_2026_02 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_02_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_created_by_id_idx ON txn.event_2026_02 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_02_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_event_type_id_idx ON txn.event_2026_02 USING btree (event_type_id);


--
-- Name: event_2026_02_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_occurred_at_idx ON txn.event_2026_02 USING btree (occurred_at);


--
-- Name: event_2026_02_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_02_subject_type_subject_id_idx ON txn.event_2026_02 USING btree (subject_type, subject_id);


--
-- Name: event_2026_03_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_actor_id_idx ON txn.event_2026_03 USING btree (actor_id);


--
-- Name: event_2026_03_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_actor_ref_id_idx ON txn.event_2026_03 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_03_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_created_by_id_idx ON txn.event_2026_03 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_03_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_event_type_id_idx ON txn.event_2026_03 USING btree (event_type_id);


--
-- Name: event_2026_03_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_occurred_at_idx ON txn.event_2026_03 USING btree (occurred_at);


--
-- Name: event_2026_03_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_03_subject_type_subject_id_idx ON txn.event_2026_03 USING btree (subject_type, subject_id);


--
-- Name: event_2026_04_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_actor_id_idx ON txn.event_2026_04 USING btree (actor_id);


--
-- Name: event_2026_04_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_actor_ref_id_idx ON txn.event_2026_04 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_04_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_created_by_id_idx ON txn.event_2026_04 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_04_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_event_type_id_idx ON txn.event_2026_04 USING btree (event_type_id);


--
-- Name: event_2026_04_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_occurred_at_idx ON txn.event_2026_04 USING btree (occurred_at);


--
-- Name: event_2026_04_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_04_subject_type_subject_id_idx ON txn.event_2026_04 USING btree (subject_type, subject_id);


--
-- Name: event_2026_05_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_actor_id_idx ON txn.event_2026_05 USING btree (actor_id);


--
-- Name: event_2026_05_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_actor_ref_id_idx ON txn.event_2026_05 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_05_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_created_by_id_idx ON txn.event_2026_05 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_05_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_event_type_id_idx ON txn.event_2026_05 USING btree (event_type_id);


--
-- Name: event_2026_05_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_occurred_at_idx ON txn.event_2026_05 USING btree (occurred_at);


--
-- Name: event_2026_05_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_05_subject_type_subject_id_idx ON txn.event_2026_05 USING btree (subject_type, subject_id);


--
-- Name: event_2026_06_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_actor_id_idx ON txn.event_2026_06 USING btree (actor_id);


--
-- Name: event_2026_06_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_actor_ref_id_idx ON txn.event_2026_06 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_06_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_created_by_id_idx ON txn.event_2026_06 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_06_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_event_type_id_idx ON txn.event_2026_06 USING btree (event_type_id);


--
-- Name: event_2026_06_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_occurred_at_idx ON txn.event_2026_06 USING btree (occurred_at);


--
-- Name: event_2026_06_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_06_subject_type_subject_id_idx ON txn.event_2026_06 USING btree (subject_type, subject_id);


--
-- Name: event_2026_07_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_actor_id_idx ON txn.event_2026_07 USING btree (actor_id);


--
-- Name: event_2026_07_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_actor_ref_id_idx ON txn.event_2026_07 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_07_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_created_by_id_idx ON txn.event_2026_07 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_07_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_event_type_id_idx ON txn.event_2026_07 USING btree (event_type_id);


--
-- Name: event_2026_07_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_occurred_at_idx ON txn.event_2026_07 USING btree (occurred_at);


--
-- Name: event_2026_07_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_07_subject_type_subject_id_idx ON txn.event_2026_07 USING btree (subject_type, subject_id);


--
-- Name: event_2026_08_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_actor_id_idx ON txn.event_2026_08 USING btree (actor_id);


--
-- Name: event_2026_08_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_actor_ref_id_idx ON txn.event_2026_08 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_08_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_created_by_id_idx ON txn.event_2026_08 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_08_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_event_type_id_idx ON txn.event_2026_08 USING btree (event_type_id);


--
-- Name: event_2026_08_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_occurred_at_idx ON txn.event_2026_08 USING btree (occurred_at);


--
-- Name: event_2026_08_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_08_subject_type_subject_id_idx ON txn.event_2026_08 USING btree (subject_type, subject_id);


--
-- Name: event_2026_09_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_actor_id_idx ON txn.event_2026_09 USING btree (actor_id);


--
-- Name: event_2026_09_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_actor_ref_id_idx ON txn.event_2026_09 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_09_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_created_by_id_idx ON txn.event_2026_09 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_09_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_event_type_id_idx ON txn.event_2026_09 USING btree (event_type_id);


--
-- Name: event_2026_09_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_occurred_at_idx ON txn.event_2026_09 USING btree (occurred_at);


--
-- Name: event_2026_09_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_09_subject_type_subject_id_idx ON txn.event_2026_09 USING btree (subject_type, subject_id);


--
-- Name: event_2026_10_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_actor_id_idx ON txn.event_2026_10 USING btree (actor_id);


--
-- Name: event_2026_10_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_actor_ref_id_idx ON txn.event_2026_10 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_10_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_created_by_id_idx ON txn.event_2026_10 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_10_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_event_type_id_idx ON txn.event_2026_10 USING btree (event_type_id);


--
-- Name: event_2026_10_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_occurred_at_idx ON txn.event_2026_10 USING btree (occurred_at);


--
-- Name: event_2026_10_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_10_subject_type_subject_id_idx ON txn.event_2026_10 USING btree (subject_type, subject_id);


--
-- Name: event_2026_11_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_actor_id_idx ON txn.event_2026_11 USING btree (actor_id);


--
-- Name: event_2026_11_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_actor_ref_id_idx ON txn.event_2026_11 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_11_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_created_by_id_idx ON txn.event_2026_11 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_11_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_event_type_id_idx ON txn.event_2026_11 USING btree (event_type_id);


--
-- Name: event_2026_11_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_occurred_at_idx ON txn.event_2026_11 USING btree (occurred_at);


--
-- Name: event_2026_11_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_11_subject_type_subject_id_idx ON txn.event_2026_11 USING btree (subject_type, subject_id);


--
-- Name: event_2026_12_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_actor_id_idx ON txn.event_2026_12 USING btree (actor_id);


--
-- Name: event_2026_12_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_actor_ref_id_idx ON txn.event_2026_12 USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_2026_12_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_created_by_id_idx ON txn.event_2026_12 USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_2026_12_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_event_type_id_idx ON txn.event_2026_12 USING btree (event_type_id);


--
-- Name: event_2026_12_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_occurred_at_idx ON txn.event_2026_12 USING btree (occurred_at);


--
-- Name: event_2026_12_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_2026_12_subject_type_subject_id_idx ON txn.event_2026_12 USING btree (subject_type, subject_id);


--
-- Name: event_default_actor_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_actor_id_idx ON txn.event_default USING btree (actor_id);


--
-- Name: event_default_actor_ref_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_actor_ref_id_idx ON txn.event_default USING btree (actor_ref_id) WHERE (actor_ref_id IS NOT NULL);


--
-- Name: event_default_created_by_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_created_by_id_idx ON txn.event_default USING btree (created_by_id) WHERE (created_by_id IS NOT NULL);


--
-- Name: event_default_event_type_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_event_type_id_idx ON txn.event_default USING btree (event_type_id);


--
-- Name: event_default_occurred_at_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_occurred_at_idx ON txn.event_default USING btree (occurred_at);


--
-- Name: event_default_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX event_default_subject_type_subject_id_idx ON txn.event_default USING btree (subject_type, subject_id);


--
-- Name: idx_magnitude_aspect; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_magnitude_aspect ON ONLY txn.magnitude USING btree (aspect_id);


--
-- Name: idx_magnitude_date; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_magnitude_date ON ONLY txn.magnitude USING btree (as_of_date);


--
-- Name: idx_magnitude_subject; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX idx_magnitude_subject ON ONLY txn.magnitude USING btree (subject_type, subject_id);


--
-- Name: magnitude_2026_q1_as_of_date_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q1_as_of_date_idx ON txn.magnitude_2026_q1 USING btree (as_of_date);


--
-- Name: magnitude_2026_q1_aspect_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q1_aspect_id_idx ON txn.magnitude_2026_q1 USING btree (aspect_id);


--
-- Name: magnitude_2026_q1_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q1_subject_type_subject_id_idx ON txn.magnitude_2026_q1 USING btree (subject_type, subject_id);


--
-- Name: magnitude_2026_q2_as_of_date_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q2_as_of_date_idx ON txn.magnitude_2026_q2 USING btree (as_of_date);


--
-- Name: magnitude_2026_q2_aspect_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q2_aspect_id_idx ON txn.magnitude_2026_q2 USING btree (aspect_id);


--
-- Name: magnitude_2026_q2_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q2_subject_type_subject_id_idx ON txn.magnitude_2026_q2 USING btree (subject_type, subject_id);


--
-- Name: magnitude_2026_q3_as_of_date_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q3_as_of_date_idx ON txn.magnitude_2026_q3 USING btree (as_of_date);


--
-- Name: magnitude_2026_q3_aspect_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q3_aspect_id_idx ON txn.magnitude_2026_q3 USING btree (aspect_id);


--
-- Name: magnitude_2026_q3_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q3_subject_type_subject_id_idx ON txn.magnitude_2026_q3 USING btree (subject_type, subject_id);


--
-- Name: magnitude_2026_q4_as_of_date_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q4_as_of_date_idx ON txn.magnitude_2026_q4 USING btree (as_of_date);


--
-- Name: magnitude_2026_q4_aspect_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q4_aspect_id_idx ON txn.magnitude_2026_q4 USING btree (aspect_id);


--
-- Name: magnitude_2026_q4_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_2026_q4_subject_type_subject_id_idx ON txn.magnitude_2026_q4 USING btree (subject_type, subject_id);


--
-- Name: magnitude_default_as_of_date_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_default_as_of_date_idx ON txn.magnitude_default USING btree (as_of_date);


--
-- Name: magnitude_default_aspect_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_default_aspect_id_idx ON txn.magnitude_default USING btree (aspect_id);


--
-- Name: magnitude_default_subject_type_subject_id_idx; Type: INDEX; Schema: txn; Owner: goreos
--

CREATE INDEX magnitude_default_subject_type_subject_id_idx ON txn.magnitude_default USING btree (subject_type, subject_id);


--
-- Name: event_2026_01_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_01_actor_id_idx;


--
-- Name: event_2026_01_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_01_actor_ref_id_idx;


--
-- Name: event_2026_01_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_01_created_by_id_idx;


--
-- Name: event_2026_01_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_01_event_type_id_idx;


--
-- Name: event_2026_01_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_01_occurred_at_idx;


--
-- Name: event_2026_01_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_01_pkey;


--
-- Name: event_2026_01_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_01_subject_type_subject_id_idx;


--
-- Name: event_2026_02_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_02_actor_id_idx;


--
-- Name: event_2026_02_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_02_actor_ref_id_idx;


--
-- Name: event_2026_02_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_02_created_by_id_idx;


--
-- Name: event_2026_02_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_02_event_type_id_idx;


--
-- Name: event_2026_02_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_02_occurred_at_idx;


--
-- Name: event_2026_02_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_02_pkey;


--
-- Name: event_2026_02_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_02_subject_type_subject_id_idx;


--
-- Name: event_2026_03_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_03_actor_id_idx;


--
-- Name: event_2026_03_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_03_actor_ref_id_idx;


--
-- Name: event_2026_03_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_03_created_by_id_idx;


--
-- Name: event_2026_03_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_03_event_type_id_idx;


--
-- Name: event_2026_03_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_03_occurred_at_idx;


--
-- Name: event_2026_03_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_03_pkey;


--
-- Name: event_2026_03_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_03_subject_type_subject_id_idx;


--
-- Name: event_2026_04_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_04_actor_id_idx;


--
-- Name: event_2026_04_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_04_actor_ref_id_idx;


--
-- Name: event_2026_04_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_04_created_by_id_idx;


--
-- Name: event_2026_04_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_04_event_type_id_idx;


--
-- Name: event_2026_04_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_04_occurred_at_idx;


--
-- Name: event_2026_04_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_04_pkey;


--
-- Name: event_2026_04_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_04_subject_type_subject_id_idx;


--
-- Name: event_2026_05_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_05_actor_id_idx;


--
-- Name: event_2026_05_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_05_actor_ref_id_idx;


--
-- Name: event_2026_05_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_05_created_by_id_idx;


--
-- Name: event_2026_05_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_05_event_type_id_idx;


--
-- Name: event_2026_05_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_05_occurred_at_idx;


--
-- Name: event_2026_05_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_05_pkey;


--
-- Name: event_2026_05_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_05_subject_type_subject_id_idx;


--
-- Name: event_2026_06_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_06_actor_id_idx;


--
-- Name: event_2026_06_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_06_actor_ref_id_idx;


--
-- Name: event_2026_06_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_06_created_by_id_idx;


--
-- Name: event_2026_06_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_06_event_type_id_idx;


--
-- Name: event_2026_06_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_06_occurred_at_idx;


--
-- Name: event_2026_06_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_06_pkey;


--
-- Name: event_2026_06_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_06_subject_type_subject_id_idx;


--
-- Name: event_2026_07_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_07_actor_id_idx;


--
-- Name: event_2026_07_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_07_actor_ref_id_idx;


--
-- Name: event_2026_07_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_07_created_by_id_idx;


--
-- Name: event_2026_07_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_07_event_type_id_idx;


--
-- Name: event_2026_07_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_07_occurred_at_idx;


--
-- Name: event_2026_07_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_07_pkey;


--
-- Name: event_2026_07_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_07_subject_type_subject_id_idx;


--
-- Name: event_2026_08_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_08_actor_id_idx;


--
-- Name: event_2026_08_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_08_actor_ref_id_idx;


--
-- Name: event_2026_08_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_08_created_by_id_idx;


--
-- Name: event_2026_08_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_08_event_type_id_idx;


--
-- Name: event_2026_08_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_08_occurred_at_idx;


--
-- Name: event_2026_08_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_08_pkey;


--
-- Name: event_2026_08_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_08_subject_type_subject_id_idx;


--
-- Name: event_2026_09_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_09_actor_id_idx;


--
-- Name: event_2026_09_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_09_actor_ref_id_idx;


--
-- Name: event_2026_09_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_09_created_by_id_idx;


--
-- Name: event_2026_09_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_09_event_type_id_idx;


--
-- Name: event_2026_09_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_09_occurred_at_idx;


--
-- Name: event_2026_09_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_09_pkey;


--
-- Name: event_2026_09_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_09_subject_type_subject_id_idx;


--
-- Name: event_2026_10_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_10_actor_id_idx;


--
-- Name: event_2026_10_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_10_actor_ref_id_idx;


--
-- Name: event_2026_10_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_10_created_by_id_idx;


--
-- Name: event_2026_10_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_10_event_type_id_idx;


--
-- Name: event_2026_10_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_10_occurred_at_idx;


--
-- Name: event_2026_10_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_10_pkey;


--
-- Name: event_2026_10_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_10_subject_type_subject_id_idx;


--
-- Name: event_2026_11_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_11_actor_id_idx;


--
-- Name: event_2026_11_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_11_actor_ref_id_idx;


--
-- Name: event_2026_11_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_11_created_by_id_idx;


--
-- Name: event_2026_11_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_11_event_type_id_idx;


--
-- Name: event_2026_11_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_11_occurred_at_idx;


--
-- Name: event_2026_11_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_11_pkey;


--
-- Name: event_2026_11_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_11_subject_type_subject_id_idx;


--
-- Name: event_2026_12_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_2026_12_actor_id_idx;


--
-- Name: event_2026_12_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_2026_12_actor_ref_id_idx;


--
-- Name: event_2026_12_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_2026_12_created_by_id_idx;


--
-- Name: event_2026_12_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_2026_12_event_type_id_idx;


--
-- Name: event_2026_12_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_2026_12_occurred_at_idx;


--
-- Name: event_2026_12_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_2026_12_pkey;


--
-- Name: event_2026_12_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_2026_12_subject_type_subject_id_idx;


--
-- Name: event_default_actor_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor ATTACH PARTITION txn.event_default_actor_id_idx;


--
-- Name: event_default_actor_ref_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_actor_ref ATTACH PARTITION txn.event_default_actor_ref_id_idx;


--
-- Name: event_default_created_by_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_created_by ATTACH PARTITION txn.event_default_created_by_id_idx;


--
-- Name: event_default_event_type_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_type ATTACH PARTITION txn.event_default_event_type_id_idx;


--
-- Name: event_default_occurred_at_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_occurred ATTACH PARTITION txn.event_default_occurred_at_idx;


--
-- Name: event_default_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.event_pkey ATTACH PARTITION txn.event_default_pkey;


--
-- Name: event_default_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_event_subject ATTACH PARTITION txn.event_default_subject_type_subject_id_idx;


--
-- Name: magnitude_2026_q1_as_of_date_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_date ATTACH PARTITION txn.magnitude_2026_q1_as_of_date_idx;


--
-- Name: magnitude_2026_q1_aspect_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_aspect ATTACH PARTITION txn.magnitude_2026_q1_aspect_id_idx;


--
-- Name: magnitude_2026_q1_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_pkey ATTACH PARTITION txn.magnitude_2026_q1_pkey;


--
-- Name: magnitude_2026_q1_subject_type_subject_id_aspect_id_as_of_d_key; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_subject_type_subject_id_aspect_id_as_of_date_key ATTACH PARTITION txn.magnitude_2026_q1_subject_type_subject_id_aspect_id_as_of_d_key;


--
-- Name: magnitude_2026_q1_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_subject ATTACH PARTITION txn.magnitude_2026_q1_subject_type_subject_id_idx;


--
-- Name: magnitude_2026_q2_as_of_date_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_date ATTACH PARTITION txn.magnitude_2026_q2_as_of_date_idx;


--
-- Name: magnitude_2026_q2_aspect_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_aspect ATTACH PARTITION txn.magnitude_2026_q2_aspect_id_idx;


--
-- Name: magnitude_2026_q2_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_pkey ATTACH PARTITION txn.magnitude_2026_q2_pkey;


--
-- Name: magnitude_2026_q2_subject_type_subject_id_aspect_id_as_of_d_key; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_subject_type_subject_id_aspect_id_as_of_date_key ATTACH PARTITION txn.magnitude_2026_q2_subject_type_subject_id_aspect_id_as_of_d_key;


--
-- Name: magnitude_2026_q2_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_subject ATTACH PARTITION txn.magnitude_2026_q2_subject_type_subject_id_idx;


--
-- Name: magnitude_2026_q3_as_of_date_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_date ATTACH PARTITION txn.magnitude_2026_q3_as_of_date_idx;


--
-- Name: magnitude_2026_q3_aspect_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_aspect ATTACH PARTITION txn.magnitude_2026_q3_aspect_id_idx;


--
-- Name: magnitude_2026_q3_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_pkey ATTACH PARTITION txn.magnitude_2026_q3_pkey;


--
-- Name: magnitude_2026_q3_subject_type_subject_id_aspect_id_as_of_d_key; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_subject_type_subject_id_aspect_id_as_of_date_key ATTACH PARTITION txn.magnitude_2026_q3_subject_type_subject_id_aspect_id_as_of_d_key;


--
-- Name: magnitude_2026_q3_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_subject ATTACH PARTITION txn.magnitude_2026_q3_subject_type_subject_id_idx;


--
-- Name: magnitude_2026_q4_as_of_date_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_date ATTACH PARTITION txn.magnitude_2026_q4_as_of_date_idx;


--
-- Name: magnitude_2026_q4_aspect_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_aspect ATTACH PARTITION txn.magnitude_2026_q4_aspect_id_idx;


--
-- Name: magnitude_2026_q4_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_pkey ATTACH PARTITION txn.magnitude_2026_q4_pkey;


--
-- Name: magnitude_2026_q4_subject_type_subject_id_aspect_id_as_of_d_key; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_subject_type_subject_id_aspect_id_as_of_date_key ATTACH PARTITION txn.magnitude_2026_q4_subject_type_subject_id_aspect_id_as_of_d_key;


--
-- Name: magnitude_2026_q4_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_subject ATTACH PARTITION txn.magnitude_2026_q4_subject_type_subject_id_idx;


--
-- Name: magnitude_default_as_of_date_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_date ATTACH PARTITION txn.magnitude_default_as_of_date_idx;


--
-- Name: magnitude_default_aspect_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_aspect ATTACH PARTITION txn.magnitude_default_aspect_id_idx;


--
-- Name: magnitude_default_pkey; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_pkey ATTACH PARTITION txn.magnitude_default_pkey;


--
-- Name: magnitude_default_subject_type_subject_id_aspect_id_as_of_d_key; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.magnitude_subject_type_subject_id_aspect_id_as_of_date_key ATTACH PARTITION txn.magnitude_default_subject_type_subject_id_aspect_id_as_of_d_key;


--
-- Name: magnitude_default_subject_type_subject_id_idx; Type: INDEX ATTACH; Schema: txn; Owner: goreos
--

ALTER INDEX txn.idx_magnitude_subject ATTACH PARTITION txn.magnitude_default_subject_type_subject_id_idx;


--
-- Name: administrative_act trg_act_history; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_act_history AFTER UPDATE ON core.administrative_act FOR EACH ROW EXECUTE FUNCTION public.fn_act_history();


--
-- Name: administrative_act trg_act_state_transition; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_act_state_transition BEFORE UPDATE OF state_id ON core.administrative_act FOR EACH ROW EXECUTE FUNCTION public.fn_validate_state_transition('state_id');


--
-- Name: administrative_act trg_administrative_act_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_administrative_act_updated_at BEFORE UPDATE ON core.administrative_act FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: administrative_procedure trg_administrative_procedure_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_administrative_procedure_updated_at BEFORE UPDATE ON core.administrative_procedure FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: agreement trg_agreement_history; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_agreement_history AFTER UPDATE ON core.agreement FOR EACH ROW EXECUTE FUNCTION public.fn_agreement_history();


--
-- Name: agreement_installment trg_agreement_installment_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_agreement_installment_updated_at BEFORE UPDATE ON core.agreement_installment FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: agreement trg_agreement_state_transition; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_agreement_state_transition BEFORE UPDATE OF state_id ON core.agreement FOR EACH ROW EXECUTE FUNCTION public.fn_validate_state_transition('state_id');


--
-- Name: agreement trg_agreement_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_agreement_updated_at BEFORE UPDATE ON core.agreement FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: agreement trg_agreement_validate_schemes; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_agreement_validate_schemes BEFORE INSERT OR UPDATE ON core.agreement FOR EACH ROW EXECUTE FUNCTION public.fn_validate_agreement_schemes();


--
-- Name: alert trg_alert_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_alert_updated_at BEFORE UPDATE ON core.alert FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: budget_carryover trg_budget_carryover_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_budget_carryover_updated_at BEFORE UPDATE ON core.budget_carryover FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: budget_commitment trg_budget_commitment_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_budget_commitment_updated_at BEFORE UPDATE ON core.budget_commitment FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: budget_program trg_budget_program_current; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_budget_program_current BEFORE INSERT OR UPDATE ON core.budget_program FOR EACH ROW EXECUTE FUNCTION public.fn_budget_program_current_amount();


--
-- Name: budget_program trg_budget_program_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_budget_program_updated_at BEFORE UPDATE ON core.budget_program FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: committee_member trg_committee_member_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_committee_member_updated_at BEFORE UPDATE ON core.committee_member FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: committee trg_committee_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_committee_updated_at BEFORE UPDATE ON core.committee FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: digital_platform trg_digital_platform_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_digital_platform_updated_at BEFORE UPDATE ON core.digital_platform FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: document trg_document_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_document_updated_at BEFORE UPDATE ON core.document FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: electronic_file trg_electronic_file_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_electronic_file_updated_at BEFORE UPDATE ON core.electronic_file FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: electronic_file trg_file_status_transition; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_file_status_transition BEFORE UPDATE OF status_id ON core.electronic_file FOR EACH ROW EXECUTE FUNCTION public.fn_validate_state_transition('status_id');


--
-- Name: fund_program trg_fund_program_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_fund_program_updated_at BEFORE UPDATE ON core.fund_program FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: agreement_installment trg_installment_payment_transition; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_installment_payment_transition BEFORE UPDATE OF payment_status_id ON core.agreement_installment FOR EACH ROW EXECUTE FUNCTION public.fn_validate_state_transition('payment_status_id');


--
-- Name: inventory_item trg_inventory_item_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_inventory_item_updated_at BEFORE UPDATE ON core.inventory_item FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: ipr_mechanism trg_ipr_mechanism_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_mechanism_updated_at BEFORE UPDATE ON core.ipr_mechanism FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: ipr_milestone trg_ipr_milestone_validate_schemes; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_milestone_validate_schemes BEFORE INSERT OR UPDATE ON core.ipr_milestone FOR EACH ROW EXECUTE FUNCTION public.fn_validate_ipr_milestone_schemes();


--
-- Name: ipr_party trg_ipr_party_single_primary; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_party_single_primary BEFORE INSERT OR UPDATE OF is_primary ON core.ipr_party FOR EACH ROW WHEN ((new.is_primary = true)) EXECUTE FUNCTION public.fn_ensure_single_primary_party();


--
-- Name: ipr_party trg_ipr_party_validate_schemes; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_party_validate_schemes BEFORE INSERT OR UPDATE ON core.ipr_party FOR EACH ROW EXECUTE FUNCTION public.fn_validate_ipr_party_schemes();


--
-- Name: ipr_problem trg_ipr_problem_flag; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_problem_flag AFTER INSERT OR DELETE OR UPDATE ON core.ipr_problem FOR EACH ROW EXECUTE FUNCTION public.fn_update_ipr_problems_flag();


--
-- Name: ipr_problem trg_ipr_problem_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_problem_updated_at BEFORE UPDATE ON core.ipr_problem FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: ipr trg_ipr_state_transition; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_state_transition BEFORE UPDATE OF status_id ON core.ipr FOR EACH ROW EXECUTE FUNCTION public.fn_validate_state_transition('status_id');


--
-- Name: ipr_territory trg_ipr_territory_single_primary; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_territory_single_primary BEFORE INSERT OR UPDATE OF is_primary ON core.ipr_territory FOR EACH ROW WHEN ((new.is_primary = true)) EXECUTE FUNCTION public.fn_ensure_single_primary_territory();


--
-- Name: ipr_territory trg_ipr_territory_validate_schemes; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_territory_validate_schemes BEFORE INSERT OR UPDATE ON core.ipr_territory FOR EACH ROW EXECUTE FUNCTION public.fn_validate_ipr_territory_schemes();


--
-- Name: ipr trg_ipr_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_updated_at BEFORE UPDATE ON core.ipr FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: ipr trg_ipr_validate_schemes; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_ipr_validate_schemes BEFORE INSERT OR UPDATE ON core.ipr FOR EACH ROW EXECUTE FUNCTION public.fn_validate_ipr_schemes();


--
-- Name: legal_document trg_legal_document_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_legal_document_updated_at BEFORE UPDATE ON core.legal_document FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: legal_mandate trg_legal_mandate_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_legal_mandate_updated_at BEFORE UPDATE ON core.legal_mandate FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: ipr_mechanism trg_mechanism_validate_attrs; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_mechanism_validate_attrs BEFORE INSERT OR UPDATE ON core.ipr_mechanism FOR EACH ROW EXECUTE FUNCTION public.fn_validate_mechanism_attrs();


--
-- Name: TRIGGER trg_mechanism_validate_attrs ON ipr_mechanism; Type: COMMENT; Schema: core; Owner: goreos
--

COMMENT ON TRIGGER trg_mechanism_validate_attrs ON core.ipr_mechanism IS 'PRO-001 FIX: Valida atributos específicos por mecanismo para garantizar coproducto controlado';


--
-- Name: organization trg_organization_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_organization_updated_at BEFORE UPDATE ON core.organization FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: person trg_person_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_person_updated_at BEFORE UPDATE ON core.person FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: planning_instrument trg_planning_instrument_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_planning_instrument_updated_at BEFORE UPDATE ON core.planning_instrument FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: procedure trg_procedure_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_procedure_updated_at BEFORE UPDATE ON core.procedure FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: progress_report trg_progress_report_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_progress_report_updated_at BEFORE UPDATE ON core.progress_report FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: rendition trg_rendition_history; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_rendition_history AFTER UPDATE ON core.rendition FOR EACH ROW EXECUTE FUNCTION public.fn_rendition_history();


--
-- Name: rendition trg_rendition_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_rendition_updated_at BEFORE UPDATE ON core.rendition FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: resolution trg_resolution_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_resolution_updated_at BEFORE UPDATE ON core.resolution FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: risk trg_risk_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_risk_updated_at BEFORE UPDATE ON core.risk FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: territorial_indicator trg_territorial_indicator_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_territorial_indicator_updated_at BEFORE UPDATE ON core.territorial_indicator FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: territory trg_territory_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_territory_updated_at BEFORE UPDATE ON core.territory FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: user trg_user_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_user_updated_at BEFORE UPDATE ON core."user" FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: vehicle trg_vehicle_updated_at; Type: TRIGGER; Schema: core; Owner: goreos
--

CREATE TRIGGER trg_vehicle_updated_at BEFORE UPDATE ON core.vehicle FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: entity trg_entity_updated_at; Type: TRIGGER; Schema: meta; Owner: goreos
--

CREATE TRIGGER trg_entity_updated_at BEFORE UPDATE ON meta.entity FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: process trg_process_updated_at; Type: TRIGGER; Schema: meta; Owner: goreos
--

CREATE TRIGGER trg_process_updated_at BEFORE UPDATE ON meta.process FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: role trg_role_updated_at; Type: TRIGGER; Schema: meta; Owner: goreos
--

CREATE TRIGGER trg_role_updated_at BEFORE UPDATE ON meta.role FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: story_entity trg_story_entity_updated_at; Type: TRIGGER; Schema: meta; Owner: goreos
--

CREATE TRIGGER trg_story_entity_updated_at BEFORE UPDATE ON meta.story_entity FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: story trg_story_updated_at; Type: TRIGGER; Schema: meta; Owner: goreos
--

CREATE TRIGGER trg_story_updated_at BEFORE UPDATE ON meta.story FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: actor trg_actor_updated_at; Type: TRIGGER; Schema: ref; Owner: goreos
--

CREATE TRIGGER trg_actor_updated_at BEFORE UPDATE ON ref.actor FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: category trg_category_sync_parent; Type: TRIGGER; Schema: ref; Owner: goreos
--

CREATE TRIGGER trg_category_sync_parent BEFORE INSERT OR UPDATE OF parent_code ON ref.category FOR EACH ROW EXECUTE FUNCTION public.fn_sync_category_parent();


--
-- Name: category trg_category_updated_at; Type: TRIGGER; Schema: ref; Owner: goreos
--

CREATE TRIGGER trg_category_updated_at BEFORE UPDATE ON ref.category FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: operational_commitment_type trg_operational_commitment_type_updated_at; Type: TRIGGER; Schema: ref; Owner: goreos
--

CREATE TRIGGER trg_operational_commitment_type_updated_at BEFORE UPDATE ON ref.operational_commitment_type FOR EACH ROW EXECUTE FUNCTION public.fn_update_timestamp();


--
-- Name: administrative_act administrative_act_act_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_act_type_id_fkey FOREIGN KEY (act_type_id) REFERENCES ref.category(id);


--
-- Name: administrative_act administrative_act_cgr_outcome_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_cgr_outcome_id_fkey FOREIGN KEY (cgr_outcome_id) REFERENCES ref.category(id);


--
-- Name: administrative_act administrative_act_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_act administrative_act_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_act_history administrative_act_history_act_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act_history
    ADD CONSTRAINT administrative_act_history_act_id_fkey FOREIGN KEY (act_id) REFERENCES core.administrative_act(id) ON DELETE CASCADE;


--
-- Name: administrative_act_history administrative_act_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act_history
    ADD CONSTRAINT administrative_act_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_act_history administrative_act_history_new_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act_history
    ADD CONSTRAINT administrative_act_history_new_state_id_fkey FOREIGN KEY (new_state_id) REFERENCES ref.category(id);


--
-- Name: administrative_act_history administrative_act_history_previous_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act_history
    ADD CONSTRAINT administrative_act_history_previous_state_id_fkey FOREIGN KEY (previous_state_id) REFERENCES ref.category(id);


--
-- Name: administrative_act administrative_act_issuer_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_issuer_id_fkey FOREIGN KEY (issuer_id) REFERENCES core.organization(id);


--
-- Name: administrative_act administrative_act_parent_act_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_parent_act_id_fkey FOREIGN KEY (parent_act_id) REFERENCES core.administrative_act(id);


--
-- Name: administrative_act administrative_act_signer_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_signer_id_fkey FOREIGN KEY (signer_id) REFERENCES meta.role(id);


--
-- Name: administrative_act administrative_act_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: administrative_act administrative_act_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_act
    ADD CONSTRAINT administrative_act_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_procedure administrative_procedure_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_procedure administrative_procedure_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: administrative_procedure administrative_procedure_initiator_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_initiator_id_fkey FOREIGN KEY (initiator_id) REFERENCES core.organization(id);


--
-- Name: administrative_procedure administrative_procedure_procedure_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_procedure_type_id_fkey FOREIGN KEY (procedure_type_id) REFERENCES ref.category(id);


--
-- Name: administrative_procedure administrative_procedure_resolution_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_resolution_id_fkey FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);


--
-- Name: administrative_procedure administrative_procedure_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES meta.role(id);


--
-- Name: administrative_procedure administrative_procedure_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: administrative_procedure administrative_procedure_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.administrative_procedure
    ADD CONSTRAINT administrative_procedure_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: admissibility_check admissibility_check_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_check
    ADD CONSTRAINT admissibility_check_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: admissibility_check admissibility_check_item_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_check
    ADD CONSTRAINT admissibility_check_item_id_fkey FOREIGN KEY (item_id) REFERENCES core.admissibility_item(id);


--
-- Name: admissibility_check admissibility_check_verified_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_check
    ADD CONSTRAINT admissibility_check_verified_by_id_fkey FOREIGN KEY (verified_by_id) REFERENCES core."user"(id);


--
-- Name: admissibility_item admissibility_item_financing_track_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.admissibility_item
    ADD CONSTRAINT admissibility_item_financing_track_id_fkey FOREIGN KEY (financing_track_id) REFERENCES core.financing_track(id);


--
-- Name: agenda_item_context agenda_item_context_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agenda_item_context
    ADD CONSTRAINT agenda_item_context_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: agenda_item_context agenda_item_context_session_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agenda_item_context
    ADD CONSTRAINT agenda_item_context_session_agreement_id_fkey FOREIGN KEY (session_agreement_id) REFERENCES core.session_agreement(id);


--
-- Name: agreement agreement_agreement_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_agreement_type_id_fkey FOREIGN KEY (agreement_type_id) REFERENCES ref.category(id);


--
-- Name: agreement agreement_cgr_outcome_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_cgr_outcome_id_fkey FOREIGN KEY (cgr_outcome_id) REFERENCES ref.category(id);


--
-- Name: agreement agreement_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: agreement agreement_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: agreement agreement_giver_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_giver_id_fkey FOREIGN KEY (giver_id) REFERENCES core.organization(id);


--
-- Name: agreement_history agreement_history_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_history
    ADD CONSTRAINT agreement_history_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id) ON DELETE CASCADE;


--
-- Name: agreement_history agreement_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_history
    ADD CONSTRAINT agreement_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES core."user"(id);


--
-- Name: agreement_history agreement_history_new_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_history
    ADD CONSTRAINT agreement_history_new_state_id_fkey FOREIGN KEY (new_state_id) REFERENCES ref.category(id);


--
-- Name: agreement_history agreement_history_previous_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_history
    ADD CONSTRAINT agreement_history_previous_state_id_fkey FOREIGN KEY (previous_state_id) REFERENCES ref.category(id);


--
-- Name: agreement_installment agreement_installment_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: agreement_installment agreement_installment_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: agreement_installment agreement_installment_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: agreement_installment agreement_installment_payment_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_payment_status_id_fkey FOREIGN KEY (payment_status_id) REFERENCES ref.category(id);


--
-- Name: agreement_installment agreement_installment_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement_installment
    ADD CONSTRAINT agreement_installment_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: agreement agreement_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: agreement agreement_receiver_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES core.organization(id);


--
-- Name: agreement agreement_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: agreement agreement_technical_referent_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_technical_referent_id_fkey FOREIGN KEY (technical_referent_id) REFERENCES core.person(id);


--
-- Name: agreement agreement_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.agreement
    ADD CONSTRAINT agreement_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: alert alert_acknowledged_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_acknowledged_by_id_fkey FOREIGN KEY (acknowledged_by_id) REFERENCES core."user"(id);


--
-- Name: alert alert_alert_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_alert_type_id_fkey FOREIGN KEY (alert_type_id) REFERENCES ref.category(id);


--
-- Name: alert alert_attended_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_attended_by_id_fkey FOREIGN KEY (attended_by_id) REFERENCES core."user"(id);


--
-- Name: alert alert_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: alert alert_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: alert alert_severity_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_severity_id_fkey FOREIGN KEY (severity_id) REFERENCES ref.category(id);


--
-- Name: alert alert_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.alert
    ADD CONSTRAINT alert_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: budget_carryover budget_carryover_budget_program_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_carryover
    ADD CONSTRAINT budget_carryover_budget_program_id_fkey FOREIGN KEY (budget_program_id) REFERENCES core.budget_program(id) ON DELETE CASCADE;


--
-- Name: budget_carryover budget_carryover_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_carryover
    ADD CONSTRAINT budget_carryover_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: budget_commitment budget_commitment_budget_program_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_budget_program_id_fkey FOREIGN KEY (budget_program_id) REFERENCES core.budget_program(id);


--
-- Name: budget_commitment budget_commitment_commitment_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_commitment_type_id_fkey FOREIGN KEY (commitment_type_id) REFERENCES ref.category(id);


--
-- Name: budget_commitment budget_commitment_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: budget_commitment budget_commitment_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: budget_commitment budget_commitment_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: budget_commitment budget_commitment_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT budget_commitment_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: budget_cycle_tracking budget_cycle_tracking_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_tracking
    ADD CONSTRAINT budget_cycle_tracking_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES core."user"(id);


--
-- Name: budget_cycle_tracking budget_cycle_tracking_milestone_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_cycle_tracking
    ADD CONSTRAINT budget_cycle_tracking_milestone_id_fkey FOREIGN KEY (milestone_id) REFERENCES core.budget_cycle_milestone(id);


--
-- Name: budget_program budget_program_allocation_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_allocation_id_fkey FOREIGN KEY (allocation_id) REFERENCES ref.category(id);


--
-- Name: budget_program budget_program_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: budget_program budget_program_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: budget_program budget_program_item_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_item_id_fkey FOREIGN KEY (item_id) REFERENCES ref.category(id);


--
-- Name: budget_program budget_program_owner_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_owner_division_id_fkey FOREIGN KEY (owner_division_id) REFERENCES core.organization(id);


--
-- Name: budget_program budget_program_program_code_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_program_code_id_fkey FOREIGN KEY (program_code_id) REFERENCES ref.category(id);


--
-- Name: budget_program budget_program_program_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_program_type_id_fkey FOREIGN KEY (program_type_id) REFERENCES ref.category(id);


--
-- Name: budget_program budget_program_subtitle_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_subtitle_id_fkey FOREIGN KEY (subtitle_id) REFERENCES ref.category(id);


--
-- Name: budget_program budget_program_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_program
    ADD CONSTRAINT budget_program_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: commitment_history commitment_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.commitment_history
    ADD CONSTRAINT commitment_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES core."user"(id);


--
-- Name: commitment_history commitment_history_commitment_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.commitment_history
    ADD CONSTRAINT commitment_history_commitment_id_fkey FOREIGN KEY (commitment_id) REFERENCES core.operational_commitment(id) ON DELETE CASCADE;


--
-- Name: commitment_history commitment_history_new_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.commitment_history
    ADD CONSTRAINT commitment_history_new_state_id_fkey FOREIGN KEY (new_state_id) REFERENCES ref.category(id);


--
-- Name: commitment_history commitment_history_previous_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.commitment_history
    ADD CONSTRAINT commitment_history_previous_state_id_fkey FOREIGN KEY (previous_state_id) REFERENCES ref.category(id);


--
-- Name: committee committee_committee_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_committee_type_id_fkey FOREIGN KEY (committee_type_id) REFERENCES ref.category(id);


--
-- Name: committee committee_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: committee committee_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: committee_member committee_member_committee_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES core.committee(id);


--
-- Name: committee_member committee_member_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: committee_member committee_member_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: committee_member committee_member_person_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_person_id_fkey FOREIGN KEY (person_id) REFERENCES core.person(id);


--
-- Name: committee_member committee_member_role_in_committee_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_role_in_committee_id_fkey FOREIGN KEY (role_in_committee_id) REFERENCES ref.category(id);


--
-- Name: committee_member committee_member_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee_member
    ADD CONSTRAINT committee_member_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: committee committee_parent_org_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_parent_org_id_fkey FOREIGN KEY (parent_org_id) REFERENCES core.organization(id);


--
-- Name: committee committee_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.committee
    ADD CONSTRAINT committee_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: crisis_meeting crisis_meeting_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: crisis_meeting crisis_meeting_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: crisis_meeting crisis_meeting_organizer_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_organizer_id_fkey FOREIGN KEY (organizer_id) REFERENCES core."user"(id);


--
-- Name: crisis_meeting crisis_meeting_session_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_session_id_fkey FOREIGN KEY (session_id) REFERENCES core.session(id);


--
-- Name: crisis_meeting crisis_meeting_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.crisis_meeting
    ADD CONSTRAINT crisis_meeting_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_bpmn_model dgi_bpmn_model_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_bpmn_model
    ADD CONSTRAINT dgi_bpmn_model_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_committee_session dgi_committee_session_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_committee_session
    ADD CONSTRAINT dgi_committee_session_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_committee_session dgi_committee_session_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_committee_session
    ADD CONSTRAINT dgi_committee_session_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_committee_session dgi_committee_session_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_committee_session
    ADD CONSTRAINT dgi_committee_session_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_committee_session dgi_committee_session_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_committee_session
    ADD CONSTRAINT dgi_committee_session_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_data_source_status dgi_data_source_status_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_data_source_status dgi_data_source_status_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_data_source_status dgi_data_source_status_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: dgi_data_source_status dgi_data_source_status_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_data_source_status dgi_data_source_status_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_data_source_status
    ADD CONSTRAINT dgi_data_source_status_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_decree dgi_decree_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_decree
    ADD CONSTRAINT dgi_decree_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_indicator dgi_indicator_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_indicator dgi_indicator_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_indicator dgi_indicator_dimension_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_dimension_id_fkey FOREIGN KEY (dimension_id) REFERENCES ref.category(id);


--
-- Name: dgi_indicator dgi_indicator_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: dgi_indicator dgi_indicator_signal_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_signal_id_fkey FOREIGN KEY (signal_id) REFERENCES ref.category(id);


--
-- Name: dgi_indicator_snapshot dgi_indicator_snapshot_indicator_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator_snapshot
    ADD CONSTRAINT dgi_indicator_snapshot_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES core.dgi_indicator(id) ON DELETE CASCADE;


--
-- Name: dgi_indicator_snapshot dgi_indicator_snapshot_signal_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator_snapshot
    ADD CONSTRAINT dgi_indicator_snapshot_signal_id_fkey FOREIGN KEY (signal_id) REFERENCES ref.category(id);


--
-- Name: dgi_indicator dgi_indicator_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_indicator
    ADD CONSTRAINT dgi_indicator_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_initiative dgi_initiative_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_initiative dgi_initiative_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_initiative dgi_initiative_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: dgi_initiative dgi_initiative_dmaic_phase_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_dmaic_phase_id_fkey FOREIGN KEY (dmaic_phase_id) REFERENCES ref.category(id);


--
-- Name: dgi_initiative dgi_initiative_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES core."user"(id);


--
-- Name: dgi_initiative dgi_initiative_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_initiative dgi_initiative_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_initiative
    ADD CONSTRAINT dgi_initiative_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_report dgi_report_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_report dgi_report_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_report dgi_report_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_report dgi_report_generated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_generated_by_id_fkey FOREIGN KEY (generated_by_id) REFERENCES core."user"(id);


--
-- Name: dgi_report dgi_report_report_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_report_type_id_fkey FOREIGN KEY (report_type_id) REFERENCES ref.category(id);


--
-- Name: dgi_report dgi_report_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: dgi_report dgi_report_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.dgi_report
    ADD CONSTRAINT dgi_report_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: digital_platform digital_platform_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: digital_platform digital_platform_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: digital_platform digital_platform_owner_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES core.organization(id);


--
-- Name: digital_platform digital_platform_platform_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_platform_type_id_fkey FOREIGN KEY (platform_type_id) REFERENCES ref.category(id);


--
-- Name: digital_platform digital_platform_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.digital_platform
    ADD CONSTRAINT digital_platform_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: document document_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: document document_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: document document_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: document document_document_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_document_type_id_fkey FOREIGN KEY (document_type_id) REFERENCES ref.category(id);


--
-- Name: document document_file_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_file_id_fkey FOREIGN KEY (file_id) REFERENCES core.electronic_file(id);


--
-- Name: document document_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: document document_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.document
    ADD CONSTRAINT document_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: electronic_file electronic_file_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: electronic_file electronic_file_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: electronic_file electronic_file_procedure_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES core.procedure(id);


--
-- Name: electronic_file electronic_file_requester_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES core.person(id);


--
-- Name: electronic_file electronic_file_resolution_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_resolution_id_fkey FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);


--
-- Name: electronic_file electronic_file_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: electronic_file electronic_file_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.electronic_file
    ADD CONSTRAINT electronic_file_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: evaluation_assignment evaluation_assignment_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: evaluation_assignment evaluation_assignment_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: evaluation_assignment evaluation_assignment_evaluator_organization_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_evaluator_organization_id_fkey FOREIGN KEY (evaluator_organization_id) REFERENCES core.organization(id);


--
-- Name: evaluation_assignment evaluation_assignment_evaluator_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_evaluator_type_id_fkey FOREIGN KEY (evaluator_type_id) REFERENCES ref.category(id);


--
-- Name: evaluation_assignment evaluation_assignment_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id) ON DELETE CASCADE;


--
-- Name: evaluation_assignment evaluation_assignment_result_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_result_id_fkey FOREIGN KEY (result_id) REFERENCES ref.category(id);


--
-- Name: evaluation_assignment evaluation_assignment_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.evaluation_assignment
    ADD CONSTRAINT evaluation_assignment_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: budget_commitment fk_budget_commitment_agreement; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT fk_budget_commitment_agreement FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: budget_commitment fk_budget_commitment_ipr; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT fk_budget_commitment_ipr FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: budget_commitment fk_budget_commitment_resolution; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.budget_commitment
    ADD CONSTRAINT fk_budget_commitment_resolution FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);


--
-- Name: fund_program fk_fund_program_resolution; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fk_fund_program_resolution FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);


--
-- Name: organization fk_org_created_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT fk_org_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: organization fk_org_deleted_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT fk_org_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: organization fk_org_updated_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT fk_org_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: person fk_person_created_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT fk_person_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: person fk_person_deleted_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT fk_person_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: person fk_person_updated_by; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT fk_person_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: resolution fk_resolution_agreement; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT fk_resolution_agreement FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: fund_program fund_program_budget_program_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_budget_program_id_fkey FOREIGN KEY (budget_program_id) REFERENCES core.budget_program(id);


--
-- Name: fund_program fund_program_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: fund_program fund_program_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: fund_program fund_program_fund_source_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_fund_source_id_fkey FOREIGN KEY (fund_source_id) REFERENCES ref.category(id);


--
-- Name: fund_program fund_program_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: fund_program fund_program_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.fund_program
    ADD CONSTRAINT fund_program_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: installment_milestone installment_milestone_installment_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.installment_milestone
    ADD CONSTRAINT installment_milestone_installment_id_fkey FOREIGN KEY (installment_id) REFERENCES core.agreement_installment(id) ON DELETE CASCADE;


--
-- Name: installment_milestone installment_milestone_milestone_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.installment_milestone
    ADD CONSTRAINT installment_milestone_milestone_id_fkey FOREIGN KEY (milestone_id) REFERENCES core.ipr_milestone(id) ON DELETE CASCADE;


--
-- Name: inventory_item inventory_item_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: inventory_item inventory_item_current_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_current_status_id_fkey FOREIGN KEY (current_status_id) REFERENCES ref.category(id);


--
-- Name: inventory_item inventory_item_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: inventory_item inventory_item_ipr_origin_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_ipr_origin_id_fkey FOREIGN KEY (ipr_origin_id) REFERENCES core.ipr(id);


--
-- Name: inventory_item inventory_item_item_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_item_type_id_fkey FOREIGN KEY (item_type_id) REFERENCES ref.category(id);


--
-- Name: inventory_item inventory_item_location_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_location_id_fkey FOREIGN KEY (location_id) REFERENCES core.organization(id);


--
-- Name: inventory_item inventory_item_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES core.person(id);


--
-- Name: inventory_item inventory_item_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.inventory_item
    ADD CONSTRAINT inventory_item_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_alert_level_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_alert_level_id_fkey FOREIGN KEY (alert_level_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_assignee_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_budget_subtitle_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_budget_subtitle_id_fkey FOREIGN KEY (budget_subtitle_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_executor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_executor_id_fkey FOREIGN KEY (executor_id) REFERENCES core.organization(id);


--
-- Name: ipr ipr_formulator_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_formulator_id_fkey FOREIGN KEY (formulator_id) REFERENCES core.organization(id);


--
-- Name: ipr ipr_fund_category_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_fund_category_id_fkey FOREIGN KEY (fund_category_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_funding_source_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_funding_source_id_fkey FOREIGN KEY (funding_source_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_investment_sector_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_investment_sector_id_fkey FOREIGN KEY (investment_sector_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_ipr_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_ipr_type_id_fkey FOREIGN KEY (ipr_type_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_mcd_phase_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_mcd_phase_id_fkey FOREIGN KEY (mcd_phase_id) REFERENCES ref.category(id);


--
-- Name: ipr_mechanism ipr_mechanism_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_mechanism ipr_mechanism_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_mechanism_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_mechanism_id_fkey FOREIGN KEY (mechanism_id) REFERENCES ref.category(id);


--
-- Name: ipr_mechanism ipr_mechanism_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: ipr_mechanism ipr_mechanism_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_mechanism
    ADD CONSTRAINT ipr_mechanism_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_milestone ipr_milestone_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_milestone ipr_milestone_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_milestone ipr_milestone_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_milestone ipr_milestone_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id) ON DELETE CASCADE;


--
-- Name: ipr_milestone ipr_milestone_milestone_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_milestone_type_id_fkey FOREIGN KEY (milestone_type_id) REFERENCES ref.category(id);


--
-- Name: ipr_milestone ipr_milestone_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_milestone
    ADD CONSTRAINT ipr_milestone_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_party ipr_party_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: ipr_party ipr_party_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_party ipr_party_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_party ipr_party_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id) ON DELETE CASCADE;


--
-- Name: ipr_party ipr_party_organization_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES core.organization(id);


--
-- Name: ipr_party ipr_party_party_role_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_party_role_id_fkey FOREIGN KEY (party_role_id) REFERENCES ref.category(id);


--
-- Name: ipr_party ipr_party_sponsor_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_sponsor_division_id_fkey FOREIGN KEY (sponsor_division_id) REFERENCES core.organization(id);


--
-- Name: ipr_party ipr_party_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_party
    ADD CONSTRAINT ipr_party_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_problem ipr_problem_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: ipr_problem ipr_problem_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_problem ipr_problem_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_problem ipr_problem_detected_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_detected_by_id_fkey FOREIGN KEY (detected_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_problem ipr_problem_impact_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_impact_id_fkey FOREIGN KEY (impact_id) REFERENCES ref.category(id);


--
-- Name: ipr_problem ipr_problem_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: ipr_problem ipr_problem_problem_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_problem_type_id_fkey FOREIGN KEY (problem_type_id) REFERENCES ref.category(id);


--
-- Name: ipr_problem ipr_problem_resolved_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_resolved_by_id_fkey FOREIGN KEY (resolved_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_problem ipr_problem_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: ipr_problem ipr_problem_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_problem
    ADD CONSTRAINT ipr_problem_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_resolution_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_resolution_type_id_fkey FOREIGN KEY (resolution_type_id) REFERENCES ref.category(id);


--
-- Name: ipr ipr_sponsor_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_sponsor_division_id_fkey FOREIGN KEY (sponsor_division_id) REFERENCES core.organization(id);


--
-- Name: ipr ipr_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: ipr_territory ipr_territory_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_territory ipr_territory_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: ipr_territory ipr_territory_impact_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_impact_type_id_fkey FOREIGN KEY (impact_type_id) REFERENCES ref.category(id);


--
-- Name: ipr_territory ipr_territory_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id) ON DELETE CASCADE;


--
-- Name: ipr_territory ipr_territory_territory_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_territory_id_fkey FOREIGN KEY (territory_id) REFERENCES core.territory(id);


--
-- Name: ipr_territory ipr_territory_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr_territory
    ADD CONSTRAINT ipr_territory_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: ipr ipr_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.ipr
    ADD CONSTRAINT ipr_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: kinship_declaration kinship_declaration_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT kinship_declaration_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: kinship_declaration kinship_declaration_person_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT kinship_declaration_person_id_fkey FOREIGN KEY (person_id) REFERENCES core.person(id);


--
-- Name: kinship_declaration kinship_declaration_related_authority_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT kinship_declaration_related_authority_id_fkey FOREIGN KEY (related_authority_id) REFERENCES core.person(id);


--
-- Name: kinship_declaration kinship_declaration_validated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.kinship_declaration
    ADD CONSTRAINT kinship_declaration_validated_by_id_fkey FOREIGN KEY (validated_by_id) REFERENCES core."user"(id);


--
-- Name: legal_document legal_document_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: legal_document legal_document_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: legal_document legal_document_doc_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_doc_type_id_fkey FOREIGN KEY (doc_type_id) REFERENCES ref.category(id);


--
-- Name: legal_document legal_document_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_document
    ADD CONSTRAINT legal_document_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: legal_mandate legal_mandate_applies_to_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_applies_to_id_fkey FOREIGN KEY (applies_to_id) REFERENCES ref.category(id);


--
-- Name: legal_mandate legal_mandate_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: legal_mandate legal_mandate_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: legal_mandate legal_mandate_legal_document_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_legal_document_id_fkey FOREIGN KEY (legal_document_id) REFERENCES core.legal_document(id);


--
-- Name: legal_mandate legal_mandate_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.legal_mandate
    ADD CONSTRAINT legal_mandate_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: minute minute_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: minute minute_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: minute minute_resolution_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_resolution_id_fkey FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);


--
-- Name: minute minute_session_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_session_id_fkey FOREIGN KEY (session_id) REFERENCES core.session(id);


--
-- Name: minute minute_signed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_signed_by_id_fkey FOREIGN KEY (signed_by_id) REFERENCES core.person(id);


--
-- Name: minute minute_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.minute
    ADD CONSTRAINT minute_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment operational_commitment_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: operational_commitment operational_commitment_budget_commitment_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_budget_commitment_id_fkey FOREIGN KEY (budget_commitment_id) REFERENCES core.budget_commitment(id);


--
-- Name: operational_commitment operational_commitment_commitment_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_commitment_type_id_fkey FOREIGN KEY (commitment_type_id) REFERENCES ref.operational_commitment_type(id);


--
-- Name: operational_commitment operational_commitment_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment operational_commitment_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment operational_commitment_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: operational_commitment operational_commitment_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: operational_commitment operational_commitment_priority_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_priority_id_fkey FOREIGN KEY (priority_id) REFERENCES ref.category(id);


--
-- Name: operational_commitment operational_commitment_problem_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_problem_id_fkey FOREIGN KEY (problem_id) REFERENCES core.ipr_problem(id);


--
-- Name: operational_commitment operational_commitment_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment operational_commitment_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: operational_commitment operational_commitment_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment operational_commitment_verified_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.operational_commitment
    ADD CONSTRAINT operational_commitment_verified_by_id_fkey FOREIGN KEY (verified_by_id) REFERENCES core."user"(id);


--
-- Name: organization organization_org_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT organization_org_type_id_fkey FOREIGN KEY (org_type_id) REFERENCES ref.category(id);


--
-- Name: organization organization_parent_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.organization
    ADD CONSTRAINT organization_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES core.organization(id);


--
-- Name: person person_estamento_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_estamento_id_fkey FOREIGN KEY (estamento_id) REFERENCES ref.category(id);


--
-- Name: person person_organization_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES core.organization(id);


--
-- Name: person person_person_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_person_type_id_fkey FOREIGN KEY (person_type_id) REFERENCES ref.category(id);


--
-- Name: person person_position_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_position_id_fkey FOREIGN KEY (position_id) REFERENCES core."position"(id);


--
-- Name: person person_qualification_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_qualification_id_fkey FOREIGN KEY (qualification_id) REFERENCES ref.category(id);


--
-- Name: person person_role_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.person
    ADD CONSTRAINT person_role_id_fkey FOREIGN KEY (role_id) REFERENCES meta.role(id);


--
-- Name: planning_instrument planning_instrument_approved_by_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES core.organization(id);


--
-- Name: planning_instrument planning_instrument_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: planning_instrument planning_instrument_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: planning_instrument planning_instrument_instrument_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_instrument_type_id_fkey FOREIGN KEY (instrument_type_id) REFERENCES ref.category(id);


--
-- Name: planning_instrument planning_instrument_parent_instrument_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_parent_instrument_id_fkey FOREIGN KEY (parent_instrument_id) REFERENCES core.planning_instrument(id);


--
-- Name: planning_instrument planning_instrument_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.planning_instrument
    ADD CONSTRAINT planning_instrument_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: position position_organization_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."position"
    ADD CONSTRAINT position_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES core.organization(id);


--
-- Name: procedure procedure_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: procedure procedure_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: procedure procedure_platform_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES core.digital_platform(id);


--
-- Name: procedure procedure_procedure_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_procedure_type_id_fkey FOREIGN KEY (procedure_type_id) REFERENCES ref.category(id);


--
-- Name: procedure procedure_responsible_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_responsible_division_id_fkey FOREIGN KEY (responsible_division_id) REFERENCES core.organization(id);


--
-- Name: procedure procedure_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.procedure
    ADD CONSTRAINT procedure_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: progress_report progress_report_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: progress_report progress_report_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: progress_report progress_report_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: progress_report progress_report_reported_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_reported_by_id_fkey FOREIGN KEY (reported_by_id) REFERENCES core."user"(id);


--
-- Name: progress_report progress_report_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.progress_report
    ADD CONSTRAINT progress_report_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: rendition rendition_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_agreement_id_fkey FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);


--
-- Name: rendition rendition_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: rendition rendition_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: rendition_escalation rendition_escalation_alert_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_escalation
    ADD CONSTRAINT rendition_escalation_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES core.alert(id);


--
-- Name: rendition_escalation rendition_escalation_phase_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_escalation
    ADD CONSTRAINT rendition_escalation_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES core.rendition_phase(id);


--
-- Name: rendition_escalation rendition_escalation_rendition_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_escalation
    ADD CONSTRAINT rendition_escalation_rendition_id_fkey FOREIGN KEY (rendition_id) REFERENCES core.rendition(id);


--
-- Name: rendition_history rendition_history_changed_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_history
    ADD CONSTRAINT rendition_history_changed_by_id_fkey FOREIGN KEY (changed_by_id) REFERENCES core."user"(id);


--
-- Name: rendition_history rendition_history_new_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_history
    ADD CONSTRAINT rendition_history_new_state_id_fkey FOREIGN KEY (new_state_id) REFERENCES ref.category(id);


--
-- Name: rendition_history rendition_history_previous_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_history
    ADD CONSTRAINT rendition_history_previous_state_id_fkey FOREIGN KEY (previous_state_id) REFERENCES ref.category(id);


--
-- Name: rendition_history rendition_history_rendition_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition_history
    ADD CONSTRAINT rendition_history_rendition_id_fkey FOREIGN KEY (rendition_id) REFERENCES core.rendition(id) ON DELETE CASCADE;


--
-- Name: rendition rendition_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: rendition rendition_renderer_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_renderer_id_fkey FOREIGN KEY (renderer_id) REFERENCES core.organization(id);


--
-- Name: rendition rendition_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES core."user"(id);


--
-- Name: rendition rendition_state_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_state_id_fkey FOREIGN KEY (state_id) REFERENCES ref.category(id);


--
-- Name: rendition rendition_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.rendition
    ADD CONSTRAINT rendition_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: resolution resolution_administrative_act_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_administrative_act_id_fkey FOREIGN KEY (administrative_act_id) REFERENCES core.administrative_act(id);


--
-- Name: resolution resolution_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: resolution resolution_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: resolution resolution_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: resolution resolution_resolution_subtype_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_resolution_subtype_id_fkey FOREIGN KEY (resolution_subtype_id) REFERENCES ref.category(id);


--
-- Name: resolution resolution_resolution_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_resolution_type_id_fkey FOREIGN KEY (resolution_type_id) REFERENCES ref.category(id);


--
-- Name: resolution resolution_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.resolution
    ADD CONSTRAINT resolution_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: risk risk_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: risk risk_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: risk risk_impact_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_impact_id_fkey FOREIGN KEY (impact_id) REFERENCES ref.category(id);


--
-- Name: risk risk_probability_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_probability_id_fkey FOREIGN KEY (probability_id) REFERENCES ref.category(id);


--
-- Name: risk risk_risk_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_risk_type_id_fkey FOREIGN KEY (risk_type_id) REFERENCES ref.category(id);


--
-- Name: risk risk_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: risk risk_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.risk
    ADD CONSTRAINT risk_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: session_agreement session_agreement_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: session_agreement session_agreement_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: session_agreement session_agreement_ipr_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_ipr_id_fkey FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);


--
-- Name: session_agreement session_agreement_minute_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_minute_id_fkey FOREIGN KEY (minute_id) REFERENCES core.minute(id);


--
-- Name: session_agreement session_agreement_responsible_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_responsible_id_fkey FOREIGN KEY (responsible_id) REFERENCES core.person(id);


--
-- Name: session_agreement session_agreement_status_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_status_id_fkey FOREIGN KEY (status_id) REFERENCES ref.category(id);


--
-- Name: session_agreement session_agreement_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_agreement
    ADD CONSTRAINT session_agreement_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: session session_committee_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES core.committee(id);


--
-- Name: session session_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: session session_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: session session_session_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_session_type_id_fkey FOREIGN KEY (session_type_id) REFERENCES ref.category(id);


--
-- Name: session session_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session
    ADD CONSTRAINT session_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: session_vote session_vote_session_agreement_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_vote
    ADD CONSTRAINT session_vote_session_agreement_id_fkey FOREIGN KEY (session_agreement_id) REFERENCES core.session_agreement(id);


--
-- Name: session_vote session_vote_vote_option_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_vote
    ADD CONSTRAINT session_vote_vote_option_id_fkey FOREIGN KEY (vote_option_id) REFERENCES ref.category(id);


--
-- Name: session_vote session_vote_voter_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.session_vote
    ADD CONSTRAINT session_vote_voter_id_fkey FOREIGN KEY (voter_id) REFERENCES core.committee_member(id);


--
-- Name: subv8_fund_ceiling subv8_fund_ceiling_fund_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.subv8_fund_ceiling
    ADD CONSTRAINT subv8_fund_ceiling_fund_id_fkey FOREIGN KEY (fund_id) REFERENCES core.subv8_fund(id);


--
-- Name: territorial_indicator territorial_indicator_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: territorial_indicator territorial_indicator_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: territorial_indicator territorial_indicator_indicator_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_indicator_type_id_fkey FOREIGN KEY (indicator_type_id) REFERENCES ref.category(id);


--
-- Name: territorial_indicator territorial_indicator_territory_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_territory_id_fkey FOREIGN KEY (territory_id) REFERENCES core.territory(id);


--
-- Name: territorial_indicator territorial_indicator_unit_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES ref.category(id);


--
-- Name: territorial_indicator territorial_indicator_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territorial_indicator
    ADD CONSTRAINT territorial_indicator_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: territory territory_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: territory territory_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: territory territory_parent_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES core.territory(id);


--
-- Name: territory territory_territory_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_territory_type_id_fkey FOREIGN KEY (territory_type_id) REFERENCES ref.category(id);


--
-- Name: territory territory_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.territory
    ADD CONSTRAINT territory_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: user user_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: user user_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: user user_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_division_id_fkey FOREIGN KEY (division_id) REFERENCES core.organization(id);


--
-- Name: user user_person_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_person_id_fkey FOREIGN KEY (person_id) REFERENCES core.person(id);


--
-- Name: user user_system_role_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_system_role_id_fkey FOREIGN KEY (system_role_id) REFERENCES ref.category(id);


--
-- Name: user user_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core."user"
    ADD CONSTRAINT user_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: vehicle vehicle_assigned_division_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_assigned_division_id_fkey FOREIGN KEY (assigned_division_id) REFERENCES core.organization(id);


--
-- Name: vehicle vehicle_created_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: vehicle vehicle_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: vehicle vehicle_fuel_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_fuel_type_id_fkey FOREIGN KEY (fuel_type_id) REFERENCES ref.category(id);


--
-- Name: vehicle vehicle_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES core.inventory_item(id);


--
-- Name: vehicle vehicle_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: vehicle vehicle_vehicle_type_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: goreos
--

ALTER TABLE ONLY core.vehicle
    ADD CONSTRAINT vehicle_vehicle_type_id_fkey FOREIGN KEY (vehicle_type_id) REFERENCES ref.category(id);


--
-- Name: entity fk_entity_created_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.entity
    ADD CONSTRAINT fk_entity_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: entity fk_entity_deleted_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.entity
    ADD CONSTRAINT fk_entity_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: entity fk_entity_updated_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.entity
    ADD CONSTRAINT fk_entity_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: process fk_process_created_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.process
    ADD CONSTRAINT fk_process_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: process fk_process_deleted_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.process
    ADD CONSTRAINT fk_process_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: process fk_process_updated_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.process
    ADD CONSTRAINT fk_process_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: role fk_role_created_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT fk_role_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: role fk_role_deleted_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT fk_role_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: role fk_role_updated_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT fk_role_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: story fk_story_created_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT fk_story_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: story fk_story_deleted_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT fk_story_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: story_entity fk_story_entity_created_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT fk_story_entity_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: story_entity fk_story_entity_deleted_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT fk_story_entity_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: story_entity fk_story_entity_updated_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT fk_story_entity_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: story fk_story_updated_by; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT fk_story_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: role role_human_accountable_id_fkey; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.role
    ADD CONSTRAINT role_human_accountable_id_fkey FOREIGN KEY (human_accountable_id) REFERENCES meta.role(id);


--
-- Name: story_entity story_entity_entity_id_fkey; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT story_entity_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES meta.entity(id);


--
-- Name: story_entity story_entity_story_id_fkey; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story_entity
    ADD CONSTRAINT story_entity_story_id_fkey FOREIGN KEY (story_id) REFERENCES meta.story(id);


--
-- Name: story story_process_id_fkey; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT story_process_id_fkey FOREIGN KEY (process_id) REFERENCES meta.process(id);


--
-- Name: story story_role_id_fkey; Type: FK CONSTRAINT; Schema: meta; Owner: goreos
--

ALTER TABLE ONLY meta.story
    ADD CONSTRAINT story_role_id_fkey FOREIGN KEY (role_id) REFERENCES meta.role(id);


--
-- Name: acceptance_criteria acceptance_criteria_us_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.acceptance_criteria
    ADD CONSTRAINT acceptance_criteria_us_id_fkey FOREIGN KEY (us_id) REFERENCES public.fact_user_story(id) ON DELETE CASCADE;


--
-- Name: bridge_us_entity bridge_us_entity_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_entity
    ADD CONSTRAINT bridge_us_entity_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.dim_entity(id) ON DELETE CASCADE;


--
-- Name: bridge_us_entity bridge_us_entity_us_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_entity
    ADD CONSTRAINT bridge_us_entity_us_id_fkey FOREIGN KEY (us_id) REFERENCES public.fact_user_story(id) ON DELETE CASCADE;


--
-- Name: bridge_us_extra_tag bridge_us_extra_tag_tag_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_extra_tag
    ADD CONSTRAINT bridge_us_extra_tag_tag_fkey FOREIGN KEY (tag) REFERENCES public.dim_extra_tag(tag) ON DELETE CASCADE;


--
-- Name: bridge_us_extra_tag bridge_us_extra_tag_us_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.bridge_us_extra_tag
    ADD CONSTRAINT bridge_us_extra_tag_us_id_fkey FOREIGN KEY (us_id) REFERENCES public.fact_user_story(id) ON DELETE CASCADE;


--
-- Name: dim_role dim_role_canonical_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.dim_role
    ADD CONSTRAINT dim_role_canonical_id_fkey FOREIGN KEY (canonical_id) REFERENCES public.dim_role_canonical(id);


--
-- Name: fact_user_story fact_user_story_process_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.fact_user_story
    ADD CONSTRAINT fact_user_story_process_id_fkey FOREIGN KEY (process_id) REFERENCES public.dim_process(id);


--
-- Name: fact_user_story fact_user_story_role_canonical_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.fact_user_story
    ADD CONSTRAINT fact_user_story_role_canonical_id_fkey FOREIGN KEY (role_canonical_id) REFERENCES public.dim_role_canonical(id);


--
-- Name: fact_user_story fact_user_story_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.fact_user_story
    ADD CONSTRAINT fact_user_story_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.dim_role(id);


--
-- Name: role_especialidad role_especialidad_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.role_especialidad
    ADD CONSTRAINT role_especialidad_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.dim_role_canonical(id) ON DELETE CASCADE;


--
-- Name: role_mapping role_mapping_canonical_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: goreos
--

ALTER TABLE ONLY public.role_mapping
    ADD CONSTRAINT role_mapping_canonical_id_fkey FOREIGN KEY (canonical_id) REFERENCES public.dim_role_canonical(id);


--
-- Name: category category_parent_id_fkey; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT category_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES ref.category(id);


--
-- Name: category category_phase_id_fkey; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT category_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES ref.category(id);


--
-- Name: actor fk_actor_created_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT fk_actor_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: actor fk_actor_deleted_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT fk_actor_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: actor fk_actor_organization; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT fk_actor_organization FOREIGN KEY (organization_id) REFERENCES core.organization(id);


--
-- Name: actor fk_actor_updated_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.actor
    ADD CONSTRAINT fk_actor_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: category fk_category_created_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT fk_category_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: category fk_category_deleted_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT fk_category_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: category fk_category_updated_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.category
    ADD CONSTRAINT fk_category_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment_type fk_oct_created_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.operational_commitment_type
    ADD CONSTRAINT fk_oct_created_by FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment_type fk_oct_deleted_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.operational_commitment_type
    ADD CONSTRAINT fk_oct_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core."user"(id);


--
-- Name: operational_commitment_type fk_oct_updated_by; Type: FK CONSTRAINT; Schema: ref; Owner: goreos
--

ALTER TABLE ONLY ref.operational_commitment_type
    ADD CONSTRAINT fk_oct_updated_by FOREIGN KEY (updated_by_id) REFERENCES core."user"(id);


--
-- Name: event event_actor_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.event
    ADD CONSTRAINT event_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES core."user"(id);


--
-- Name: event event_actor_ref_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.event
    ADD CONSTRAINT event_actor_ref_id_fkey FOREIGN KEY (actor_ref_id) REFERENCES ref.actor(id);


--
-- Name: event event_created_by_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.event
    ADD CONSTRAINT event_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: event event_event_type_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.event
    ADD CONSTRAINT event_event_type_id_fkey FOREIGN KEY (event_type_id) REFERENCES ref.category(id);


--
-- Name: magnitude magnitude_aspect_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.magnitude
    ADD CONSTRAINT magnitude_aspect_id_fkey FOREIGN KEY (aspect_id) REFERENCES ref.category(id);


--
-- Name: magnitude magnitude_created_by_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.magnitude
    ADD CONSTRAINT magnitude_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES core."user"(id);


--
-- Name: magnitude magnitude_unit_id_fkey; Type: FK CONSTRAINT; Schema: txn; Owner: goreos
--

ALTER TABLE txn.magnitude
    ADD CONSTRAINT magnitude_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES ref.category(id);


--
-- PostgreSQL database dump complete
--

\unrestrict wnKeXLgaBV9DHH0Ave44DDZHUYKULcYedQbT7LkIj7xG32v4YWyyFAzdUlouLdU

