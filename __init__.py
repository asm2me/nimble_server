import esphome.codegen as cg
import esphome.config_validation as cv
from typing import Optional
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_UUID,
    PLATFORM_ESP32,
)
ESP_PLATFORMS = [PLATFORM_ESP32]

DEPENDENCIES = ['esp32']

ble_custom_ns = cg.esphome_ns.namespace('ble_custom')
BLECustomComponent = ble_custom_ns.class_('BLECustomComponent', cg.Component)

# Configuration constants
CONF_SERVICES = "services"
CONF_UUID = "uuid"
CONF_UUID128 = "uuid128"
CONF_CHARACTERISTICS = "characteristics"
CONF_PERMISSIONS = "permissions"

# Permission flags
PERMISSION_READ = "read"
PERMISSION_WRITE = "write"
PERMISSION_NOTIFY = "notify"

# NimBLE permission flags
PERMISSIONS = {
    PERMISSION_READ: 0x0001,    # BLE_GATT_CHR_F_READ
    PERMISSION_WRITE: 0x0002,   # BLE_GATT_CHR_F_WRITE
    PERMISSION_NOTIFY: 0x0004,  # BLE_GATT_CHR_F_NOTIFY
}

def validate_uuid128(value):
    if not isinstance(value, list) or len(value) != 16:
        raise cv.Invalid("UUID128 must be a list of 16 bytes")
    return [cv.hex_uint8_t(x) for x in value]

def validate_characteristic(value):
    if isinstance(value, dict):
        if CONF_UUID in value and CONF_UUID128 in value:
            raise cv.Invalid("Cannot specify both uuid and uuid128")
        if CONF_UUID in value:
            return cv.Schema({
                cv.Required(CONF_UUID): cv.hex_uint16_t,
                cv.Required(CONF_PERMISSIONS): cv.ensure_list(cv.one_of(*PERMISSIONS, lower=True)),
            })(value)
        elif CONF_UUID128 in value:
            return cv.Schema({
                cv.Required(CONF_UUID128): validate_uuid128,
                cv.Required(CONF_PERMISSIONS): cv.ensure_list(cv.one_of(*PERMISSIONS, lower=True)),
            })(value)
        else:
            raise cv.Invalid("Must specify either uuid or uuid128")
    raise cv.Invalid("Expected characteristic to be dictionary")

def validate_service(value):
    if isinstance(value, dict):
        if CONF_UUID in value and CONF_UUID128 in value:
            raise cv.Invalid("Cannot specify both uuid and uuid128")
        if CONF_UUID in value:
            return cv.Schema({
                cv.Required(CONF_UUID): cv.hex_uint16_t,
                cv.Required(CONF_CHARACTERISTICS): cv.ensure_list(validate_characteristic),
            })(value)
        elif CONF_UUID128 in value:
            return cv.Schema({
                cv.Required(CONF_UUID128): validate_uuid128,
                cv.Required(CONF_CHARACTERISTICS): cv.ensure_list(validate_characteristic),
            })(value)
        else:
            raise cv.Invalid("Must specify either uuid or uuid128")
    raise cv.Invalid("Expected service to be dictionary")

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(BLECustomComponent),
    cv.Required(CONF_SERVICES): cv.ensure_list(validate_service),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    for service in config[CONF_SERVICES]:
        if CONF_UUID in service:
            # Handle 16-bit UUID service
            characteristics = []
            for char in service[CONF_CHARACTERISTICS]:
                flags = 0
                for permission in char[CONF_PERMISSIONS]:
                    flags |= PERMISSIONS[permission]
                characteristics.append((char[CONF_UUID], flags))

            # Create vector of pairs using ArrayInitializer
            chars_array = cg.ArrayInitializer(
                *(cg.ArrayInitializer(uuid, flags) for uuid, flags in characteristics)
            )

#            cg.add(var.add_service(cg.uint16(service[CONF_UUID]), chars_array))
        else:
            # Handle 128-bit UUID service
            service_uuid_arr = cg.ArrayInitializer(
                *(cg.uint8(x) for x in service[CONF_UUID128])
            )

            chars_array = []
            for char in service[CONF_CHARACTERISTICS]:
                flags = 0
                for permission in char[CONF_PERMISSIONS]:
                    flags |= PERMISSIONS[permission]

                char_uuid_arr = cg.ArrayInitializer(
                    *(cg.uint8(x) for x in char[CONF_UUID128])
                )
                chars_array.append(cg.ArrayInitializer(char_uuid_arr, flags))

            chars_initializer = cg.ArrayInitializer(*chars_array)
#            cg.add(var.add_service_128(service_uuid_arr, chars_initializer))