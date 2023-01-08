

SELECT *
FROM public."LearningAPI_cohort";


SELECT *
FROM public."LearningAPI_opportunity";


SELECT *
FROM public."LearningAPI_learningrecord";


SELECT *
FROM public."socialaccount_socialaccount";


SELECT *
FROM public."auth_user";


SELECT *
FROM public."LearningAPI_studentassessment";


SELECT *
FROM public."authtoken_token";

DELETE FROM public."LearningAPI_cohortcourse";

SELECT *
FROM public."LearningAPI_course";

SELECT *
FROM public."LearningAPI_studenttag";

DELETE FROM public."LearningAPI_studenttag";

SELECT *
FROM public."LearningAPI_cohort";

SELECT *
FROM public."LearningAPI_cohortcourse";


insert into public."LearningAPI_cohortcourse"
 (cohort_id, course_id, active)
values (3, 1, FALSE);

insert into public."LearningAPI_cohortcourse"
 (cohort_id, course_id, active)
values (3, 3, TRUE);

select *
from pg_catalog.pg_tables;


SELECT *
FROM public."LearningAPI_studentpersonality";

DELETE FROM public."LearningAPI_cohort" where id = 12;
DELETE FROM public."LearningAPI_cohortcourse";


UPDATE public."LearningAPI_nssuser"
SET slack_handle = 'G08NYBJSY'
;


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
       COUNT("LearningAPI_nssusercohort"."id")
            FILTER ( WHERE NOT "auth_user"."is_staff" ) AS "students",
       COUNT("LearningAPI_nssusercohort"."id")
            FILTER ( WHERE "auth_user"."is_staff" ) AS "instructors"
FROM "LearningAPI_cohort"
LEFT OUTER JOIN "LearningAPI_nssusercohort" ON ("LearningAPI_cohort"."id" = "LearningAPI_nssusercohort"."cohort_id")
LEFT OUTER JOIN "LearningAPI_nssuser" ON ("LearningAPI_nssusercohort"."nss_user_id" = "LearningAPI_nssuser"."id")
LEFT OUTER JOIN "auth_user" ON ("LearningAPI_nssuser"."user_id" = "auth_user"."id")
GROUP BY "LearningAPI_cohort"."id"
;


SELECT "LearningAPI_capstone"."id",
       "LearningAPI_capstone"."student_id",
       "LearningAPI_capstone"."course_id",
       "LearningAPI_capstone"."proposal_url",
       "LearningAPI_capstone"."repo_url",
       "LearningAPI_capstone"."description",
       COUNT("LearningAPI_capstonetimeline"."id") AS "status_count",
       COUNT("LearningAPI_capstonetimeline"."id")
            FILTER ( WHERE "LearningAPI_proposalstatus"."status" = Approved) AS "approved"
FROM "LearningAPI_capstone"
LEFT OUTER JOIN "LearningAPI_capstonetimeline" ON ("LearningAPI_capstone"."id" = "LearningAPI_capstonetimeline"."capstone_id")
LEFT OUTER JOIN "LearningAPI_proposalstatus" ON ("LearningAPI_capstonetimeline"."status_id" = "LearningAPI_proposalstatus"."id")
WHERE "LearningAPI_capstone"."student_id" = 74
GROUP BY "LearningAPI_capstone"."id"
;

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

