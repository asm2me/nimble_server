#pragma once

#include "esphome/core/component.h"
//#include "esphome/core/log.h"
#include <vector>
#include "host/ble_gap.h"

namespace esphome {
namespace ble_custom {

#define MYNEWT_VAL_BLE_STORE_MAX_CSFCS (8)
static void bleprph_advertise(void);
static void bleprph_on_reset(int);
static void ble_app_set_addr(void);
static void bleprph_print_conn_desc(struct ble_gap_conn_desc *desc);
void bleprph_host_task(void *param);

class BLECustomComponent : public Component {
public:
    BLECustomComponent() = default;
    virtual ~BLECustomComponent() = default;

    void setup() override;
    void loop() override;

private:
    void start_advertising_();
    static BLECustomComponent* instance_;

};

}  // namespace ble_custom
}  // namespace esphome