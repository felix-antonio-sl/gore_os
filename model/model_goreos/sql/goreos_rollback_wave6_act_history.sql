BEGIN;
DROP TRIGGER IF EXISTS trg_act_history ON core.administrative_act;
DROP FUNCTION IF EXISTS fn_act_history();
DROP TABLE IF EXISTS core.administrative_act_history;
COMMIT;
