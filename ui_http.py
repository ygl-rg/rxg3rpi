# -*- coding: utf-8 -*-
from twisted.internet import defer
from twisted.python import log
from cyclone import web as cyclone_web
import rg_lib
import xy_lib
import rxg_consts
import api_core
import g_vars
import node_models


class UIBase(cyclone_web.RequestHandler):
    async def async_get(self):
        raise NotImplementedError()

    async def async_post(self):
        raise NotImplementedError()

    def get(self):
        return defer.ensureDeferred(self.async_get())

    def post(self):
        return defer.ensureDeferred(self.async_post())


class AppAdmLogin(UIBase):
    def initialize(self, **kwargs):
        self.url_tbl = {'zb_device': rxg_consts.Node_URLs.APP_ADM_ZB_DEVICE,
                        'zb_module': rxg_consts.Node_URLs.APP_ADM_ZB_MODULE,
                        'sys_cfg': rxg_consts.Node_URLs.APP_SYS_CFG}

        self.adm_types = [{'name': 'Zigbee Device|Zigbee设备', 'value': 'zb_device', "checked": 1},
                          {'name': 'Zigbee Module|Zigbee模组', 'value': 'zb_module'},
                          {'name': 'System Config|系统设置', 'value': 'sys_cfg'}]

    def RenderPage(self, user_lang, hint):
        self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_LOGIN,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title="Sys Adm",
                    hint=hint,
                    loginurl=rxg_consts.Node_URLs.APP_ADM_LOGIN,
                    bkgpng=g_vars.g_cfg['web']['login_page_bkg'],
                    user_lang=user_lang,
                    adm_types=self.adm_types)

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppAdmLogin", rg_lib.Cyclone.TryGetRealIp(self), 5)
            user_lang = self.get_cookie(rxg_consts.Cookies.USERLANG, "eng")
            self.RenderPage(user_lang, '')
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)

    async def async_post(self):
        await api_core.ReqLimit.CheckMinuteRate("AppAdmLogin", rg_lib.Cyclone.TryGetRealIp(self), 5)
        pwd = self.get_argument('pwd', '').strip()
        adm_type = self.get_argument('adm_type', 'zb_device')
        user_lang = self.get_cookie(rxg_consts.Cookies.USERLANG, "eng")
        if pwd:
            try:
                sessionid,expire_at, curr = await api_core.Login.Adm(pwd)
                self.set_cookie(rxg_consts.Cookies.TENANT, sessionid, expires=rg_lib.DateTime.ts2dt(expire_at),
                                httponly=True)
                if adm_type in self.url_tbl:
                    self.redirect(self.url_tbl[adm_type])
                else:
                    raise ValueError("adm type incorrect")
            except rg_lib.RGError as rge:
                if node_models.ErrorTypes.TypeOfPwdErr(rge):
                    self.RenderPage(user_lang, 'password error')
                elif node_models.ErrorTypes.TypeOfAccessOverLimit(rge):
                    self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
                else:
                    self.RenderPage(user_lang, 'server error')
            except Exception:
                log.err()
                self.RenderPage(user_lang, 'server error')
        else:
            await self.async_get()


class AppEm(UIBase):
    def GetTitle(self):
        return "Elastic Monitoring powered by RoundGIS Lab"

    def GetLabel(self):
        return {
            "en": {"open": "turn on", "close": "turn off", "open_duration_desc": "15-9999 seconds",
                   'goto': 'env data'},
            "zh-cn": {"open": "打开", "close": "关闭", "open_duration_desc": "15-9999秒",
                      'goto': '环境数据'}
        }

    async def handlePage_(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppEm",
                                                    rg_lib.Cyclone.TryGetRealIp(self), 3)
            ulang = self.get_cookie(rxg_consts.Cookies.USERLANG, "en")
            label_tbl = self.GetLabel()[ulang]
            self.render(rxg_consts.Node_TPL_NAMES.APP_EM,
                        app_js_dir=g_vars.g_cfg['web']['js_dir'],
                        app_css_dir=g_vars.g_cfg['web']['css_dir'],
                        app_template_dir=g_vars.g_cfg['web']['template_dir'],
                        title=self.GetTitle(),
                        user_lang=ulang,
                        open_valve_label=label_tbl['open'],
                        close_valve_label=label_tbl['close'],
                        em_sensor_url=rxg_consts.Node_URLs.APP_EM_SENSOR[1:],
                        goto_label=label_tbl['goto'])
        except rg_lib.RGError as rge:
            if node_models.ErrorTypes.TypeOfNoRight(rge):
                self.redirect(rxg_consts.Node_URLs.APP_EM_LOGIN)
            elif node_models.ErrorTypes.TypeOfAccessOverLimit(rge):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)
        except Exception:
            log.err()
            self.finish(rxg_consts.WebContent.SERVER_ERROR)

    async def async_get(self):
        await self.handlePage_()


