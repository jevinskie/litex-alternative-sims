#undef NDEBUG
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <vpi_user.h>

PLI_INT32 clk_cb(struct t_cb_data *cb_data_ptr) {
    uint64_t time = ((uint64_t)cb_data_ptr->time->high << 32) | cb_data_ptr->time->low;
    printf("@ %" PRIu64 " clk: %d\n", time, cb_data_ptr->value->value.integer);
    return 0;
}

PLI_INT32 serial2tcp_register_change(struct t_cb_data *cb_data_ptr) {
    vpiHandle clk = vpi_handle_by_name("serial2tcp_loopback_tb.sys_clk", NULL);
    assert(clk);
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
}

void serial2tcp_register() {
    s_cb_data cb_data;
    s_vpi_time timerec = {vpiSuppressTime, 0, 0, 0};

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
