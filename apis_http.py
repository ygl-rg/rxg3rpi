import functools
from twisted.python import log
import rg_lib
import api_core
import api_device
import xy_lib
import g_vars


class EM:
    @classmethod
    async def ListDevice(cls, req_handler, limit_key, arg):
        """
        :param req_handler: http request
        :param arg: {token, list_no: switch or sensor or all,
                     get_vals, optional}
        :return: devices
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            return await api_device.List(arg['list_no'], arg.get('get_vals', False))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def OpenSwitch(cls, req_handler, limit_key, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceid"}}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            return await api_device.OpSwitch(para['arg']['deviceid'], True)
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def OpenMultiSwitch(cls, req_handler, limit_key, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceids"}}
        :return: devices
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            devs = []
            for devid in para['arg']['deviceids']:
                devs.append(await api_device.OpSwitch(devid, True))
            return devs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def CloseSwitch(cls, req_handler, limit_key, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceid"}}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            return await api_device.OpSwitch(para['arg']['deviceid'], False)
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def CloseMultiSwitch(cls, req_handler, limit_key, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceids"}}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            devs = []
            for devid in para['arg']['deviceids']:
                devs.append(await api_device.OpSwitch(devid, False))
            return devs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def SampleSensor(cls, req_handler, limit_key, para):
        """
        :param req_handler:
        :param limit_key:
        :param para: {deviceids, sample_count}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            return await api_device.SampleSensor(para['deviceids'], para.get('sample_count', 10))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def ReadDevice(cls, req_handler, limit_key, para):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            return await api_device.GetVal(para['deviceids'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class ZbDevice:
    @classmethod
    async def __GetDevice(cls, deviceid):
        return await api_device.Get(["""select r1.* 
                                        from rxg_zb_device r1 
                                        where r1.id=?""", (deviceid,)])

    @classmethod
    async def Remove(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, deviceids}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await api_device.Remove(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reset(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, deviceids}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await api_device.Reset(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Add(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, device}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await api_device.CheckNId(arg['device'])
            return await cls.__GetDevice(await api_device.Add(arg['device']))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Set(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, device}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            return await cls.__GetDevice(await api_device.Update(arg['device']))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Get(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            return await cls.__GetDevice(arg['deviceid'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Search(cls, req_handler, limit_key, para):
        """
        :param req_handler:
        :param sessionid:
        :param para: {"name": xxx, "val": xxx}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            return await api_device.Search(para['arg'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetOpLog(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param arg: {"token" "deviceid": deviceid, "start_ts": start timestamp, "stop_ts": stop timestamp}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler), 3)
            await api_core.Login.CheckRight(arg['token'])
            return await api_core.DeviceLog.Get(arg['start_ts'], arg['stop_ts'], arg['deviceid'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetOpErrorCount(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param arg: {token, start_ts, stop_ts}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            devs = await api_core.BizDB.Query(["select id, name, device_no from rxg_zb_device", []])
            devids = [i['id'] for i in devs]
            devs_tbl = {i['id']: i for i in devs}
            recs = await api_core.DeviceLog.GetErrorCount(arg['start_ts'], arg['stop_ts'], devids)
            for rec in recs:
                rec['device_no'] = devs_tbl[rec['deviceid']]['device_no']
                rec['device_name'] = devs_tbl[rec['deviceid']]['name']
            return recs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetNId(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param arg: {token, deviceid, moduleid}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler), 5)
            await api_core.Login.CheckRight(arg['token'])
            res = {"nid": -1, "count": 0}
            for i in range(10):
                res['count'] = i + 1
                await rg_lib.Twisted.sleep(1)
                nid = await xy_lib.Api.GetDeviceNId(arg['deviceid'], arg['moduleid'])
                if nid is not None:
                    res['nid'] = nid
                    break
            if res['nid'] > 0:
                await api_device.TryUpdateNId(arg['deviceid'], res['nid'])
            return res
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reboot(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await api_device.Reboot(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class ZbModule:
    @classmethod
    async def List(cls, req_handler, limit_key, arg):
        """
        :param req_handler:
        :param arg: {"token", list_no: "active", "backup"}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            return await api_device.Module.List(arg)
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def ProbeDevice(cls, req_handler, limit_key, para):
        """
        :param req_handler:
        :param para: {token, moduleid: }
        :return: {"devices": []}
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler), 3)
            await api_core.Login.CheckRight(para['token'])
            return await api_device.Module.ProbeDevice(para['moduleid'])
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reboot(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await xy_lib.Api.RebootModule(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reset(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await xy_lib.Api.ClearModule(arg['moduleid'])
            await xy_lib.Api.RebootModule(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Backup(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await api_device.Module.Backup(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Restore(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            flag = await api_device.Module.Restore(arg['target_moduleid'], arg['src_moduleid'])
            return 'ok' if flag else 'failed'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def RebootAll(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            await xy_lib.Api.RebootAll()
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()


class _SysCfg:
    @classmethod
    async def SetCfg(cls, req_handler, limit_key, para):
        """
        :param req_handler:
        :param sessionid:
        :param para: {token, arg: {key->val}}
        :return:
        """
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(para['token'])
            await api_core.SysCfg.Set(para['arg'])
            await rg_lib.Twisted.sleep(2)
            await api_core.PageKite.RestartBackend(g_vars.g_cfg['http_port'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetCfg(cls, req_handler, limit_key, arg):
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            return await api_core.SysCfg.Get(["select * from rxg_sys_cfg", tuple()])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def RebootSys(cls, req_handler, limit_key, arg):
        from twisted.internet import reactor
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            tp = rg_lib.ProcessProto('reboot')
            reactor.spawnProcess(tp, '/sbin/reboot', ['/sbin/reboot'], {})
            return 'ok'
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def RestartRXG(cls, req_handler, limit_key, arg):
        import os
        try:
            await api_core.ReqLimit.CheckMinuteRate(limit_key, rg_lib.Cyclone.TryGetRealIp(req_handler))
            await api_core.Login.CheckRight(arg['token'])
            rg_lib.Process.Kill(os.getpid())
            return 'ok'
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class Base(rg_lib.AsyncDynFuncHandler):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {}

    def GetFunc(self, func_name):
        return self.FUNC_TBL[func_name] if func_name in self.FUNC_TBL else None


class EnvMonitor(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {'ListDevice': functools.partial(EM.ListDevice, self, "1_1"),
                         'OpenSwitch': functools.partial(EM.OpenSwitch, self, "1_2"),
                         'OpenMultiSwitch': functools.partial(EM.OpenMultiSwitch, self, "1_3"),
                         'CloseSwitch': functools.partial(EM.CloseSwitch, self, "1_4"),
                         'CloseMultiSwitch': functools.partial(EM.CloseMultiSwitch, self, "1_5"),
                         'SampleSensor': functools.partial(EM.SampleSensor, self, "1_6"),
                         'ReadDevice': functools.partial(EM.ReadDevice, self, "1_7")}


class ZbDeviceAdm(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"AddDevice": functools.partial(ZbDevice.Add, self, "2_1"),
                         "SetDevice": functools.partial(ZbDevice.Set, self, "2_2"),
                         "GetDevice": functools.partial(ZbDevice.Get, self, "2_3"),
                         "GetDeviceNId": functools.partial(ZbDevice.GetNId, self, "2_4"),
                         'RemoveDevice': functools.partial(ZbDevice.Remove, self, "2_5"),
                         'ResetDevice': functools.partial(ZbDevice.Reset, self, "2_6"),
                         'SearchDevice': functools.partial(ZbDevice.Search, self, "2_7"),
                         'GetDeviceOpLog': functools.partial(ZbDevice.GetOpLog, self, "2_8"),
                         'GetDeviceOpErrorCount': functools.partial(ZbDevice.GetOpErrorCount, self, "2_9"),
                         'RebootDevice': functools.partial(ZbDevice.Reboot, self, "2_10")
                         }


class ZbModuleAdm(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"ListModule": functools.partial(ZbModule.List, self, "3_1"),
                         'ProbeDevice': functools.partial(ZbModule.ProbeDevice, self, "3_2"),
                         'ResetModule': functools.partial(ZbModule.Reset, self, "3_3"),
                         'BackupModule': functools.partial(ZbModule.Backup, self, "3_4"),
                         'RestoreModule': functools.partial(ZbModule.Restore, self, "3_5"),
                         'RebootModule': functools.partial(ZbModule.Reboot, self, "3_6"),
                         'RebootAll': functools.partial(ZbModule.RebootAll, self, "3_7")}


class SysCfg(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"SetCfg": functools.partial(_SysCfg.SetCfg, self, "4_1"),
                         "GetCfg": functools.partial(_SysCfg.GetCfg, self, "4_2"),
                         "RebootSys": functools.partial(_SysCfg.RebootSys, self, "4_3"),
                         "RestartRXG": functools.partial(_SysCfg.RestartRXG, self, "4_4")}

