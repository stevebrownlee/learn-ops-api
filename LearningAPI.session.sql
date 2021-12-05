SELECT *
FROM public."LearningAPI_cohort";

SELECT *
FROM public."LearningAPI_opportunity";

SELECT *
FROM public."LearningAPI_nssuser";

SELECT *
FROM public."LearningAPI_learningrecord";

SELECT *
FROM public."LearningAPI_learningrecordweight";

SELECT *
FROM public."socialaccount_socialaccount";

SELECT *
FROM public."auth_user";

select * from pg_catalog.pg_tables;

SELECT *
FROM public."LearningAPI_nssusercohort";

INSERT INTO public."LearningAPI_nssusercohort" (cohort_id, nss_user_id)
VALUES (1, 6);


DELETE from public."LearningAPI_nssusercohort"
where id = 2;


INSERT INTO public."LearningAPI_course" (name)
VALUES ('JavaScript and React');

INSERT INTO public."LearningAPI_book" (name, course_id)
VALUES ('Bangazon', 1);








































SELECT "LearningAPI_cohort"."id",
    "LearningAPI_cohort"."name",
    "LearningAPI_cohort"."slack_channel",
    "LearningAPI_cohort"."start_date",
    "LearningAPI_cohort"."end_date",
    "LearningAPI_cohort"."break_start_date",
    "LearningAPI_cohort"."break_end_date",
    COUNT("LearningAPI_nssusercohort"."id") FILTER (
        WHERE NOT "auth_user"."is_staff"
    ) AS "students",
    COUNT("LearningAPI_nssusercohort"."id") FILTER (
        WHERE "auth_user"."is_staff"
    ) AS "instructors"
FROM "LearningAPI_cohort"
    LEFT OUTER JOIN "LearningAPI_nssusercohort" ON (
        "LearningAPI_cohort"."id" = "LearningAPI_nssusercohort"."cohort_id"
    )
    LEFT OUTER JOIN "LearningAPI_nssuser" ON (
        "LearningAPI_nssusercohort"."nss_user_id" = "LearningAPI_nssuser"."id"
    )
    LEFT OUTER JOIN "auth_user" ON (
        "LearningAPI_nssuser"."user_id" = "auth_user"."id"
    )
GROUP BY "LearningAPI_cohort"."id"
;