from IPy import IP
from django_user_agents.utils import get_user_agent
from requests import get


class IpApi:
    @staticmethod
    def is_private(ip):
        ip_class = IP(ip)
        ip_type = ip_class.iptype()
        return ip_type in ['PRIVATE', 'LOOPBACK']

    @staticmethod
    def fetch_ip_info(ip, *fields):
        """
        fields
         status :  success ,	 continent :  Asia ,	 continentCode :  AS ,	 country :  Afghanistan ,
         countryCode :  AF ,	 region :  HER ,	 regionName :  Herat ,	 city :  Herat ,	 district :   ,
         zip :   ,	 lat : 34.3482,	 lon : 62.1997,	 timezone :  Asia/Kabul ,	 offset : 16200,	 currency :  AFN ,
         isp :  Stark Telecom ,	 org :   ,	 as :  AS137975 Stark Telecom ,	 asname :  STARKTELECOM-AS-AP ,
         reverse :   ,	 mobile : false,	 proxy : false,	 hosting : false,	 query :  103.119.24.122
        """
        if not fields:
            fields = '66846719'
        else:
            fields += 'status',
            fields = ','.join(fields)
        ip_data = {}
        if not IpApi.is_private(ip):
            service_url = f'http://ip-api.com/json/{ip}?fields={fields}'
            try:
                response = get(url=service_url)
                ip_data: dict = response.json()
            except Exception as e:
                pass
            else:
                ip_data.pop('status', 0)
        return ip_data


def ip_details(request):
    user_agent = get_user_agent(request)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    device_type = ""

    if user_agent.is_mobile:
        device_type = "Mobile"
    if user_agent.is_tablet:
        device_type = "Tablet"
    if user_agent.is_pc:
        device_type = "PC"

    browser_type = user_agent.browser.family
    browser_version = user_agent.browser.version_string
    os_type = user_agent.os.family
    os_version = user_agent.os.version_string

    context = {
        "ip": ip,
        "device_type": device_type,
        "browser_type": browser_type,
        "browser_version": browser_version,
        "os_type": os_type,
        "os_version": os_version,
    }
    ip_info = IpApi.fetch_ip_info(ip, 'country', 'city', 'lat', 'lon', 'proxy')
    context.update(ip_info)
    return context
