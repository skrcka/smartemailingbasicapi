import asyncio
from dotenv import load_dotenv
import os

from SmartEmailingConnector import SmartEmailingConnector


async def main():
    load_dotenv()
    USER = os.getenv('USER')
    API_KEY = os.getenv('API_KEY')
    SOURCE_EMAIL = os.getenv('SOURCE_EMAIL')

    connector = SmartEmailingConnector(username=USER, api_key=API_KEY, source_email=SOURCE_EMAIL)
    result = await connector.check_api_status()
    print(result)
    result = await connector.check_credentials()
    print(result)
    #result = await connector.add_contact('Testname4', 'testemail4@seznam.cz')
    result = await connector.add_tag('testemail4@seznam.cz', 'xdddd222')
    print(result)

if __name__ == "__main__":
    asyncio.run(main())