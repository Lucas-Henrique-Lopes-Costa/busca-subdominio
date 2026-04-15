import asyncio
import aiohttp
import re

DOMAIN = "terrasgerais.com"
TIMEOUT = aiohttp.ClientTimeout(total=3)

CRT_URL = f"https://crt.sh/?q=%25.{DOMAIN}&output=json"

async def fetch_subdomains():
    async with aiohttp.ClientSession() as session:
        async with session.get(CRT_URL, timeout=TIMEOUT) as r:
            data = await r.json()

    subs = set()
    for entry in data:
        names = entry.get("name_value", "")
        for name in names.split("\n"):
            name = name.replace("*.", "").strip()
            if name.endswith(DOMAIN):
                subs.add(name)

    return sorted(subs)

async def check_domain(session, domain):
    for scheme in ("https", "http"):
        try:
            async with session.get(f"{scheme}://{domain}", timeout=TIMEOUT):
                print(f"[ATIVO] {domain}")
                return domain
        except:
            pass
    return None

async def main():
    subdomains = await fetch_subdomains()
    print(f"🔎 Encontrados {len(subdomains)} subdomínios no crt.sh")

    active = []
    async with aiohttp.ClientSession() as session:
        tasks = [check_domain(session, d) for d in subdomains]
        results = await asyncio.gather(*tasks)

    active = [r for r in results if r]

    with open("subdominios_ativos.txt", "w") as f:
        for d in active:
            f.write(d + "\n")

    print(f"✅ Ativos: {len(active)} (salvos em subdominios_ativos.txt)")

asyncio.run(main())
