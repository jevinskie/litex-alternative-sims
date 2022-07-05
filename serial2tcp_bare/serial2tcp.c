#undef NDEBUG
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <vpi_user.h>

static vpiHandle sink_data;
static s_vpi_value sink_data_val;
static s_vpi_time timerec3;
static s_cb_data cb_data3;

static PLI_INT32 clk_cb(struct t_cb_data *cb_data_ptr) {
    uint64_t time = ((uint64_t)cb_data_ptr->time->high << 32) | cb_data_ptr->time->low;
    printf("@ %" PRIu64 " clk: %d\n", time, cb_data_ptr->value->value.integer);

    s_vpi_value sink_data_val_local = {.format = vpiIntVal};
    vpi_get_value(sink_data, &sink_data_val_local);
    printf("sink_data: 0x%02x\n", sink_data_val_local.value.integer);
    printf("sink_data static: 0x%02x\n", sink_data_val.value.integer);
    return 0;
}

static PLI_INT32 sink_data_cb(struct t_cb_data *cb_data_ptr) {
    uint64_t time = ((uint64_t)cb_data_ptr->time->high << 32) | cb_data_ptr->time->low;

    sink_data_val.value.integer = cb_data_ptr->value->value.integer;
    printf("@ %" PRIu64 " cb: 0x%02x\n", time, sink_data_val.value.integer);
    return 0;
}

static int sim_time_cb(struct t_cb_data *cb_data_ptr) {
    printf("!!: %p %p\n", &cb_data3, cb_data_ptr);
    printf("b: %p %p\n", cb_data3.time, cb_data_ptr->time);
    uint64_t time = ((uint64_t)cb_data_ptr->time->high << 32) | cb_data_ptr->time->low;
    printf("@@@@@ %" PRIu64 "\n", time);
    // __asm__ volatile("int $0x03");
    vpiHandle hdl;
    memset(&timerec3, 0, sizeof(timerec3));
    memset(&cb_data3, 0, sizeof(cb_data3));
    timerec3.type   = vpiSimTime;
    cb_data3.time   = &timerec3;
    cb_data3.reason = cbNextSimTime;
    cb_data3.cb_rtn = sim_time_cb;
    assert((hdl = vpi_register_cb(&cb_data3)) && vpi_free_object(hdl));
    return 0;
}

PLI_INT32 serial2tcp_register_change(struct t_cb_data *cb_data_ptr) {
    vpiHandle hdl;
    vpiHandle clk = vpi_handle_by_name("serial2tcp_loopback_tb.sys_clk", NULL);
    assert(clk);
    sink_data = vpi_handle_by_name("serial2tcp_loopback_tb.serial2tcp_sink_data", NULL);
    assert(sink_data);

    // s_vpi_time timerec3 = {vpiSimTime, 0, 0, 0};
    timerec3.type   = vpiSimTime;
    cb_data3.time   = &timerec3;
    cb_data3.reason = cbNextSimTime;
    cb_data3.cb_rtn = sim_time_cb;
    printf("!: %p\n", &cb_data3);
    printf("a: %p\n", cb_data3.time);
    assert((hdl = vpi_register_cb(&cb_data3)) && vpi_free_object(hdl));

    s_vpi_time timerec = {vpiSimTime, 0, 0, 0};
    s_vpi_value valrec = {vpiIntVal, {.integer = 42}};
    s_cb_data cb_data  = {0};
    cb_data.reason     = cbValueChange;
    cb_data.cb_rtn     = clk_cb;
    cb_data.obj        = clk;
    cb_data.time       = &timerec;
    cb_data.value      = &valrec;
    cb_data.user_data  = (void *)clk;
    assert(vpi_register_cb(&cb_data));

    s_vpi_time timerec2  = {vpiSimTime, 0, 0, 0};
    sink_data_val.format = vpiIntVal;
    s_cb_data cb_data2   = {0};
    cb_data2.reason      = cbValueChange;
    cb_data2.cb_rtn      = sink_data_cb;
    cb_data2.obj         = sink_data;
    cb_data2.time        = &timerec2;
    cb_data2.value       = &sink_data_val;
    cb_data2.user_data   = NULL;
    assert(vpi_register_cb(&cb_data2));

    return 0;
}

void serial2tcp_register() {
    s_cb_data cb_data;
    s_vpi_time timerec = {vpiSuppressTime, 0, 0, 0};
    printf("%s\n", __FUNCTION__);

    cb_data.time      = &timerec;
    cb_data.value     = 0;
    cb_data.user_data = 0;
    cb_data.obj       = 0;
    cb_data.reason    = cbEndOfCompile;
    cb_data.cb_rtn    = serial2tcp_register_change;

    vpi_register_cb(&cb_data);
}

void (*vlog_startup_routines[])() = {
    serial2tcp_register,
    NULL,
};
