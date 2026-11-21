-- Only the exact synthetic notices created by the hosting smoke test.
WITH fixture AS MATERIALIZED (
    SELECT s.household, s.id
    FROM sources s
    WHERE s.title = 'Synthetic hosting check'
      AND s.text = E'Subject: Synthetic hosting check\nWhen: Sunday, November 22, 2026 at 10:30 a.m.\nWhere: Test library\nPlease bring a test folder.'
      AND s.date = '2026-11-22' AND s.time = '10:30'
      AND s.location = 'Test library' AND s.preparation = 'a test folder'
      AND s.person = '' AND s.responsibility = '' AND s.deadline = '' AND s.instructions = ''
      AND NOT EXISTS (
          SELECT 1 FROM versions v
          WHERE v.household = s.household AND v.source = s.id
            AND (EXISTS (
              SELECT 1 FROM versions other
              WHERE other.household = v.household AND other.plan = v.plan AND other.source <> s.id
            ) OR EXISTS (
              SELECT 1 FROM tasks t WHERE t.household = v.household AND t.plan = v.plan
            ) OR EXISTS (
              SELECT 1 FROM sources later WHERE later.household = v.household AND later.target = v.plan
            ))
      )
), removed_versions AS (
    DELETE FROM versions v USING fixture f
    WHERE v.household = f.household AND v.source = f.id
    RETURNING v.household, v.source
)
DELETE FROM sources s USING fixture f
WHERE s.household = f.household AND s.id = f.id
  AND (NOT EXISTS (
     SELECT 1 FROM versions v WHERE v.household = s.household AND v.source = s.id
  ) OR EXISTS (
     SELECT 1 FROM removed_versions v WHERE v.household = s.household AND v.source = s.id
  ))
RETURNING s.id;
