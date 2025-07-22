import time
from panel.panel import Panel
from utils.marzban_api import Marzban
from db.methods import get_vpn_user
from panel.models import PanelProfile
import glv

class MarzbanPanel(Panel):
    def __init__(self):
        self.api = Marzban(glv.config['PANEL_HOST'], glv.config['PANEL_USER'], glv.config['PANEL_PASS'])
        self.api.get_token()
        self._available_inbounds = None

    async def get_available_inbounds(self):
        if self._available_inbounds is None:
            try:
                inbounds_data = await self.api.get_inbounds()
                self._available_inbounds = []
                
                for protocol, inbounds_list in inbounds_data.items():
                    if isinstance(inbounds_list, list):
                        for inbound in inbounds_list:
                            if 'tag' in inbound:
                                self._available_inbounds.append(inbound['tag'])
                                
            except Exception as e:
                self._available_inbounds = []
        return self._available_inbounds

    async def get_dynamic_protocols(self):
        available_inbounds = await self.get_available_inbounds()
        
        preferred_vless_inbounds = [
            'VLESS Reality Steal Oneself',
            'VLESS WS'
        ]
        
        existing_vless_inbounds = [
            inbound for inbound in preferred_vless_inbounds 
            if inbound in available_inbounds
        ]
        
        if not existing_vless_inbounds:
            vless_inbounds = [
                inbound for inbound in available_inbounds 
                if 'vless' in inbound.lower()
            ]
            existing_vless_inbounds = vless_inbounds[:1] if vless_inbounds else []
        
        if existing_vless_inbounds:
            return {
                "proxies": {"vless": {"flow": "xtls-rprx-vision"}},
                "inbounds": {"vless": existing_vless_inbounds}
            }
        else:
            if available_inbounds:
                return {
                    "proxies": {"vless": {"flow": "xtls-rprx-vision"}},
                    "inbounds": {"vless": available_inbounds[:1]}
                }
            else:
                raise Exception("No inbounds available in the panel")

    async def check_if_user_exists(self, username):
        try:
            await self.api.get_user(username)
            return True
        except Exception as e:
            return False

    async def get_panel_user(self, tg_id: int):
        result = await get_vpn_user(tg_id)
        res = await self.check_if_user_exists(result.vpn_id)
        if not res:
            return None
        user = await self.api.get_user(result.vpn_id)
        return PanelProfile.from_marzban_profile(user)

    async def generate_subscription(self, username: str, months: int, data_limit: int):
        res = await self.check_if_user_exists(username)
        ps = await self.get_dynamic_protocols()
        if res:
            user = await self.api.get_user(username)
            user['status'] = 'active'
            if user['expire'] < time.time():
                await self.api.user_data_limit_reset(username)
                user['expire'] = self.get_subscription_end_date(months)
            else:
                user['expire'] += self.get_subscription_end_date(months, True)
            user['data_limit'] = data_limit
            result = await self.api.modify_user(username, user)
        else:
            user = {
                'username': username,
                'proxies': ps["proxies"],
                'inbounds': ps["inbounds"],
                'expire': self.get_subscription_end_date(months),
                'data_limit': data_limit,
                'data_limit_reset_strategy': "month",
            }
            result = await self.api.add_user(user)
        return PanelProfile.from_marzban_profile(result)

    async def generate_test_subscription(self, username):
        res = await self.check_if_user_exists(username)
        ps = await self.get_dynamic_protocols()
        if res:
            user = await self.api.get_user(username)
            user['status'] = 'active'
            if user['expire'] < time.time():
                user['expire'] = self.get_test_subscription_end_date(glv.config['PERIOD_LIMIT'])
            else:
                user['expire'] += self.get_test_subscription_end_date(glv.config['PERIOD_LIMIT'], True)
            result = await self.api.modify_user(username, user)
        else:
            user = {
                'username': username,
                'proxies': ps["proxies"],
                'inbounds': ps["inbounds"],
                'expire': self.get_test_subscription_end_date(glv.config['PERIOD_LIMIT']),
                'data_limit': 107374182400,
                'data_limit_reset_strategy': "month",
            }
            result = await self.api.add_user(user)
        return PanelProfile.from_marzban_profile(result)

    async def update_subscription_data_limit(self, username: str, datalimit: int):
        user = await self.api.get_user(username)
        user['status'] = 'active'
        user['data_limit'] = user['data_limit'] + datalimit
        result = await self.api.modify_user(username, user)
        return PanelProfile.from_marzban_profile(result)

    async def reset_subscription_data_limit(self, username):
        if not await self.check_if_user_exists(username):
            return None
        result = await self.api.user_data_limit_reset(username)
        return result
