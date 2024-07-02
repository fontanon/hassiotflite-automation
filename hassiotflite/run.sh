#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start toldo-terraza service
# ==============================================================================

bashio::log.info "Starting Todo Terraza..."

exec TF_LABELS=con,sin TF_LABEL_INVOKE=con MODEL_FILE=/addon_configs/model.tflite WATCHDIR=/config/camterraza WEBHOOKURL=http://192.168.0.58:8123/api/webhook/-zOxVfLI6XOYf6sAL2HZ0pd9Z python3 hassiotflite.py