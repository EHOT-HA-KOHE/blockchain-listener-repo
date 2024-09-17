from typing import Optional


def get_portal_url_from_pair_info(pair: dict) -> Optional[str]:
    if 'info' in pair and 'socials' in pair['info']:
        for social in pair['info']['socials']:
            if social['type'] == 'telegram':
                return social['url']
