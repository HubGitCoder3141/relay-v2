-- Preserve the Supabase event trigger and remove direct execution by API roles.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p JOIN pg_event_trigger e ON e.evtfoid = p.oid
        WHERE p.oid = to_regprocedure('public.rls_auto_enable()')
          AND p.prorettype = 'event_trigger'::regtype
    ) THEN
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon, authenticated;
    END IF;
END;
$$;
