
SELECT *
FROM public."LearningAPI_cohort";


SELECT *
FROM public."LearningAPI_opportunity";


SELECT *
FROM public."LearningAPI_learningrecord";


SELECT *
FROM public."socialaccount_socialaccount";


SELECT *
FROM public."auth_user"
ORDER BY id DESC;


SELECT *
FROM public."LearningAPI_studentassessment";


SELECT *
FROM public."authtoken_token";


DELETE
FROM public."LearningAPI_cohortcourse";


SELECT *
FROM public."LearningAPI_course";


SELECT *
FROM public."LearningAPI_studenttag";


DELETE
FROM public."LearningAPI_studenttag";


SELECT *
FROM public."LearningAPI_cohort";


SELECT *
FROM public."LearningAPI_cohortcourse";


insert into public."LearningAPI_cohortcourse" (cohort_id,
                                               course_id,
                                               active)
values (3,
        1,
        FALSE);


insert into public."LearningAPI_cohortcourse" (cohort_id,
                                               course_id,
                                               active)
values (3,
        3,
        TRUE);


select *
from pg_catalog.pg_tables;


SELECT *
FROM public."LearningAPI_studentpersonality";


DELETE
FROM public."LearningAPI_cohort"
where id = 12;


DELETE
FROM public."LearningAPI_cohortcourse";


UPDATE public."LearningAPI_nssuser"
SET slack_handle = 'G08NYBJSY' ;


UPDATE public."LearningAPI_studentpersonality"
SET briggs_myers_type = 'ESTJ'
WHERE student_id = 56;


INSERT INTO public."LearningAPI_studentpersonality" (student_id,
                                                     briggs_myers_type,
                                                     bfi_extraversion,
                                                     bfi_agreeableness,
                                                     bfi_conscientiousness,
                                                     bfi_neuroticism,
                                                     bfi_openness)
VALUES (56,
        'ENTJ-A',
        69,
        96,
        73,
        0,
        94);


SELECT *
FROM public."LearningAPI_capstone";


SELECT *
FROM public."LearningAPI_proposalstatus";


INSERT INTO public."LearningAPI_capstonetimeline" (capstone_id,
                                                   status_id, date)
VALUES (3,
        1,
        '2022-11-04');


INSERT INTO public."LearningAPI_capstone" (proposal_url,
                                           repo_url,
                                           course_id,
                                           student_id,
                                           description)
VALUES ('http://www.claire.com',
        'http://www.claire.com',
        3,
        56,
        'Client side capstone proposal');


SELECT "LearningAPI_cohort"."id",
       "LearningAPI_cohort"."name",
       "LearningAPI_cohort"."slack_channel",
       "LearningAPI_cohort"."start_date",
       "LearningAPI_cohort"."end_date",
       "LearningAPI_cohort"."break_start_date",
       "LearningAPI_cohort"."break_end_date",
       COUNT("LearningAPI_nssusercohort"."id") FILTER (
                                                       WHERE NOT "auth_user"."is_staff" ) AS "students",
       COUNT("LearningAPI_nssusercohort"."id") FILTER (
                                                       WHERE "auth_user"."is_staff" ) AS "instructors"
FROM "LearningAPI_cohort"
LEFT OUTER JOIN "LearningAPI_nssusercohort" ON ("LearningAPI_cohort"."id" = "LearningAPI_nssusercohort"."cohort_id")
LEFT OUTER JOIN "LearningAPI_nssuser" ON ("LearningAPI_nssusercohort"."nss_user_id" = "LearningAPI_nssuser"."id")
LEFT OUTER JOIN "auth_user" ON ("LearningAPI_nssuser"."user_id" = "auth_user"."id")
GROUP BY "LearningAPI_cohort"."id" ;


SELECT "LearningAPI_capstone"."id",
       "LearningAPI_capstone"."student_id",
       "LearningAPI_capstone"."course_id",
       "LearningAPI_capstone"."proposal_url",
       "LearningAPI_capstone"."repo_url",
       "LearningAPI_capstone"."description",
       COUNT("LearningAPI_capstonetimeline"."id") AS "status_count",
       COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                          WHERE "LearningAPI_proposalstatus"."status" = Approved) AS "approved"
FROM "LearningAPI_capstone"
LEFT OUTER JOIN "LearningAPI_capstonetimeline" ON ("LearningAPI_capstone"."id" = "LearningAPI_capstonetimeline"."capstone_id")
LEFT OUTER JOIN "LearningAPI_proposalstatus" ON ("LearningAPI_capstonetimeline"."status_id" = "LearningAPI_proposalstatus"."id")
WHERE "LearningAPI_capstone"."student_id" = 74
GROUP BY "LearningAPI_capstone"."id" ;


select w.id,
       w.label,
       w.weight,
       w.tier,
       r.achieved,
       r.student_id
from public."LearningAPI_learningweight" w
left outer join public."LearningAPI_learningrecord" r on r.weight_id = w.id
and r.student_id = 19
where r.achieved is NULL
order by w.tier;


SELECT "LearningAPI_book"."id",
       "LearningAPI_book"."name",
       "LearningAPI_book"."course_id",
       "LearningAPI_book"."description",
       "LearningAPI_book"."index"
FROM "LearningAPI_book"
ORDER BY "LearningAPI_book"."course_id" ASC,
         "LearningAPI_book"."index" ASC ;


