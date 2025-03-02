from io import StringIO
import io

from ipaddress import IPv4Address, AddressValueError
from django.db import transaction
from django.db.models import Subquery

from .models import Vlan, MacIP
from utils.errors import NetworkError
from compute.managers import CenterManager, GroupManager


class VlanManager:
    """
    局域子网Vlan管理器
    """
    MODEL = Vlan

    @staticmethod
    def get_vlan_by_id(vlan_id: int):
        """
        通过id获取镜像元数据模型对象
        :param vlan_id: 镜像id
        :return:
            Vlan() # success
            None    #不存在

        :raise NetworkError
        """
        if not isinstance(vlan_id, int) or vlan_id < 0:
            raise NetworkError(msg='子网ID参数有误')

        try:
            return Vlan.objects.select_related('group').filter(id=vlan_id).first()
        except Exception as e:
            raise NetworkError(msg=f'查询子网时错误,{str(e)}')

    @staticmethod
    def get_vlan_queryset():
        return Vlan.objects.filter(enable=True).all()

    def get_center_vlan_queryset(self, center):
        """
        分中心的vlan查询集

        :param center: 分中心实例，或id
        :return:
            QuerySet()
        """
        groups = CenterManager().get_group_queryset_by_center(center)
        queryset = self.get_vlan_queryset()
        return queryset.filter(group__in=Subquery(groups.values('id'))).all()

    def get_group_vlan_queryset(self, group):
        """
        宿主机组的vlan查询集

        :param group: 宿主机组实例，或id
        :return:
            QuerySet()
        """
        queryset = self.get_vlan_queryset()
        return queryset.filter(group=group).all()

    def filter_vlan_queryset(self, center: int = None, group: int = None, is_public: bool = None, user=None):
        """
        筛选vlan查询集

        :param center: 分中心id
        :param group: 宿主机组id
        :param is_public: 公网或私网
        :param user: 用户实例，用于过滤用户有权限使用的vlan
        :return:
            QuerySet()
        """
        group_set = None
        if user:
            group_set = user.group_set.all()

        if group:
            if not group_set:
                group_set = GroupManager().get_group_queryset()

            group_set = group_set.filter(id=group)
        elif center:
            if group_set:
                group_set = group_set.filter(center=center)
            else:
                group_set = CenterManager().get_group_queryset_by_center(center)

        queryset = self.get_vlan_queryset()
        if is_public is True:
            queryset = queryset.filter(tag=Vlan.NET_TAG_PUBLIC)
        elif is_public is False:
            queryset = queryset.filter(tag=Vlan.NET_TAG_PRIVATE)

        if group_set:
            queryset = queryset.filter(group__in=Subquery(group_set.values('id'))).all()

        return queryset

    @staticmethod
    def generate_subips(vlan_id, from_ip, to_ip, write_database=False):
        """
        生成子网ip
        :param vlan_id:
        :param from_ip: 开始ip
        :param to_ip: 结束ip
        :param write_database: True 生成并导入到数据库 False 生成不导入数据库
        :return:
        """
        try:
            ipv4_from = IPv4Address(from_ip)
            ipv4_to = IPv4Address(to_ip)
        except AddressValueError as e:
            raise NetworkError(msg=f'输入的ip地址无效, {e}')

        int_from = int(ipv4_from)
        int_to = int(ipv4_to)
        if int_from > int_to:
            raise NetworkError(msg='请检查输入的ip地址的范围，起始ip不能大于结束ip地址')

        l_ip_mac = []
        for ip in range(int_from, int_to + 1):
            if ip & 0xff:
                ip_obj = IPv4Address(ip)
                p = ip_obj.packed
                mac = f'C8:00:{p[0]:02X}:{p[1]:02X}:{p[2]:02X}:{p[3]:02X}'
                l_ip_mac.append((str(ip_obj), mac))

        if write_database:
            with transaction.atomic():
                for subip, submac in l_ip_mac:
                    try:
                        MacIP.objects.create(vlan_id=vlan_id, ipv4=subip, mac=submac)
                    except Exception as error:
                        raise NetworkError(msg='ip写入数据库失败，部分ip数据库中已有')

        return l_ip_mac

    @staticmethod
    def get_macips_by_vlan(vlan):
        """
        获得vlan对应的所有macip记录
        :param vlan:
        :return: 直接返回查询结果
        """
        try:
            macips = MacIP.objects.filter(vlan=vlan)
        except Exception as error:
            raise NetworkError(msg='读取macips失败。' + str(error))
        return macips

    @staticmethod
    def generate_config_file(vlan, macips):
        """
        生成DHCP配置文件
        :param vlan: vlan对象
        :param macips: 对应vlan下的所有macip组
        :return: str, StringIO()
        """
        lines = 'subnet %s netmask %s {\n' % (vlan.subnet_ip, vlan.net_mask)
        lines += '\t' + 'option routers\t%s;\n' % vlan.gateway
        lines += '\t' + 'option subnet-mask\t%s;\n' % vlan.net_mask
        lines += '\t' + 'option domain-name-servers\t%s;\n' % vlan.dns_server
        lines += '\t' + vlan.dhcp_config + '\n'
        # lines = lines + '\t' + 'option domain-name-servers\t8.8.8.8;\n'
        # lines = lines + '\t' + 'option time-offset\t-18000; # EAstern Standard Time\n'
        # lines = lines + '\t' + 'range dynamic-bootp 10.0.224.240 10.0.224.250;\n'
        # lines = lines + '\t' + 'default-lease-time 21600;\n'
        # lines = lines + '\t' + 'max-lease-time 43200;\n'
        # lines = lines + '\t' + 'next-server 159.226.50.246;   #tftp server\n'
        # lines = lines + '\t' + 'filename "/pxelinux.0";    #boot file\n'

        file_name = f'{vlan.subnet_ip}_dhcpd.conf'
        file = StringIO()
        file.write(lines)
        for macip in macips:
            line = f"\thost v_{macip.ipv4.replace('.', '_')} " \
                   f"{{hardware ethernet {macip.mac};fixed-address {macip.ipv4};}}\n"
            file.write(line)

        file.write('}')
        file.seek(io.SEEK_SET)      # 重置偏移量
        return file_name, file


