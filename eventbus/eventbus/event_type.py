# ping pong
PING = "ping"
PONG = "pong"

# state update, action
STATE = "state"
STATE_ACTION = "action"

# get/set state, log, config, ...
GET_STATE = "get_state"
GET_LOG = "get_log"
GET_CONFIG = "get_config"
PUT_CONFIG = "put_config"

# log message
LOG = "log"

# auth and secrets
GET_AUTH = "get_auth"
PUT_AUTH = "put_auth"

GET_SECRETS = "get_secrets"
PUT_SECRETS = "put_secrets"

GET_CERT = "get_cert"
PUT_CERT = "put_cert"

# hello
HELLO_CONNECTED = "hello_connected"
HELLO_NO_TOKEN = "hello_no_token"
HELLO_INVALID_TOKEN = "hello_invalid_token"
HELLO_ALREADY_CONNECTED = "hello_already_connected"
BYE = "bye"
BYE_TIMEOUT = "bye_timeout"

CLEAR_COUNTER = "clear_counter"

# ota
OTA = "ota"  # with params = {dst="#branches/tree_id/tree_id.branch_id", tag="v0.1.0", dry_run=True, sha}
OTA_PROGRESS = "ota_progress"
OTA_COMPLETE = "ota_complete"
OTA_FAILED = "ota_failed"
