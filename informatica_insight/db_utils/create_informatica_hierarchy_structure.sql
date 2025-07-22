DROP TABLE IF EXISTS INFORMATICA_HIERARCHY_STRUCTURE;


-- table contain all INFORMATICA_HIERARCHY_STRUCTURE for wf and related sessions
---                   PCI , RHEL
--
--SELECT base_query.folder_name, -- Folder Name (subj_name from opb_subject)
-- REGEXP_SUBSTR(base_query.hierarchy_structure, '[^/]+$', 1, 1) AS SESSION_WF_NAME, -- Extract the last part of hierarchy_structure as session_name
-- REGEXP_SUBSTR(base_query.path, '[0-9]+', 1, 1) AS workflow_id, -- Extract first number in path as workflow_id
-- CASE
--     WHEN INSTR(base_query.path, '/', -1) = 1 THEN NULL
--     ELSE REGEXP_SUBSTR(base_query.path, '[0-9]+', 1, REGEXP_COUNT(base_query.path, '/') - 1)
-- END AS session_id, -- Extract last number in path as session_id
-- base_query.hierarchy_structure, -- Hierarchy Structure (task name)
-- base_query.path, -- Path
-- base_query.instance_id, -- Instance ID
-- SYS_CONTEXT('USERENV', 'DB_NAME') AS informatica_server, -- Informatica Server
-- SYS_CONTEXT('USERENV', 'SESSION_USER') AS informatica_user, -- Informatica User
-- TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') AS created_date -- Created Date
--FROM
--  (-- Original query for folder name and hierarchy structure
-- SELECT DISTINCT '/' || task.task_id AS PATH,
--                 task.task_name AS hierarchy_structure,
--                 subject.subj_name AS folder_name, -- Folder Name (subj_name from opb_subject)
-- NULL AS instance_id -- Since instance_id doesn't exist in this part, set it to NULL
--
--   FROM opb_task task
--   JOIN opb_subject subject ON task.subject_id = subject.subj_id
--   WHERE task.task_type = 71
--    -- AND subject.subj_name = 'PCI'
--   UNION ALL SELECT DISTINCT hierarchy.path,
--                             hierarchy.task_name AS hierarchy_structure,
--                             subject.subj_name AS folder_name, -- Folder Name (subj_name from opb_subject)
-- hierarchy.instance_id -- Instance ID from hierarchy
--   FROM
--     (SELECT task_inst.workflow_id,
--             task_inst.task_id,
--             task_inst.instance_id,
--             LEVEL AS depth,
--                      SYS_CONNECT_BY_PATH(task_inst.workflow_id, '/') || '/' || task_inst.task_id || '/' AS PATH,
--                      LPAD(' ', 4 * LEVEL, ' ') || SYS_CONNECT_BY_PATH(task_inst.instance_name, '/') AS task_name
--      FROM opb_task_inst task_inst
--      WHERE task_inst.task_type IN (68,
--                                    70)
--        START WITH workflow_id IN
--          (SELECT task_id
--           FROM opb_task
--           WHERE task_type = 71) CONNECT BY
--        PRIOR task_inst.task_id = task_inst.workflow_id) HIERARCHY
--   JOIN opb_task task ON task.task_id = SUBSTR(hierarchy.path, 2, INSTR(hierarchy.path, '/', 1, 2) - 2)
--   JOIN opb_subject subject ON task.subject_id = subject.subj_id
--   ---WHERE subject.subj_name = 'PCI'
--   ) base_query
--ORDER BY FOLDER_NAME,
--         base_query.path ASC;