class MacIPManager:
    """
    mac ip地址管理器
    """
    @staticmethod
    def get_macip_queryset():
        return MacIP.objects.all()

    def get_enable_macip_queryset(self):
        """所有开启使用的"""
        return self.get_macip_queryset().filter(enable=True).all()

    def get_enable_free_macip_queryset(self):
        """所有开启使用的未分配的"""
        return self.get_enable_macip_queryset().filter(used=False).all()

    def filter_macip_queryset(self, vlan=None, used=None):
        """
        筛选macip查询集

        :param vlan: None不参与筛选
        :param used: None不参与筛选
        :return:
            QuerySet()
        """
        queryset = self.get_enable_macip_queryset()
        if vlan is not None:
            queryset = queryset.filter(vlan=vlan).all()

        if used is not None:
            queryset = queryset.filter(used=used).all()

        return queryset

    @staticmethod
    def get_macip_by_id(macip_id: int):
        """
        通过id获取mac ip

        :param macip_id: mac ip id
        :return:
            MacIP() # success
            None    #不存在

        :raise NetworkError
        """
        if not isinstance(macip_id, int) or macip_id < 0:
            raise NetworkError(msg='MacIP ID参数有误')

        try:
            return MacIP.objects.filter(id=macip_id).first()
        except Exception as e:
            raise NetworkError(msg=f'查询MacIP时错误,{str(e)}')

    @staticmethod
    def get_macip_by_ipv4(ipv4: str):
        """
        通过ipv4获取mac ip

        :param ipv4: ip地址
        :return:
            MacIP() # success
            None    #不存在

        :raise NetworkError
        """
        if not ipv4 or not isinstance(ipv4, str):
            raise NetworkError(msg='ipv4参数有误')

        try:
            return MacIP.objects.filter(ipv4=ipv4).select_related('vlan').first()
        except Exception as e:
            raise NetworkError(msg=f'查询MacIP时错误,{str(e)}')

    @staticmethod
    def has_free_ip_in_vlan(vlan_id: int):
        """
        子网中是否有可用的IP

        :param vlan_id: 子网id
        :return:
            True: 有
            False: 没有
        """
        qs = MacIP.get_all_free_ip_in_vlan(vlan_id)
        if qs.count() > 0:
            return True

        return False

    @staticmethod
    def apply_for_free_ip(vlan_id: int = 0, ipv4: str = ''):
        """
        申请一个未使用的ip，申请成功的ip不再使用时需要通过free_used_ip()释放

        :param vlan_id: 子网id
        :param ipv4: 指定要申请的ip
        :return:
            MacIP() # 成功
            None    # 失败
        """
        if not vlan_id and not ipv4:
            return None

        with transaction.atomic():
            qs_ips = MacIP.objects.select_for_update().filter(used=False, enable=True).select_related('vlan')
            if ipv4:
                qs_ips = qs_ips.filter(ipv4=ipv4)

            if vlan_id and vlan_id > 0:
                qs_ips = qs_ips.filter(vlan=vlan_id)

            ip = qs_ips.first()
            if not ip:
                return None

            ip.used = True
            try:
                ip.save(update_fields=['used'])
            except Exception as e:
                return None

        return ip

    @staticmethod
    def free_used_ip(ip_id: int = 0, ipv4: str = ''):
        """
        释放一个使用中的ip,通过id或ip

        :param ip_id:
        :param ipv4:
        :return:
            True    # success
            False   # failed
        """
        try:
            with transaction.atomic():
                if ip_id > 0:
                    ip = MacIP.objects.select_for_update().filter(id=ip_id).first()
                elif ipv4:
                    ip = MacIP.objects.select_for_update().filter(ipv4=ipv4).first()
                else:
                    return False

                if not ip:
                    return False

                if not ip.set_free():
                    return False
            return True
        except Exception as e:
            return False