SELECT COUNT("LearningAPI_capstonetimeline"."id") AS "status_count",
       COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                          WHERE "LearningAPI_proposalstatus"."status" = 'Approved') AS approved,
       COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                          WHERE "LearningAPI_proposalstatus"."status" = 'MVP') AS mvp,
       CASE
           WHEN COUNT("LearningAPI_capstonetimeline"."id") = 0 THEN 'submitted'
           WHEN (COUNT("LearningAPI_capstonetimeline"."id") > 0
                 AND COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                                        WHERE ("LearningAPI_proposalstatus"."status" = 'MVP')) = 1) THEN 'mvp'
           WHEN (COUNT("LearningAPI_capstonetimeline"."id") > 0
                 AND COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                                        WHERE ("LearningAPI_proposalstatus"."status" = 'Approved')) = 0) THEN 'reviewed'
           WHEN (COUNT("LearningAPI_capstonetimeline"."id") > 0
                 AND COUNT("LearningAPI_capstonetimeline"."id") FILTER (
                                                                        WHERE ("LearningAPI_proposalstatus"."status" = 'Approved')) = 1) THEN 'approved'
           ELSE 'unsubmitted'
       END AS current_status
FROM "LearningAPI_capstone"
LEFT OUTER JOIN "LearningAPI_capstonetimeline" ON ("LearningAPI_capstone"."id" = "LearningAPI_capstonetimeline"."capstone_id")
LEFT OUTER JOIN "LearningAPI_proposalstatus" ON ("LearningAPI_capstonetimeline"."status_id" = "LearningAPI_proposalstatus"."id")
WHERE "LearningAPI_capstone"."student_id" = 291
GROUP BY "LearningAPI_capstone"."id" ;


SELECT *
FROM get_project_average_start_delay(1);


select *
from "LearningAPI_course";


SELECT book.name AS "BookName",
       book.index AS "BookIndex",
       project.name AS "ProjectName",
       project.index AS "ProjectIndex",
       AVG(student_project.date_created - cohort.start_date) AS "AverageStartDelay"
FROM "LearningAPI_studentproject" AS student_project
INNER JOIN "LearningAPI_project" AS project ON student_project.project_id = project.id
INNER JOIN "LearningAPI_book" AS book ON project.book_id = book.id
INNER JOIN "LearningAPI_nssusercohort" AS nssusercohort ON student_project.student_id = nssusercohort.nss_user_id
INNER JOIN "LearningAPI_cohort" AS cohort ON nssusercohort.cohort_id = cohort.id
INNER JOIN "LearningAPI_course" AS course ON book.course_id = course.id
WHERE course.id = 3
GROUP BY book.index,
         book.name,
         project.index,
         project.name
ORDER BY book.index,
         project.index ;






































DROP FUNCTION IF EXISTS get_cohort_student_data(INT);
select * from get_cohort_student_data(11);



CREATE FUNCTION get_cohort_student_data(selected_cohort_id INT)
RETURNS TABLE (
    user_id INT,
    github_handle TEXT,
    name TEXT,
    assessment_status_id INT,
    project_id INT,
    project_index INT,
    project_name TEXT,
    book_id INT,
    book_index INT,
    book_name TEXT,
    score INT
) AS $$
BEGIN
    RETURN QUERY
SELECT
        nu.user_id::int,
        nu.github_handle::text,
        au."first_name" || ' ' || au."last_name" AS name,
        sa.status_id::int AS assessment_status_id,
        sp.project_id::int AS project_id,
        p.index::int AS project_index,
        p.name::text AS project_name,
        b.id::int AS book_id,
        b.index::int AS book_index,
        b.name::text AS book_name,
        lr.total_score::int AS score
    FROM "LearningAPI_nssuser" nu
    JOIN "auth_user" au ON au."id" = nu."user_id"
    JOIN "LearningAPI_nssusercohort" nc ON nc."nss_user_id" = nu."id"
    JOIN "LearningAPI_cohort" c ON c."id" = nc."cohort_id"
    LEFT JOIN "LearningAPI_studentproject" sp
        ON sp."student_id" = nu."id"
        AND sp."date_created" = (
            SELECT MAX("date_created")
            FROM "LearningAPI_studentproject"
            WHERE "student_id" = nu."id"
        )
    LEFT JOIN "LearningAPI_project" p ON p."id" = sp."project_id"
    LEFT JOIN "LearningAPI_book" b ON b."id" = p."book_id"
    LEFT JOIN "LearningAPI_assessment" la
        ON b.id = la.book_id
    LEFT JOIN "LearningAPI_studentassessment" sa
        ON sa."student_id" = nu."id"
        AND sa."date_created" = (
            SELECT MAX("date_created")
            FROM "LearningAPI_studentassessment"
            WHERE "student_id" = nu."id"
        )
        AND sa.assessment_id = la.id
    LEFT JOIN (
        SELECT lr."student_id", SUM(lw."weight") AS total_score
        FROM "LearningAPI_learningrecord" lr
        JOIN "LearningAPI_learningrecordentry" lre ON lre."record_id" = lr."id"
        JOIN "LearningAPI_learningweight" lw ON lw."id" = lr."weight_id"
        WHERE lr."achieved" = true
        GROUP BY lr."student_id"
    ) lr ON lr."student_id" = nu."id"
    WHERE nc."cohort_id" = selected_cohort_id
    ORDER BY b.index ASC,
        p.index ASC;
END;
$$ LANGUAGE plpgsql;