---- PCI , Centos
--
--SELECT
--    base_query.folder_name, -- Folder Name (subj_name from opb_subject)
--    REGEXP_SUBSTR(base_query.hierarchy_structure, '[^/]+$', 1, 1) AS SESSION_WF_NAME, -- Extract the last part of hierarchy_structure as session_name
--    REGEXP_SUBSTR(base_query.path, '[0-9]+', 1, 1) AS workflow_id, -- Extract first number in path as workflow_id
--    CASE
--        WHEN INSTR(base_query.path, '/', -1) = 1 THEN NULL
--        ELSE REGEXP_SUBSTR(base_query.path, '[0-9]+', 1, REGEXP_COUNT(base_query.path, '/') - 1)
--    END AS session_id, -- Extract last number in path as session_id
--    base_query.hierarchy_structure, -- Hierarchy Structure (task name)
--    base_query.path, -- Path
--    base_query.instance_id, -- Instance ID
--    SYS_CONTEXT('USERENV', 'DB_NAME') AS informatica_server, -- Informatica Server
--    SYS_CONTEXT('USERENV', 'SESSION_USER') AS informatica_user, -- Informatica User
--    TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') AS created_date -- Created Date
--FROM
--  (-- Original query for folder name and hierarchy structure
--   SELECT DISTINCT
--       '/' || task.task_id AS path,
--       task.task_name AS hierarchy_structure,
--       subject.subj_name AS folder_name, -- Folder Name (subj_name from opb_subject)
--       NULL AS instance_id -- Since instance_id doesn't exist in this part, set it to NULL
--   FROM
--       INFO_REP_PROD.opb_task task
--   JOIN
--       INFO_REP_PROD.opb_subject subject
--       ON task.subject_id = subject.subj_id
--   WHERE
--       task.task_type = 71
--       -- AND subject.subj_name = 'PCI'
--   UNION ALL
--   SELECT DISTINCT
--       hierarchy.path,
--       hierarchy.task_name AS hierarchy_structure,
--       subject.subj_name AS folder_name, -- Folder Name (subj_name from opb_subject)
--       hierarchy.instance_id -- Instance ID from hierarchy
--   FROM
--       (SELECT
--            task_inst.workflow_id,
--            task_inst.task_id,
--            task_inst.instance_id,
--            LEVEL AS depth,
--            SYS_CONNECT_BY_PATH(task_inst.workflow_id, '/') || '/' || task_inst.task_id || '/' AS path,
--            LPAD(' ', 4 * LEVEL, ' ') || SYS_CONNECT_BY_PATH(task_inst.instance_name, '/') AS task_name
--        FROM
--            INFO_REP_PROD.opb_task_inst task_inst
--        WHERE
--            task_inst.task_type IN (68, 70)
--        START WITH
--            workflow_id IN (
--                SELECT task_id
--                FROM INFO_REP_PROD.opb_task
--                WHERE task_type = 71
--            )
--        CONNECT BY
--            PRIOR task_inst.task_id = task_inst.workflow_id
--       ) hierarchy
--   JOIN
--       INFO_REP_PROD.opb_task task
--       ON task.task_id = SUBSTR(hierarchy.path, 2, INSTR(hierarchy.path, '/', 1, 2) - 2)
--   JOIN
--       INFO_REP_PROD.opb_subject subject
--       ON task.subject_id = subject.subj_id
--   -- WHERE subject.subj_name = 'PCI'
--   ) base_query
--ORDER BY
--    folder_name,
--    base_query.path ASC;


CREATE TABLE INFORMATICA_HIERARCHY_STRUCTURE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FOLDER_NAME VARCHAR2(100),              -- Folder Name (PCI_TRANSFORMER, etc.)
    SESSION_WF_NAME VARCHAR2(255),          -- Session Workflow Name (e.g., s_m_etl_dqa_results)
    WORKFLOW_ID VARCHAR2(20),              -- Workflow ID (e.g., 9586)
    SESSION_ID VARCHAR2(20),               -- Session ID (e.g., 9636)
    HIERARCHY_STRUCTURE VARCHAR2(500),     -- Hierarchy Structure (e.g., /wl_DQA/s_m_etl_dqa_results)
    PATH VARCHAR2(500),                    -- Path (e.g., /9586/9632/9636/)
    INSTANCE_ID VARCHAR2(100),              -- Instance ID (e.g., 5584)
    INFORMATICA_SERVER VARCHAR2(200),       -- Informatica Server (e.g., infoprod)
    INFORMATICA_USER VARCHAR2(50),         -- Informatica User (e.g., INFOPROD_REP_PCI)
    CREATED_DATE DATE,               -- Created Date (e.g., 2025-01-02 13:55:33)
    UPDATED_DATE DATE
);
