# ===============================================================================
# CREATE OR REPLACE VIEW v_api_calls AS
# SELECT distinct
#     aa.auth_key,
#     aa.dt_creation,
#     aa.active,
#     aa.user_id,
#     ag.role as group_role,
#     ag.id as group_id,
#     rt.max_requests,
#     rt.max_entries,
#     re.dt_request::timestamp::date,
#     count(re.auth_key) over (partition by re.auth_key) AS total_requests,
#     count(re.auth_key) over (partition by re.auth_key, dt_request::timestamp::date) AS total_day_requests
#     --(SELECT COUNT(*) FROM api_request WHERE auth_key=aa.id) AS total_requests,
#     --(SELECT COUNT(*) over (partition by auth_key, dt_request::timestamp::date) FROM api_request WHERE auth_key=aa.id) AS total_requests_dt_request
# FROM
#     api_auth aa
#     INNER JOIN auth_membership am ON am.user_id = aa.user_id
#     INNER JOIN auth_group ag ON am.group_id = ag.id
#     INNER JOIN api_request_type rt ON rt.group_id = ag.id
#     LEFT JOIN api_request re ON re.auth_key = aa.id
#===============================================================================

db.define_table("v_api_calls",
                Field("auth_key", "string"),
                Field("dt_creation", "datetime"),
                Field("active", "boolean"),
                Field("user_id", db.api_auth),
                Field("group_role", "string"),
                Field("group_id", db.auth_group),
                Field("max_requests", "integer"),
                Field("max_entries", "integer"),
                Field("total_requests", "integer"),
                Field("total_day_requests", "integer"),
                Field("dt_request", "date"),
                primarykey=['user_id', 'active'],
                migrate=False)
