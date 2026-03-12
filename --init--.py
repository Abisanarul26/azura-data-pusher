from homeassistant.helpers.event import async_track_state_change
from azure.iot.device import IoTHubDeviceClient

DOMAIN = "azure_power_pusher"

async def async_setup(hass, config):
    # Retrieve Azure credentials from your configuration.yaml
    conf = config.get(DOMAIN)
    connection_string = conf.get("connection_string")
    tasmota_entity = conf.get("entity_id")

    # Initialize Azure Client
    azure_client = IoTHubDeviceClient.create_from_connection_string(connection_string)

    async def send_to_azure(entity_id, old_state, new_state):
        if new_state is None or new_state.state in ["unknown", "unavailable"]:
            return
        
        # Prepare the payload
        payload = {
            "entity": entity_id,
            "power": new_state.state,
            "unit": new_state.attributes.get("unit_of_measurement")
        }
        
        # Push to Cloud (Note: in production, use a non-blocking thread)
        azure_client.send_message(str(payload))

    # Start tracking the Tasmota entity
    async_track_state_change(hass, tasmota_entity, send_to_azure)
    
    return True