class AppEmSensor(UIBase):
    def GetTitle(self):
        return "Elastic Sensor powered by RoundGIS Lab"

    def GetLabel(self):
        return {
            "en": {'goto': 'env ctrl', 'sample': 'sample'},
            "zh-cn": {'goto': '环境控制', 'sample': '采样'}
        }

    def GetSampleCountTbls(self):
        return [
            {"label": 10, 'value': 10},
            {"label": 20, "value": 20},
            {"label": 30, "value": 30, 'selected': True},
            {"label": 60, "value": 60},
            {"label": 120, "value": 120},
            {"label": 180, "value": 180}
        ]

    async def handlePage_(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppEmSensor", rg_lib.Cyclone.TryGetRealIp(self), 3)
            ulang = self.get_cookie(rxg_consts.Cookies.USERLANG, "en")
            label_tbl = self.GetLabel()[ulang]
            self.render(rxg_consts.Node_TPL_NAMES.APP_EM_SENSOR,
                        app_js_dir=g_vars.g_cfg['web']['js_dir'],
                        app_css_dir=g_vars.g_cfg['web']['css_dir'],
                        app_template_dir=g_vars.g_cfg['web']['template_dir'],
                        title=self.GetTitle(),
                        user_lang=ulang,
                        samaple_count_tbls=self.GetSampleCountTbls(),
                        em_url=rxg_consts.Node_URLs.APP_EM[1:],
                        goto_label=label_tbl['goto'],
                        sample_label=label_tbl['sample'])
        except rg_lib.RGError as rge:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(rge):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)
        except Exception:
            self.finish(rxg_consts.WebContent.SERVER_ERROR)

    async def async_get(self):
        await self.handlePage_()


