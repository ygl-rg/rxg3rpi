# -*- coding: utf-8 -*-


class Timeout:
    COOKIE_INTERVAL = 3600*2


class DbConsts:
    SEARCH_LIMIT = 256


class Cookies:
    TENANT = "nbgis1_"
    USERLANG = "nbgislang_"


class Node_URLs:
    APP_LOGOUT = r"logout"
    APP_ADM_LOGIN = r"adm/login"
    APP_EM_LOGIN = r"login"
    APP_EM = r"em"
    APP_EM_SENSOR = r"em/sensor"
    APP_EDIT_ZB_DEVICE = r"edit/zbdevice"
    APP_ADM_ZB_DEVICE = r"adm/zbdevice"
    APP_SYNC_ZB_DEVICE = r'adm/synczbdevice'
    APP_DEVICE_OP_LOG = r'log/zbdevice/op'
    APP_DEVICE_OP_ERROR_COUNT = r'log/zbdevice/op/errorcount'
    APP_SYS_CFG = r'cfg/sys'
    APP_RECAP_ZB_DEVICE = r'adm/recapdevice'
    APP_ADM_ZB_MODULE = r"adm/zbmodule"
    APP_RESTORE_ZB_MODULE = r"adm/restorezbmodule"
    API_EM = r"api/em"
    API_ZB_DEVICE_ADM = r'api/zbdeviceadm'
    API_SYS_CFG = r'api/syscfg'
    API_ZB_MODULE_ADM = r'api/zbmoduleadm'
    ENTRY = r'entry'


class Node_TPL_NAMES:
    APP_LOGIN = r"app_login_tpl.html"
    APP_ADM_LOGIN = r"app_adm_login_tpl.html"
    APP_EM = r"app_em_tpl.html"
    APP_EM_SENSOR = r"app_em_sensor_tpl.html"
    APP_EDIT_ZB_DEVICE = r'app_edit_zb_device_tpl.html'
    APP_ADM_ZB_DEVICE = r'app_adm_zb_device_tpl.html'
    APP_SYNC_ZB_DEVICE = r'app_sync_zb_device_tpl.html'
    APP_SYS_CFG = r'app_sys_cfg_tpl.html'
    APP_DEVICE_OP_LOG = r'app_device_op_log_tpl.html'
    APP_DEVICE_OP_ERROR_COUNT = r'app_device_op_error_count_tpl.html'
    APP_RECAP_ZB_DEVICE = r'app_recap_zb_device_tpl.html'
    APP_ADM_ZB_MODULE = r'app_adm_zb_module_tpl.html'
    APP_RESTORE_ZB_MODULE = r'app_restore_zb_module_tpl.html'
    ENTRY_POINT = r'entry_point_tpl.html'


class Keys:
    MINUTE_RATE_FORMAT = "access_minute_rate:{0}_{1}_{2}" #prefix,key &ip
    USER_SESSION = 'user_session:{0}'


class WebContent:
    ACCESS_OVER_LIMIT = "<h2>access over limit</h2>"
    SERVER_ERROR = "<h2>server error</h2>"

