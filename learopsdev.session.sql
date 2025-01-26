
-- View all tables
SELECT * from pg_catalog.pg_tables;


SELECT * from "auth_user" order by id desc;
SELECT * from "socialaccount_socialaccount" order by id desc;
SELECT * from "authtoken_token" where user_id = 470;
SELECT * from "LearningAPI_nssuser" where user_id = 470;
SELECT * from "LearningAPI_nssusercohort" where nss_user_id = 468;
SELECT * from "LearningAPI_studentteam";
SELECT * FROM "LearningAPI_cohort";

SELECT * FROM "LearningAPI_helprequest";

DROP FUNCTION IF EXISTS get_student_details(INT);
DROP FUNCTION IF EXISTS get_project_average_start_delay(INT);


DROP FUNCTION IF EXISTS get_cohort_student_data(INT);
SELECT * from get_cohort_student_data(29);



CREATE FUNCTION get_cohort_student_data(selected_cohort_id INT)
RETURNS TABLE (
    user_id INT,
    student_name TEXT,
    score INT,
    github_handle TEXT,
    extra_data TEXT,
    current_cohort TEXT,
    current_cohort_id INT,
    assessment_status_id INT,
    assessment_url TEXT,
    current_project_id INT,
    current_project_index INT,
    current_project_name TEXT,
    current_book_id INT,
    current_book_index INT,
    current_book_name TEXT,
    student_notes TEXT,
    student_tags TEXT,
    capstone_proposals TEXT,
    project_duration DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        nu.id::int AS user_id,
        au."first_name" || ' ' || au."last_name" AS student_name,
        COALESCE(lr.total_score, 0)::int AS score,
        nu.github_handle::text,
        social.extra_data::text,
        c.name::text AS current_cohort,
        c.id::int AS current_cohort_id,
        COALESCE(sa.status_id::int, 0) AS assessment_status_id,
        sa.url::text AS assessment_url,
        sp.project_id::int AS current_project_id,
        p.index::int AS current_project_index,
        p.name::text AS current_project_name,
        b.id::int AS current_book_id,
        b.index::int AS current_book_index,
        b.name::text AS current_book_name,
        COALESCE(
            json_agg(
                json_build_object(
                    'note_id', sn.id,
                    'note', sn.note,
                    'created_on', sn.created_on,
                    'note_type_id', sn.note_type_id,
                    'note_label', COALESCE(snt.label, '')
                )
            )
        )::text AS student_notes,
        COALESCE(
            (
            SELECT json_agg(
                json_build_object(
                    'id', st."id",
                    'tag', t."name"
                )
            )
            FROM "LearningAPI_studenttag" st
            LEFT JOIN "LearningAPI_tag" t ON t."id" = st."tag_id"
            WHERE st."student_id" = nu.id
            )
        , '[]')::text AS student_tags,
        COALESCE(
            (
                SELECT json_agg(
                    json_build_object(
                        'id', c."id",
                        'status', ps.status,
                        'current_status_id', ps.id,
                        'proposal_url', c."proposal_url",
                        'created_on', tl.date,
                        'course_name', cr.name
                    )
                )
                FROM "LearningAPI_capstone" c
                LEFT JOIN (
                    SELECT DISTINCT ON (
                        ct.capstone_id, c.course_id
                    ) *
                    FROM "LearningAPI_capstonetimeline" ct
                    JOIN "LearningAPI_capstone" c ON c.id = ct.capstone_id
                    ORDER BY
                        c.course_id,
                        ct.capstone_id,
                        date desc
                ) tl ON tl.capstone_id = c.id
                LEFT JOIN "LearningAPI_proposalstatus" ps ON ps."id" = tl.status_id
                LEFT JOIN "LearningAPI_course" cr ON c.course_id = cr.id
                WHERE c."student_id" = nu.id
            ), '[]'
        )::text AS capstone_proposals,
        CASE
            WHEN sa.id IS NOT NULL AND sa.assessment_id = la.id  THEN
                (
                    EXTRACT(YEAR FROM AGE(NOW(), sa.date_created)) * 365 +
                    EXTRACT(MONTH FROM AGE(NOW(), sa.date_created)) * 30 +
                    EXTRACT(DAY FROM AGE(NOW(), sa.date_created))
                )::double precision
            ELSE
                (
                    EXTRACT(YEAR FROM AGE(NOW(), sp.date_created)) * 365 +
                    EXTRACT(MONTH FROM AGE(NOW(), sp.date_created)) * 30 +
                    EXTRACT(DAY FROM AGE(NOW(), sp.date_created))
                )::double precision
        END AS project_duration
    FROM "LearningAPI_nssuser" nu
    JOIN "auth_user" au ON au."id" = nu."user_id"
    LEFT JOIN "LearningAPI_nssusercohort" nc ON nc."nss_user_id" = nu."id"
    LEFT JOIN "LearningAPI_cohort" c ON c."id" = nc."cohort_id"
    LEFT JOIN "LearningAPI_studentnote" sn ON sn."student_id" = nu."id"
    LEFT JOIN "LearningAPI_studentnotetype" snt ON sn."note_type_id" = snt."id"
    LEFT JOIN "LearningAPI_studenttag" stg ON stg."student_id" = nu."id"
    LEFT JOIN "LearningAPI_tag" tag ON stg.tag_id = tag.id
    LEFT JOIN "socialaccount_socialaccount" social ON social.user_id = nu.user_id
    LEFT JOIN "LearningAPI_capstone" sc ON sc.student_id = nu."id"
    LEFT JOIN "LearningAPI_studentproject" sp
        ON sp."student_id" = nu."id"
        AND sp.id = (
            SELECT id
            FROM "LearningAPI_studentproject"
            WHERE "student_id" = nu."id"
            ORDER BY id DESC
            LIMIT 1
        )
    LEFT JOIN "LearningAPI_project" p ON p."id" = sp."project_id"
    LEFT JOIN "LearningAPI_book" b ON b."id" = p."book_id"
    LEFT JOIN "LearningAPI_assessment" la
        ON b.id = la.book_id
    LEFT JOIN "LearningAPI_studentassessment" sa
        ON sa."student_id" = nu."id"
        AND sa."assessment_id" = la."id"
        AND sa."date_created" = (
            SELECT MAX("date_created")
            FROM "LearningAPI_studentassessment"
            WHERE "student_id" = nu."id"
            AND "assessment_id" = la."id"
        )
        AND sa.assessment_id = la.id
    LEFT JOIN (
        SELECT lr."student_id", SUM(lw."weight") AS total_score
        FROM "LearningAPI_learningrecord" lr
        JOIN "LearningAPI_learningweight" lw ON lw."id" = lr."weight_id"
        WHERE lr."achieved" = true
        GROUP BY lr."student_id"
    ) lr ON lr."student_id" = nu."id"
    WHERE nc."cohort_id" = selected_cohort_id
    AND au.is_active = TRUE
    AND au.is_staff = FALSE
    GROUP BY nu.id, nu.github_handle, social.extra_data, sa.url,
        student_name, current_cohort, current_cohort_id, assessment_status_id,
        current_project_id, current_project_index, current_project_name,
        project_duration, current_book_id, current_book_index, current_book_name,
        score
    ORDER BY b.index ASC,
        p.index ASC;
END;
$$ LANGUAGE plpgsql;
























SELECT
    nu.id::int AS user_id,
    au."first_name" || ' ' || au."last_name" AS student_name,
    COALESCE(lr.total_score, 0)::int AS score,
    nu.github_handle::text,
    social.extra_data::text,
    c.name::text AS current_cohort,
    c.id::int AS current_cohort_id,
    COALESCE(sa.status_id::int, 0) AS assessment_status_id,
    sa.url::text AS assessment_url,
    sp.project_id::int AS current_project_id,
    p.index::int AS current_project_index,
    p.name::text AS current_project_name,
    b.id::int AS current_book_id,
    b.index::int AS current_book_index,
    b.name::text AS current_book_name,
    COALESCE(
        json_agg(
            json_build_object(
                'note_id', sn.id,
                'note', sn.note,
                'created_on', sn.created_on,
                'note_type_id', sn.note_type_id,
                'note_label', COALESCE(snt.label, '')
            )
        )
    )::text AS student_notes,
    COALESCE(
        (
          SELECT json_agg(
              json_build_object(
                  'id', st."id",
                  'tag', t."name"
              )
           )
           FROM "LearningAPI_studenttag" st
           LEFT JOIN "LearningAPI_tag" t ON t."id" = st."tag_id"
           WHERE st."student_id" = nu.id
        )
     , '[]')::text AS student_tags,
    COALESCE(
        (
            SELECT json_agg(
                json_build_object(
                    'id', c."id",
                    'status', ps.status,
                    'current_status_id', ps.id,
                    'proposal_url', c."proposal_url",
                    'created_on', tl.date,
                    'course_name', cr.name
                )
            )
            FROM "LearningAPI_capstone" c
            LEFT JOIN (
                SELECT DISTINCT ON (
                    ct.capstone_id, c.course_id
                ) *
                FROM "LearningAPI_capstonetimeline" ct
                JOIN "LearningAPI_capstone" c ON c.id = ct.capstone_id
                ORDER BY
                    c.course_id,
                    ct.capstone_id,
                    date desc
            ) tl ON tl.capstone_id = c.id
            LEFT JOIN "LearningAPI_proposalstatus" ps ON ps."id" = tl.status_id
            LEFT JOIN "LearningAPI_course" cr ON c.course_id = cr.id
            WHERE c."student_id" = nu.id
        ), '[]'
    )::text AS capstone_proposals,

    CASE
        WHEN sa.id IS NOT NULL AND sa.assessment_id = la.id  THEN
            EXTRACT(YEAR FROM AGE(NOW(), sa.date_created)) * 365 +
            EXTRACT(MONTH FROM AGE(NOW(), sa.date_created)) * 30 +
            EXTRACT(DAY FROM AGE(NOW(), sa.date_created))::double precision
        ELSE
            EXTRACT(YEAR FROM AGE(NOW(), sp.date_created)) * 365 +
            EXTRACT(MONTH FROM AGE(NOW(), sp.date_created)) * 30 +
            EXTRACT(DAY FROM AGE(NOW(), sp.date_created))::double precision
    END AS project_duration

FROM "LearningAPI_nssuser" nu
JOIN "auth_user" au ON au."id" = nu."user_id"
LEFT JOIN "LearningAPI_nssusercohort" nc ON nc."nss_user_id" = nu."id"
LEFT JOIN "LearningAPI_cohort" c ON c."id" = nc."cohort_id"
LEFT JOIN "LearningAPI_studentnote" sn ON sn."student_id" = nu."id"
LEFT JOIN "LearningAPI_studentnotetype" snt ON sn."note_type_id" = snt."id"
LEFT JOIN "LearningAPI_studenttag" stg ON stg."student_id" = nu."id"
LEFT JOIN "LearningAPI_tag" tag ON stg.tag_id = tag.id
LEFT JOIN "socialaccount_socialaccount" social ON social.user_id = nu.user_id
LEFT JOIN "LearningAPI_capstone" sc ON sc.student_id = nu."id"
LEFT JOIN "LearningAPI_studentproject" sp
    ON sp."student_id" = nu."id"
    AND sp.id = (
        SELECT id
        FROM "LearningAPI_studentproject"
        WHERE "student_id" = nu."id"
        ORDER BY id DESC
        LIMIT 1
    )
LEFT JOIN "LearningAPI_project" p ON p."id" = sp."project_id"
LEFT JOIN "LearningAPI_book" b ON b."id" = p."book_id"
LEFT JOIN "LearningAPI_assessment" la
    ON b.id = la.book_id
LEFT JOIN "LearningAPI_studentassessment" sa
    ON sa."student_id" = nu."id"
    AND sa."assessment_id" = la."id"
    AND sa."date_created" = (
        SELECT MAX("date_created")
        FROM "LearningAPI_studentassessment"
        WHERE "student_id" = nu."id"
        AND "assessment_id" = la."id"
    )
    AND sa.assessment_id = la.id
LEFT JOIN (
    SELECT lr."student_id", SUM(lw."weight") AS total_score
    FROM "LearningAPI_learningrecord" lr
    JOIN "LearningAPI_learningweight" lw ON lw."id" = lr."weight_id"
    WHERE lr."achieved" = true
    GROUP BY lr."student_id"
) lr ON lr."student_id" = nu."id"
WHERE nc."cohort_id" = 29
AND au.is_active = TRUE
AND au.is_staff = FALSE
GROUP BY nu.id, nu.github_handle, social.extra_data, sa.url,
    student_name, current_cohort, current_cohort_id, assessment_status_id,
    current_project_id, current_project_index, current_project_name,
    project_duration, current_book_id, current_book_index, current_book_name,
    score
ORDER BY b.index ASC,
    p.index ASC;



SELECT *
    FROM "LearningAPI_learningrecordentry" lr
order by id desc;

SELECT
    sum(lw.weight) as score,
    au."first_name" || ' ' || au."last_name" AS student_name
from "LearningAPI_learningrecord" lr
join "LearningAPI_learningweight" lw on lr.weight_id = lw.id
join "LearningAPI_nssuser" nu on nu.id = lr.student_id
join "auth_user" au on au.id = nu.user_id
join "LearningAPI_nssusercohort" uc on uc.nss_user_id = nu.id
join "LearningAPI_cohort" c on uc.cohort_id = c.id
where c.id = 29
group by student_name
;





SELECT * from "LearningAPI_studentnote" order by id desc;