class AppEditZbDevice(UIBase):
    def GetDeviceNoTbls(self):
        return [{'label': i, 'value': i} for i in xy_lib.DeviceNo.LIST]

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppEditZbDevice", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                edit_mode = self.get_argument("edit_mode")
                if edit_mode == "edit":
                    deviceid = self.get_argument("deviceid")
                    self.render(rxg_consts.Node_TPL_NAMES.APP_EDIT_ZB_DEVICE,
                                app_js_dir=g_vars.g_cfg['web']['js_dir'],
                                app_css_dir=g_vars.g_cfg['web']['css_dir'],
                                app_template_dir=g_vars.g_cfg['web']['template_dir'],
                                title="Edit Zigbee Device",
                                sessionid=sid, edit_mode=edit_mode, deviceid=deviceid,
                                device_no_tbls=self.GetDeviceNoTbls())
                else:
                    self.finish("incorrect edit mode")
            else:
                self.finish("please login")
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppZbDeviceAdm(UIBase):
    def GetTitle(self):
        return "Zigbee Device Adm powered by RoundGIS Lab"

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppZbDeviceAdm", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_ZB_DEVICE,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title=self.GetTitle(),
                            sessionid=sid,
                            edit_zb_dev_url=rxg_consts.Node_URLs.APP_EDIT_ZB_DEVICE[1:],
                            recap_zb_dev_url=rxg_consts.Node_URLs.APP_RECAP_ZB_DEVICE[1:],
                            op_log_url=rxg_consts.Node_URLs.APP_DEVICE_OP_LOG[1:],
                            op_error_count_url=rxg_consts.Node_URLs.APP_DEVICE_OP_ERROR_COUNT[1:],
                            zb_module_adm_url=rxg_consts.Node_URLs.APP_ADM_ZB_MODULE[1:])
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppSyncZbDevice(UIBase):
    def GetTitle(self):
        return "Sync Zigbee Device powered by RoundGIS Lab"

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppSyncZbDevice", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            moduleid = self.get_argument("moduleid")
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_SYNC_ZB_DEVICE,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title=self.GetTitle(),
                            sessionid=sid,
                            moduleid=moduleid)
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppRecapZbDevice(UIBase):
    def GetTitle(self):
        return "Recap Zigbee Device powered by RoundGIS Lab"

    def GetDeviceNoTbls(self):
        return [{'label': i, 'value': i} for i in xy_lib.DeviceNo.LIST]

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppRecapZbDevice", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_RECAP_ZB_DEVICE,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title=self.GetTitle(),
                            device_no_tbls=self.GetDeviceNoTbls(),
                            sessionid=sid)
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class EntryPoint(UIBase):
    def RenderPage(self, hint_str):
        app_opts = self.GetAppOptions()
        self.render(rxg_consts.Node_TPL_NAMES.ENTRY_POINT,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    hint=hint_str,
                    entry_point_url=self.GetEntryPointUrl(),
                    bkgpng=g_vars.g_cfg['web']['login_page_bkg'],
                    lang_options=self.GetLangOptions(), app_options=app_opts)

    def GetLangOptions(self):
        return [{"label": "ENG", "value": "en"},
                {"label": "中文", "value": "zh-cn"}]

    def GetTitle(self):
        return "Elastic Monitoring"

    def GetEntryPointUrl(self):
        return rxg_consts.Node_URLs.ENTRY

    def GetAppOptions(self):
        return [{'label': "Control/控制", "value": "ctrl"},
                {'label': "Sensor/传感器", "value": "sensor"}]

    def GotoPage(self):
        web_type = self.get_argument("web_type", "ctrl")
        if web_type == "ctrl":
            self.redirect(rxg_consts.Node_URLs.APP_EM)
        elif web_type == 'sensor':
            self.redirect(rxg_consts.Node_URLs.APP_EM_SENSOR)
        else:
            raise cyclone_web.HTTPError(404)

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate(self.GetEntryPointUrl(),
                                                    rg_lib.Cyclone.TryGetRealIp(self), 5)
            self.RenderPage("")
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppSysCfg(UIBase):
    def GetTimezoneOpts(self):
        import pytz
        asia_tzs = ['UTC']+[i for i in pytz.common_timezones if i.find('Asia') >= 0]
        return [{'label': i, 'value': i} for i in asia_tzs]

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppSysCfg", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_SYS_CFG,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            tz_options=self.GetTimezoneOpts(),
                            title="Sys Config", sessionid=sid)
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppDeviceOpLog(UIBase):
    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppDeviceOpLog", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                deviceid = self.get_argument("deviceid")
                self.render(rxg_consts.Node_TPL_NAMES.APP_DEVICE_OP_LOG,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title="Device Op Log",
                            sessionid=sid,
                            deviceid=deviceid)
            else:
                self.finish("please login")
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppDeviceOpErrorCount(UIBase):
    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppDeviceOpErrorCount", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_DEVICE_OP_ERROR_COUNT,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title="Device Op Error Count",
                            op_log_url=rxg_consts.Node_URLs.APP_DEVICE_OP_LOG[1:],
                            sessionid=sid)
            else:
                self.finish("please login")
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppZbModuleAdm(UIBase):
    def GetTitle(self):
        return "Zigbee Module Adm powered by RoundGIS Lab"

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppZbModuleAdm", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_ZB_MODULE,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title=self.GetTitle(),
                            sessionid=sid,
                            sync_zb_dev_url=rxg_consts.Node_URLs.APP_SYNC_ZB_DEVICE[1:],
                            restore_module_url=rxg_consts.Node_URLs.APP_RESTORE_ZB_MODULE[1:])
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class AppRestoreZbModule(UIBase):
    def GetTitle(self):
        return "Restore Zigbee Module powered by RoundGIS Lab"

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("AppRestoreZbModule", rg_lib.Cyclone.TryGetRealIp(self), 3)
            sid = self.get_cookie(rxg_consts.Cookies.TENANT)
            moduleid = self.get_argument("moduleid")
            if sid:
                await api_core.Login.CheckRight(sid)
                self.render(rxg_consts.Node_TPL_NAMES.APP_RESTORE_ZB_MODULE,
                            app_js_dir=g_vars.g_cfg['web']['js_dir'],
                            app_css_dir=g_vars.g_cfg['web']['css_dir'],
                            app_template_dir=g_vars.g_cfg['web']['template_dir'],
                            title=self.GetTitle(),
                            sessionid=sid,
                            target_moduleid=moduleid)
            else:
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
        except rg_lib.RGError as err:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)
            elif node_models.ErrorTypes.TypeOfNoRight(err):
                self.redirect(rxg_consts.Node_URLs.APP_ADM_LOGIN)
            else:
                self.finish(rxg_consts.WebContent.SERVER_ERROR)


class Logout(UIBase):
    async def __logout(self):
        sid = self.get_cookie(rxg_consts.Cookies.TENANT)
        if sid:
            await api_core.UserSession.Remove(sid)
        self.clear_cookie(rxg_consts.Cookies.TENANT)
        self.finish("<h2>you are now logged out</h2>")

    async def async_get(self):
        try:
            await api_core.ReqLimit.CheckMinuteRate("logout", rg_lib.Cyclone.TryGetRealIp(self), 3)
            await self.__logout()
        except rg_lib.RGError as err_obj:
            if node_models.ErrorTypes.TypeOfAccessOverLimit(err_obj):
                self.finish(rxg_consts.WebContent.ACCESS_OVER_LIMIT)

