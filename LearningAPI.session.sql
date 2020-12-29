SELECT * FROM public."LearningAPI_cohort"
;
SELECT * FROM public."LearningAPI_nssuser"
;

INSERT INTO public."LearningAPI_nssusercohort" (cohort_id, nss_user_id)
VALUES (
    1,
    1
  );